import arrow
import time
import requests
import amazonmws as mws
import mwskeys, pakeys

from itertools import chain
from fuzzywuzzy import fuzz
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QTimer, QUrl, QCoreApplication, QEventLoop
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply

from responseparser import ListMatchingProductsParser, ErrorResponseParser, GetLowestOfferListingsForASINParser
from responseparser import GetMyFeesEstimateParser, GetCompetitivePricingForASINParser, ItemLookupParser
from responseparser import ParseError

from database import *
from sqlalchemy.event import listen


def remove_symbols(string, repl=''):
    return re.sub(r'[^a-zA-Z0-9\s]', repl, string)


def brand_match(listing1, listing2):
    fits = list()
    brand1 = remove_symbols(listing1.brand or '').lower()
    brand2 = remove_symbols(listing2.brand or '').lower()
    title1 = remove_symbols(listing1.title or '').lower()
    title2 = remove_symbols(listing2.title or '').lower()

    fits.append(fuzz.partial_ratio(brand1, brand2))
    fits.append(fuzz.partial_ratio(brand1, title2))
    fits.append(fuzz.partial_ratio(brand2, title1))
    return max(fits)


def model_match(listing1, listing2):
    fits = list()
    model1 = remove_symbols(listing1.model or '').lower()
    model2 = remove_symbols(listing2.model or '').lower()
    title1 = remove_symbols(listing1.title or '').lower()
    title2 = remove_symbols(listing2.title or '').lower()

    if model1.isdigit() and model2.isdigit():
        fits.append(100 * (model1 in model2 or model2 in model1))
    else:
        fits.append(fuzz.token_set_ratio(model1, model2))

    fits.append(fuzz.token_set_ratio(model1, title2))
    fits.append(fuzz.token_set_ratio(model2, title1))
    return max(fits)


def title_match(listing1, listing2):
    title1 = str(listing1.title or '').lower()
    title2 = str(listing2.title or '').lower()
    return fuzz.token_set_ratio(title1, title2)


class OperationsManager(QObject):

    __instance__ = None
    @classmethod
    def get_instance(cls, parent=None):
        if cls.__instance__ is None:
            cls.__instance__ = OperationsManager(parent=parent)
        return cls.__instance__

    supported_ops = ['TestMargins', 'FindAmazonMatches', 'GetMyFeesEstimate', 'UpdateAmazonListing', 'SearchAmazon']

    operation_complete = pyqtSignal(int)
    status_message = pyqtSignal(str)

    def __init__(self, parent=None):
        super(OperationsManager, self).__init__(parent=parent)
        self.dbsession = Session()
        self.network_manager = QNetworkAccessManager(self)
        self.scheduled = {}
        self.processing = False
        self.running = True
        self._callbacks = {}

        listen(self.dbsession, 'before_commit', self._before_commit_listener)

        # Set up the Amazon api's and throttling managers
        self.mwsapi = mws.Throttler(mws.Products(mwskeys.accesskey, mwskeys.secretkey, mwskeys.sellerid),
                                    limits=mws.PRODUCTS_LIMITS,
                                    blocking=True)
        self.paapi = mws.Throttler(mws.ProductAdvertising(pakeys.accesskey, pakeys.secretkey, pakeys.associatetag),
                                   limits=mws.PRODUCT_ADVTERTISING_LIMITS,
                                   blocking=True)

        self.mwsapi.api.make_request = self.make_request
        self.paapi.api.make_request = self.make_request

        # Set the priority limits
        for operation in self.mwsapi.limits:
            self.mwsapi.set_priority_quota(operation, priority=0, quota=self.mwsapi.limits[operation].quota_max - 2)
            self.mwsapi.set_priority_quota(operation, priority=10, quota=2)

    def register_callback(self, op, callback):
        self._callbacks[op] = callback

    def _before_commit_listener(self, session):
        """Checks if any Operations have been added/modified in the session. If so, calls load_next()."""
        for item in chain(session.new, session.dirty, session.deleted):
            if isinstance(item, Operation):
                break
        else:
            return

        if self.running:
            self.load_next()

    def start(self):
        """Starts processing operations in the database."""
        self.status_message.emit('Begin processing operations...')
        self.running = True
        self.load_next()

    def stop(self):
        """Remove all pending operations from the queue."""
        self.status_message.emit('Stopping all operations.')
        self.running = False

        for t_id in self.scheduled:
            self.killTimer(t_id)
        self.scheduled.clear()

    def load_next(self):
        """Load and schedule the next operation of each type listed in self.supported_ops."""
        if not self.running:
            return

        for op_name in self.supported_ops:
            eligible_ops = self.dbsession.query(Operation).\
                                          filter(Operation.complete == False).\
                                          filter(Operation.error == False).\
                                          filter(Operation.operation == op_name)

            # Get the highest-priority event older than the current time
            next_op = eligible_ops.filter(Operation.scheduled <= func.now()).\
                                   order_by(Operation.priority.desc()).\
                                   order_by(Operation.scheduled).\
                                   first()

            # If nothing is overdue, schedule event with the nearest scheduled time
            if next_op is None:
                next_op = eligible_ops.order_by(Operation.scheduled).\
                                       order_by(Operation.priority.desc()).\
                                       first()

                # If no more ops of this type, skip to the next one
                if next_op is None:
                    continue

            # Make sure only one operation of this type is scheduled at a time
            for timer_id, sched_op in {k:v for k, v in self.scheduled.items()}.items():
                if sched_op.operation == next_op.operation:
                    self.killTimer(timer_id)
                    self.scheduled.pop(timer_id)

            self.schedule_op(next_op)

    def schedule_op(self, op, wait=None):
        """Get the required wait and set a timer for the given operation."""
        if wait is None:
            # Get next available time from the throttler
            throttled_wait = self.get_wait(op.operation, op.priority)

            delta = op.scheduled - arrow.utcnow().naive
            scheduled_wait = delta.total_seconds()

            wait = max(throttled_wait, scheduled_wait, 0)

        # Schedule the timer
        timer_id = self.startTimer(wait * 1000 * 1.1)
        self.scheduled[timer_id] = op

    def get_wait(self, operation, priority):
        """Return the wait time, in seconds, before the given api_call can be executed."""
        if operation == 'FindAmazonMatches':
            return self.mwsapi.request_wait('ListMatchingProducts', priority)

        elif operation == 'GetMyFeesEstimate':
            return self.mwsapi.request_wait('GetMyFeesEstimate', priority)

        elif operation == 'UpdateAmazonListing':
            return self.paapi.request_wait('ItemLookup', priority) \
                   + self.mwsapi.request_wait('GetLowestOfferListingsForASIN', priority)

        elif operation == 'SearchAmazon':
            return self.mwsapi.request_wait('ListMatchingProducts', priority)

        elif operation == 'TestMargins':
            return self.get_wait('GetMyFeesEstimate', priority)

        else:
            return max(self.mwsapi.request_wait(operation, priority), self.paapi.request_wait(operation, priority))

    def timerEvent(self, event):
        """Do the operation scheduled by the given timer."""
        if self.processing:
            event.ignore()
            return

        # Kill the timer and get the associated operation
        timer_id = event.timerId()
        self.killTimer(timer_id)
        op = self.scheduled.pop(timer_id)

        # If the op was deleted just load the next one
        try:
            op.id
        except ObjectDeletedError:
            self.load_next()
            return

        # Handle the operation
        status_message = 'Processing: \'%s\', priority=%s' % (op.operation, op.priority)
        handler = getattr(self, op.operation, None)
        if handler is None:
            op.error = True
            op.message = 'No handler found.'
            self.dbsession.commit()

            status_message += ', error: No handler found.'
            self.status_message.emit(status_message)
            return

        self.processing = True
        handler(op)
        self.processing = False
        self.dbsession.commit()

        if op.complete or op.error:
            if self._callbacks.get(op):
                self._callbacks[op](op)

        if op.complete:
            status_message += ': %s' % (op.message or 'complete.')
            self.operation_complete.emit(op.id)
        elif op.error:
            status_message += ', error: %s' % op.message
        elif not op.complete and not op.error:
            status_message += ': %s' % op.message if op.message else ''

        self.status_message.emit(status_message)

    def is_error_response(self, reply, op):
        """Test if the response is an error, and take appropriate action."""
        status_code = reply.attribute(QNetworkRequest.HttpStatusCodeAttribute)
        error = reply.error()

        if status_code == 200:
            return False

        # Try to parse the error response, if there is one
        msg = 'Status code %i, ' % status_code
        try:
            parser = ErrorResponseParser(reply.readAll().data().decode())
            msg += '%s - %s' % (parser.code, parser.message)
        except ParseError:
            msg += 'no parsable response.'

        op.message = msg

        # 400 usually means an invalid parameter
        if status_code in [400]:
            op.error = True
        # 401, 403, 404 means there was a problem with the keys, signature, or address used
        elif status_code in [401, 403, 404]:
            self.stop()
        # 500 or 503 usually means internal service error or throttling
        elif status_code in [500, 503]:
            self.stop()
            QTimer.singleShot(5 * 60 * 1000, self.start)
        # Connection reset, timed out, network session failure, etc
        elif error in [QNetworkReply.ConnectionRefusedError,
                       QNetworkReply.TimeoutError,
                       QNetworkReply.ServiceUnavailableError,
                       QNetworkReply.NetworkSessionFailedError]:
            self.stop()
            QTimer.singleShot(15 * 60 * 1000, self.start)
            msg += ' Connection reset, timed out, or service unavailable. Waiting 15 minutes.'

        return True

    def make_request(self, *args, **kwargs):
        """Make the actual network request."""
        url = QUrl(kwargs['url'])
        request = QNetworkRequest(url)

        for k, v in kwargs['headers'].items():
            request.setRawHeader(k.encode(), v.encode())

        reply = self.network_manager.sendCustomRequest(request, kwargs['method'].encode(), kwargs['data'])

        while reply.isRunning():
            QCoreApplication.processEvents(QEventLoop.AllEvents, 100)

        return reply

    def TestMargins(self, op):
        """Look at the potential profit margin for a listing, based on available sources. Add the listing to a list
        if the margin meets a minimum threshold.

        Parameters:         threshold=      The minimum profit margin to be added to the list.
                            list=           The name of the list to add matches to.
        """
        amz_listing = op.listing
        params = op.params

        if not amz_listing.price or not amz_listing.quantity:
            op.complete = True
            return

        # Get the lowest vendor cost available
        vnd_unit_cost = self.dbsession.query(func.min(VendorListing.unit_price)).\
                                        join(LinkedProducts, LinkedProducts.vnd_listing_id == VendorListing.id).\
                                        filter(LinkedProducts.amz_listing_id == amz_listing.id).\
                                        scalar()
        if vnd_unit_cost is None:
            op.complete = True
            return

        # Test the margin based solely on cost
        cost = vnd_unit_cost * amz_listing.quantity
        profit = amz_listing.price - cost

        if profit / cost < params['threshold']:
            op.complete = True
            return

        # Now get fees
        price_point = self.dbsession.query(AmzPriceAndFees).\
                                     filter_by(amz_listing_id=amz_listing.id,
                                               price=amz_listing.price).\
                                     first()
        if price_point is None:
            price_point = AmzPriceAndFees(amz_listing=amz_listing, price=amz_listing.price)
            self.dbsession.add(price_point)

        if price_point.fba is None:
            self.GetMyFeesEstimate(op)

        fba, prep, ship = self.dbsession.query(func.ifnull(AmzPriceAndFees.fba, amz_listing.price * .25),
                                               func.ifnull(AmzPriceAndFees.prep, 0),
                                               func.ifnull(AmzPriceAndFees.ship, 0)).\
                                         filter_by(amz_listing_id=amz_listing.id, price=amz_listing.price).\
                                         first()

        # Calculate the margin
        cost = vnd_unit_cost * amz_listing.quantity + prep + ship
        profit = amz_listing.price - cost - fba

        if profit / cost < params['threshold']:
            op.complete = True
            return

        # Add to the list
        add_list = self.dbsession.query(List).filter_by(name=params['list']).first()
        if add_list is None:
            add_list = List(name=params['list'], is_amazon=True)
            self.dbsession.add(add_list)
            self.dbsession.flush()

        self.dbsession.add(self.dbsession.merge(ListMembership(list_id=add_list.id,
                                                               listing_id=amz_listing.id)))
        op.complete = True

    def SearchAmazon(self, op):
        """Find Amazon listings based on given search terms. Add the results to a list.

        Parameters:     terms=      A string containing search terms.
                        addtolist=  A list name to add results to.
        """
        params = op.params

        r = self.mwsapi.ListMatchingProducts(priority=op.priority, MarketplaceId=self.mwsapi.api.market_id(), Query=params['terms'])
        if self.is_error_response(r, op):
            return

        parser = ListMatchingProductsParser(r.readAll().data().decode())

        for product in parser.get_products():
            previous_id = self.dbsession.query(AmazonListing.id).filter_by(sku=product['asin']).scalar()
            amz_listing = self.dbsession.merge(AmazonListing(id=previous_id, vendor_id=0, sku=product['asin']))

            amz_listing.title = product['title']
            amz_listing.brand = product['brand']
            amz_listing.model = product['model']
            amz_listing.upc = product['upc']
            amz_listing.quantity = product['quantity']
            amz_listing.salesrank = product['salesrank']
            amz_listing.updated = func.now()

            self.dbsession.add(amz_listing)

            # Create a new category if necessary
            pcid = product['productcategoryid']
            if pcid is not None:
                category = self.dbsession.query(AmazonCategory).filter_by(product_category_id=pcid).first()
                if category is None:
                    category = AmazonCategory(name=pcid, product_category_id=pcid)
                    self.dbsession.add(category)
                amz_listing.category = category

            # Add to list
            if 'addtolist' in params:
                add_list = self.dbsession.query(List).filter_by(name=params['addtolist']).first()
                if add_list is None:
                    add_list = List(name=params['addtolist'], is_amazon=True)
                    self.dbsession.add(add_list)
                    self.dbsession.flush()

                self.dbsession.add(self.dbsession.merge(ListMembership(list_id=add_list.id,
                                                                       listing_id=amz_listing.id)))

            # Schedule an update to fill in the rest of the product info
            self.dbsession.flush()
            self.dbsession.add(Operation.UpdateAmazonListing(listing_id=amz_listing.id, priority=op.priority))

        op.complete = True

    def FindAmazonMatches(self, op):
        """Query Amazon for products matching a given listing.

        Parameters:     linkif:         create a link only if the conditions are met
                            conf=       match confidence greater than or equal to the given value.

                        testmargins:    Create a TestMargins operation if the conditions are met.
                            salesrank=  Maximum sales rank
                            list=       The name of the list given to TestMargins
                            threshold=  The minimum margin threshold given to TestMargins
        """
        vnd_listing = op.listing
        params = op.params

        title = str(vnd_listing.title).replace(vnd_listing.brand, '').replace(vnd_listing.model, '').strip()
        query = ' '.join([vnd_listing.brand, vnd_listing.model, title])

        r = self.mwsapi.ListMatchingProducts(priority=op.priority, MarketplaceId=self.mwsapi.api.market_id(), Query=query)
        if self.is_error_response(r, op):
            return

        parser = ListMatchingProductsParser(r.readAll().data().decode())

        for product in parser.get_products():
            previous_id = self.dbsession.query(AmazonListing.id).filter_by(sku=product['asin']).scalar()
            amz_listing = self.dbsession.merge(AmazonListing(id=previous_id, vendor_id=0, sku=product['asin']))

            amz_listing.title = product['title']
            amz_listing.brand = product['brand']
            amz_listing.model = product['model']
            amz_listing.upc = product['upc']
            amz_listing.quantity = product['quantity']
            amz_listing.salesrank = product['salesrank']
            amz_listing.updated = func.now()

            # Create a new category if necessary
            pcid = product['productcategoryid']
            if pcid is not None:
                category = self.dbsession.query(AmazonCategory).filter_by(product_category_id=pcid).first()
                if category is None:
                    category = AmazonCategory(name=pcid, product_category_id=pcid)
                    self.dbsession.add(category)
                amz_listing.category = category

            # Create a link between the two listings
            link = LinkedProducts()
            link.brand_match = brand_match(amz_listing, vnd_listing)
            link.model_match = model_match(amz_listing, vnd_listing)
            link.title_match = title_match(amz_listing, vnd_listing)
            link.confidence = sum([link.brand_match * 2, link.model_match * 2, link.title_match]) / 5

            # Add the link if it meets the criteria, or if no criteria were provided
            add_cond_1 = 'linkif' in params \
                            and 'conf' in params['linkif'] \
                            and link.confidence >= float(params['linkif']['conf'])
            add_cond_2 = 'linkif' not in params

            if add_cond_1 or add_cond_2:
                self.dbsession.flush()
                link.amz_listing_id = amz_listing.id
                link.vnd_listing_id = vnd_listing.id
                self.dbsession.merge(link)

                # Test margins?
                if 'testmargins' in params:
                    if 'salesrank' not in params['testmargins'] \
                        or (amz_listing.salesrank and amz_listing.salesrank <= params['testmargins']['salesrank']):

                        update_op = Operation.UpdateAmazonListing(listing=amz_listing,
                                                                  params={'testmargins': params['testmargins']},
                                                                  priority=op.priority)
                        self.dbsession.add(update_op)

        op.message = '%s links found.' % len(vnd_listing.amz_links)
        op.complete = True

    def GetMyFeesEstimate(self, op):
        """Get an FBA fees estimate for the given listing.

        Parameters:     price=  Update all price points at the given price. If not provided, update all price points
                                at the current listing price. Create a new price point if none exist.

                        fees=   Set the fees to the given value. If not provided, request fees from Amazon.
        """
        amz_listing = op.listing
        params = op.params

        if 'price' in params:
            price = float(params['price'])
        else:
            price = amz_listing.price

        if 'fees' in params:
            fba_fees = float(params['fees'])
        else:
            feerequest = {'MarketplaceId': self.mwsapi.api.market_id(),
                          'IdType': 'ASIN',
                          'IdValue': amz_listing.sku,
                          'Identifier': 'prwlr',
                          'IsAmazonFulfilled': 'true',
                          'PriceToEstimateFees.ListingPrice.CurrencyCode': 'USD',
                          'PriceToEstimateFees.ListingPrice.Amount': price}

            r = self.mwsapi.GetMyFeesEstimate(FeesEstimateRequestList=[feerequest])
            if self.is_error_response(r, op):
                return

            parser = GetMyFeesEstimateParser(r.readAll().data().decode())
            fees = next(parser.get_fees())
            if fees is None or fees['status'] != 'Success':
                op.error = True
                op.message = fees['errormessage']
                return
            else:
                fba_fees = fees['amount']

        # Get all the price points this fee request applies to
        price_point = None
        for price_point in self.dbsession.query(AmzPriceAndFees).filter_by(amz_listing_id=amz_listing.id, price=price):
            price_point.fba = fba_fees
        if price_point is None:
            price_point = AmzPriceAndFees(amz_listing=amz_listing, price=price, fba=fba_fees)
            self.dbsession.add(price_point)

        op.complete = True

    def UpdateAmazonListing(self, op):
        """Update pricing, salesrank, offers, and merchant info for listing, then add to product history.

        Parameters:         log=            Add the new product data to the log
                            repeat=         Repeat this operation after the given number of minutes.
                            testmargins:    Create a TestMargins operation if the criteria are met.
                                salesrank=  Sales Rank must be below the given value.
                                threshold=  The minimum require profit margin to add to the list.
                                list=       The name of the list to add matches to.
        """

        amz_listing = op.listing
        params = op.params

        r = self.paapi.ItemLookup(priority=op.priority,
                                  ItemId=amz_listing.sku,
                                  ResponseGroup='OfferFull,SalesRank,ItemAttributes')

        if self.is_error_response(r, op):
            return

        parser = ItemLookupParser(r.readAll().data().decode())
        info = parser.get_info()

        amz_listing.url = info['url']
        amz_listing.salesrank = info['salesrank']
        amz_listing.upc = info['upc']
        amz_listing.offers = info['offers']
        amz_listing.price = info['price']
        amz_listing.hasprime = info['prime']
        amz_listing.updated = func.now()

        # Add a new merchant if necessary
        merchant = self.dbsession.query(AmazonMerchant).filter_by(name=info['merchant'] or 'N/A').first()
        if merchant:
            amz_listing.merchant_id = merchant.id
        else:
            name = info['merchant'] or 'N/A'
            merchant = AmazonMerchant(name=name)
            self.dbsession.add(merchant)
            self.dbsession.flush()
            amz_listing.merchant_id = merchant.id

        # Fall back on GetLowestOfferListings if necessary
        if amz_listing.price is None:
            r = self.mwsapi.GetLowestOfferListingsForASIN(priority=op.priority,
                                                          MarketplaceId=self.mwsapi.api.market_id(),
                                                          ASINList=[amz_listing.sku],
                                                          ItemCondition='New')

            if self.is_error_response(r, op):
                return

            parser = GetLowestOfferListingsForASINParser(r.readAll().data().decode())
            result = next(parser.get_product_info())

            if result['error']:
                op.error = True
                op.message = result['message']
                return
            else:
                amz_listing.price = result['price']
                amz_listing.hasprime = result['prime']

        # Test margins?
        if 'testmargins' in params:
            if 'salesrank' not in params['testmargins'] \
                or (amz_listing.salesrank and amz_listing.salesrank <= params['testmargins']['salesrank']):

                test_op = Operation.TestMargins(listing=amz_listing,
                                                params=params['testmargins'],
                                                priority=op.priority)
                self.dbsession.add(test_op)

        if 'log' in params and params['log'] == True:
            self.dbsession.add(AmzProductHistory(amz_listing_id=amz_listing.id,
                                                 salesrank=amz_listing.salesrank,
                                                 hasprime=amz_listing.hasprime,
                                                 price=amz_listing.price,
                                                 merchant_id=amz_listing.merchant_id,
                                                 offers=amz_listing.offers,
                                                 timestamp=func.now()))

        if 'repeat' in params and params['repeat'] > 0:
            op.scheduled = arrow.utcnow().replace(minutes=params['repeat']).naive
        else:
            op.complete = True


