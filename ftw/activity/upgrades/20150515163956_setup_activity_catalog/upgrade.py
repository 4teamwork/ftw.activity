from ftw.activity.catalog import get_activity_soup
from ftw.activity.catalog import index_object
from ftw.upgrade import UpgradeStep


class SetupActivityCatalog(UpgradeStep):
    """Setup and index soup-based activity catalog.
    """

    def __call__(self):
        self.install_upgrade_profile()
        soup = get_activity_soup()
        if len(soup.data) > 0:
            return
        map(index_object, self.objects({}, 'Index activity catalog.'))
