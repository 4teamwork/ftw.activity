from ftw.activity.catalog.locator import ANNOTATION_KEY
from ftw.testing.genericsetup import apply_generic_setup_layer
from ftw.testing.genericsetup import GenericSetupUninstallMixin
from unittest2 import TestCase
from zope.annotation.interfaces import IAnnotations


@apply_generic_setup_layer
class TestGenericSetupUninstall(TestCase, GenericSetupUninstallMixin):
    package = 'ftw.activity'

    def assertSnapshotsEqual(self, *args, **kwargs):
        super(TestGenericSetupUninstall, self).assertSnapshotsEqual(*args, **kwargs)
        self.assertSouperCatalogRemoved()

    def assertSouperCatalogRemoved(self):
        annotations = IAnnotations(self.layer['portal'])
        self.assertNotIn(ANNOTATION_KEY, annotations,
                         'souper catalog was not removed successfully when uninstalling.')
