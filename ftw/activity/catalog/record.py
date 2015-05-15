from AccessControl import getSecurityManager
from DateTime import DateTime
from plone.uuid.interfaces import IUUID
from Products.CMFCore.utils import getToolByName
from souper.soup import Record
from zope.component.hooks import getSite


class ActivityRecord(Record):

    def __init__(self, context, action, actor_userid=None, date=None):
        self.attrs['path'] = '/'.join(context.getPhysicalPath())
        self.attrs['uuid'] = IUUID(context)
        self.attrs['portal_type'] = context.portal_type
        self.attrs['action'] = action
        self.attrs['actor'] = (actor_userid
                               or getSecurityManager().getUser().getId())
        self.attrs['date'] = date or DateTime()

    def get_object(self):
        reference_catalog = getToolByName(getSite(), 'reference_catalog')
        return reference_catalog.lookupObject(self.attrs['uuid'])

    def __str__(self):
        return '<{0} "{1}" for "{2}">'.format(
            self.__class__.__name__,
            self.attrs['action'],
            self.attrs['path'])
