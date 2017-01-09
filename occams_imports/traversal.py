def traversed(item, parent):
    item.__parent__ = parent
    return item
