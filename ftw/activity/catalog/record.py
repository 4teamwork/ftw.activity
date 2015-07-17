from AccessControl import getSecurityManager
from collective.prettydate.interfaces import IPrettyDate
from DateTime import DateTime
from ftw.activity.events import ActivityCreatedEvent
from ftw.activity.utils import roles_and_users_for_permission
from plone.app.uuid.utils import uuidToObject
from plone.uuid.interfaces import IUUID
from Products.CMFCore.utils import getToolByName
from souper.soup import Record
from zope.component import getUtility
from zope.component.hooks import getSite
from zope.event import notify
from zope.i18n import translate


class ActivityRecord(Record):

    def __init__(self, context, action, actor_userid=None, date=None):
        self.attrs['allowed_roles_and_users'] = (
            roles_and_users_for_permission(context, 'View'))
        self.attrs['path'] = '/'.join(context.getPhysicalPath())
        self.attrs['uuid'] = IUUID(context)
        self.attrs['portal_type'] = context.portal_type
        self.attrs['title'] = context.Title()
        self.attrs['action'] = action
        self.attrs['actor'] = (actor_userid
                               or getSecurityManager().getUser().getId())
        self.attrs['date'] = date or DateTime()

        notify(ActivityCreatedEvent(context, self))

    def get_object(self):
        obj = uuidToObject(self.attrs['uuid'])
        return obj

    def get_actor_info(self):
        membership = getToolByName(getSite(), 'portal_membership')
        portal_url = getToolByName(getSite(), 'portal_url')

        userid = self.attrs['actor']
        member = membership.getMemberById(userid)
        if not member:
            return {'url': '',
                    'portrait_url': portal_url() + '/defaultUser.png',
                    'fullname': userid or 'N/A'}

        portrait = membership.getPersonalPortrait(userid)
        return {'url': membership.getHomeUrl(userid),
                'portrait_url': portrait and portrait.absolute_url() or '',
                'fullname': member.getProperty('fullname') or userid}

    def get_pretty_date(self):
        date_utility = getUtility(IPrettyDate)
        return {
            'relative': date_utility.date(self.attrs['date']),
            'absolute': self.attrs['date']}

    def translated_portal_type(self):
        request = getSite().REQUEST
        portal_types = getToolByName(getSite(), 'portal_types')
        fti = portal_types.get(self.attrs['portal_type'], None)
        default = translate(self.attrs['portal_type'], domain='plone',
                            context=request)
        if fti:
            return translate(fti.title, domain=fti.i18n_domain,
                             default=default,
                             context=request)
        return default

    def __str__(self):
        return '<{0} "{1}" for "{2}">'.format(
            self.__class__.__name__,
            self.attrs['action'],
            self.attrs['path'])

    __repr__ = __str__
