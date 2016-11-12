from database import *


def get_or_create(session, dtype, **kwargs):
    """Return either an existing object with the given properties, or a new one."""
    obj = session.query(dtype).filter_by(**kwargs).first()
    if obj is None:
        obj = dtype(**kwargs)
        session.add(obj)

    return obj


def add_ids_to_list(session, listing_ids, list_name):
    """Add all listings specified in ids to list named list_name. Will create a new list if necessary. """
    add_list = get_or_create(session, List, name=list_name)
    session.add(add_list)

    for listing_id in listing_ids:
        get_or_create(session, ListMembership, list=add_list, listing_id=listing_id)

    first = session.query(Listing).filter_by(id=listing_ids[0]).first()
    add_list.is_amazon = isinstance(first, AmazonListing)


def remove_ids_from_list(session, listing_ids, list_name):
    """Remove all specified listings from the given list."""
    rm_list = session.query(List).filter_by(name=list_name).first()
    if not rm_list or not listing_ids:
        return

    for listing_id in listing_ids:
        membership = session.query(ListMembership).filter_by(list_id=rm_list.id, listing_id=listing_id).first()
        if membership:
            session.delete(membership)


def link_products(session, amz_listing_id, vnd_listing_id):
    """Create a link between two products, unless one already exists."""
    link = get_or_create(session, LinkedProducts, amz_listing_id=amz_listing_id, vnd_listing_id=vnd_listing_id)
    return link


def unlink_products(session, amz_listing_id, vnd_listing_id):
    """Delete a link between two products, if one exists."""
    link = session.query(LinkedProducts).filter_by(amz_listing_id=amz_listing_id, vnd_listing_id=vnd_listing_id).first()
    if link:
        session.delete(link)


def get_watch(session, listing_id):
    """Return the repeating UpdateAmazonListing operation associated with this listing, or none."""
    watch = session.query(Operation).filter_by(listing_id=listing_id).\
                                     filter(and_(Operation.operation == 'UpdateAmazonListing',
                                                 Operation.param_string.contains('repeat'))).\
                                     first()
    return watch


def set_watch(session, listing_id, time):
    """Create or modify a product watch, or delete if time=None."""
    watch = get_watch(session, listing_id)

    if time is None:
        if watch:
            session.delete(watch)
    else:
        watch = watch or Operation.UpdateAmazonListing(listing_id=listing_id, priority=5)
        watch.params = {'log': True, 'repeat': time}
        session.add(watch)