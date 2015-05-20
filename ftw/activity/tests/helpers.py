from ftw.activity.catalog import get_activity_soup
from repoze.catalog.query import Eq
from zope.component.hooks import getSite


def get_soup_activities(attributes=('path', 'action')):
    portal_path = '/'.join(getSite().getPhysicalPath())
    return map(
        lambda record: dict((key, value) for (key, value)
                            in record.attrs.items()
                            if key in attributes),
        get_activity_soup().query(Eq('path', portal_path),
                                  sort_index='date',
                                  reverse=False))
