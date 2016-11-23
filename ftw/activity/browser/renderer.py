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


class DefaultCommentRenderer(DefaultRenderer):
    index = ViewPageTemplateFile('templates/comment.pt')
    comment_crop_length = 100

    def __init__(self, *args, **kwargs):
        super(DefaultCommentRenderer, self).__init__(*args, **kwargs)
        self.ploneview = self.context.restrictedTraverse('@@plone')

    def position(self):
        return 900

    def match(self, activity, obj):
        return activity.attrs['action'].startswith('comment:')

    def render(self, activity, obj):
        return self.index(
            activity=activity,
            obj=obj,
            comment=self.crop_comment(activity.attrs['comment_text']))

    def crop_comment(self, comment_text):
        return self.ploneview.cropText(comment_text, self.comment_crop_length)
