from ftw.activity.interfaces import IActivityRenderer
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import adapts
from zope.interface import implements
from zope.interface import Interface


class DefaultRenderer(object):
    implements(IActivityRenderer)
    adapts(Interface, Interface, Interface)

    index = ViewPageTemplateFile('templates/default.pt')

    def __init__(self, context, request, view):
        self.context = context
        self.request = request
        self.view = view
        self.items = []

    def position(self):
        """The default representation should always be last in the chain and
        has therefore the default position 1000.
        Other generators should have a lower position for preceding it.
        """
        return 1000

    def match(self, activity, obj):
        """The default representation renders all activites not rendered
        by any previous renderer.
        """
        return True

    def render(self, activity, obj):
        return self.index(activity=activity, obj=obj)
