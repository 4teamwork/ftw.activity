from ftw.activity import _
from plone import api
from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope import schema
from zope.component import getMultiAdapter
from zope.formlib import form
from zope.interface import implements


class IActivityPortlet(IPortletDataProvider):
    """A portlet which renders the activity stream
    """

    count = schema.Int(
        title=_(u'number_of_items_label',
                default=u'Number of items to display'),
        description=_(u'number_of_items_description',
                      default=u'How many items to list.'),
        required=True,
        default=5)

    show_more = schema.Bool(
        title=_(u'show_more_link', default='Show a link to more activities'),
        default=True)


class Assignment(base.Assignment):
    implements(IActivityPortlet)

    def __init__(self, count=5, show_more=True):
        self.count = count
        self.show_more = show_more

    @property
    def title(self):
        return _(
            u'activity_portlet_title',
            default=u'Activity stream',
        )


class EditForm(base.EditForm):
    form_fields = form.Fields(IActivityPortlet)
    label = _(u'activity_portlet_edit_form_label',
              default=u'Edit Activity Portlet')
    description = _(u'activity_portlet_form_description',
                    default=u'This portlet displays activities.')


class AddForm(base.AddForm):
    form_fields = form.Fields(IActivityPortlet)
    label = _(u'activity_portlet_add_form_label',
              default=u'Add Activity Portlet')
    description = _(u'activity_portlet_form_description',
                    default=u'This portlet displays activities.')

    def create(self, data):
        return Assignment(count=data.get('count', 5),
                          show_more=data.get('show_more', True))


class Renderer(base.Renderer):
    render = ViewPageTemplateFile('templates/activity_portlet.pt')

    def events(self):
        view = getMultiAdapter(
            (self.get_navigation_root(), self.request), name="activity")
        return view.events(self.data.count)

    @property
    def title(self):
        """Portlet title"""
        return self.data.title

    def full_activity_link(self):
        if not self.data.show_more:
            return
        return '%s/@@activity' % self.get_navigation_root().absolute_url()

    def get_navigation_root(self):
        return api.portal.get_navigation_root(self.context)
