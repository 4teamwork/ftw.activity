from BTrees.OOBTree import OOBTree
from Products.CMFPlone.interfaces import IPloneSiteRoot
from souper.interfaces import IStorageLocator
from souper.soup import SoupData
from zope.annotation.interfaces import IAnnotations
from zope.component import adapts
from zope.interface import implements


ANNOTATION_KEY = 'ftw.activity.soups'


class SiteStorageLocator(object):
    implements(IStorageLocator)
    adapts(IPloneSiteRoot)

    def __init__(self, context):
        self.context = context

    def storage(self, soup_name):
        annotations = IAnnotations(self.context)
        if ANNOTATION_KEY not in annotations:
            annotations[ANNOTATION_KEY] = OOBTree()

        if soup_name not in annotations[ANNOTATION_KEY]:
            annotations[ANNOTATION_KEY][soup_name] = SoupData()

        return annotations[ANNOTATION_KEY][soup_name]
