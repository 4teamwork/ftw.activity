from ftw.activity.catalog import get_activity_soup
from ftw.activity.catalog import index_object
from ftw.activity.catalog.locator import ANNOTATION_KEY
from Products.CMFCore.utils import getToolByName
from zope.annotation.interfaces import IAnnotations


def installed(site):
    index_soup(site)


def uninstalled(site):
    remove_soup(site)


def index_soup(site):
    soup = get_activity_soup()
    if len(soup.data) > 0:
        return

    catalog = getToolByName(site, 'portal_catalog')
    for brain in catalog.unrestrictedSearchResults({}):
        obj = site.unrestrictedTraverse(brain.getPath())
        index_object(obj)


def remove_soup(site):
    annotations = IAnnotations(site)
    if ANNOTATION_KEY in annotations:
        del annotations[ANNOTATION_KEY]
