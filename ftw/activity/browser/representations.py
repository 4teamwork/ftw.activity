from collective.lastmodifier.interfaces import ILastModifier
from collective.prettydate.interfaces import IPrettyDate
from ftw.activity import _
from ftw.activity.interfaces import IActivityRepresentation
from plone.uuid.interfaces import IUUID
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import adapts
from zope.component import getUtility
from zope.i18n import translate
from zope.interface import implements
from zope.interface import Interface


class DefaultRepresentation(object):
    implements(IActivityRepresentation)
    adapts(Interface, Interface)

    index = ViewPageTemplateFile(
        'templates/default_representation.pt')

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def visible(self):
        return bool(self.get_last_modifier())

    def render(self):
        return self.index()

    def portrait_url(self, member_id):
        mtool = getToolByName(self.context, 'portal_membership')
        portrait = mtool.getPersonalPortrait(member_id)
        if portrait is not None:
            return portrait.absolute_url()
        utool = getToolByName(self.context, 'portal_url')
        # XXX
        return '%s/defaultUser.png' % utool()

    def actor(self):
        last_modifier = self.get_last_modifier()
        mtool = getToolByName(self.context, 'portal_membership')
        member = mtool.getMemberById(last_modifier)
        return {
            'url': mtool.getHomeUrl(member.getId()),
            'portrait_url': self.portrait_url(last_modifier),
            'fullname': member.getProperty('fullname') or \
                member.getId(),
            'member': member}

    def get_last_modifier(self):
        return ILastModifier(self.context).get()

    def portal_type(self):
        portal_types = getToolByName(self.context, 'portal_types')
        fti = portal_types.get(self.context.portal_type, None)
        default = translate(self.context.portal_type, domain='plone',
                            context=self.request)
        if fti:
            return translate(fti.title, domain=fti.i18n_domain,
                             default=default,
                             context=self.request)
        return default

    def action(self):
        # modified and created are not exactly equal,
        # so we only compare down to the second:
        modified = self.context.modified().asdatetime().timetuple()
        created = self.context.created().asdatetime().timetuple()
        if modified == created:
            return _('created')
        else:
            return _('modified')

    def when(self):
        date_utility = getUtility(IPrettyDate)
        return {
            'relative': date_utility.date(self.context.modified()),
            'absolute': self.context.modified()}

    def uid(self):
        return IUUID(self.context)
