from DateTime import DateTime
from ftw.activity.catalog import get_activity_soup
from ftw.upgrade import ProgressLogger
from ftw.upgrade import UpgradeStep
from repoze.catalog.indexes.field import CatalogFieldIndex
from souper.soup import NodeAttributeIndexer


class UseUnixTimestampAsSouperIndex(UpgradeStep):
    """Use unix timestamp as souper index.
    """

    def __call__(self):
        self.install_upgrade_profile()
        soup = get_activity_soup()
        index = soup.catalog['date'] = CatalogFieldIndex(
            NodeAttributeIndexer(u'timestamp'))
        msg = 'Reindex souper catalog "date" index'
        for record in ProgressLogger(msg, soup.data.values()):
            record.attrs['timestamp'] = DateTime(record.attrs['date']).millis()
            index.reindex_doc(record.intid, record)
