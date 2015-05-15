from repoze.catalog.catalog import Catalog
from repoze.catalog.indexes.field import CatalogFieldIndex
from repoze.catalog.indexes.path import CatalogPathIndex
from souper.interfaces import ICatalogFactory
from souper.soup import NodeAttributeIndexer
from zope.interface import implements


class ActivitySoupCatalogFactory(object):
    implements(ICatalogFactory)

    def __call__(self, context=None):
        catalog = Catalog()
        catalog[u'path'] = CatalogPathIndex(NodeAttributeIndexer(u'path'))
        catalog[u'portal_type'] = CatalogFieldIndex(NodeAttributeIndexer(
                u'portal_type'))
        catalog[u'action'] = CatalogFieldIndex(NodeAttributeIndexer(u'action'))
        catalog[u'actor'] = CatalogFieldIndex(NodeAttributeIndexer(u'actor'))
        catalog[u'date'] = CatalogFieldIndex(NodeAttributeIndexer(u'date'))
        return catalog