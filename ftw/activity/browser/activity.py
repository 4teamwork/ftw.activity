from ftw.activity.catalog import query_soup
from ftw.activity.interfaces import IActivityFilter
from ftw.activity.interfaces import IActivityRenderer
from operator import itemgetter
from plone.memoize import instance
from Products.CMFPlone.utils import normalizeString
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from repoze.catalog.query import Eq
from zope.component import getAdapters


class ActivityView(BrowserView):

    activity_template = ViewPageTemplateFile('templates/activity.pt')
    raw_template = ViewPageTemplateFile('templates/activity_raw.pt')
    events_template = ViewPageTemplateFile('templates/events.pt')

    def __call__(self):
        return self.activity_template()

    def fetch(self):
        """Action for retrieving more events (based on `last_activity` in
        the request) with AJAX.
        """
        self.request.response.setHeader('X-Theme-Disabled', 'True')
        # The HTML stripped in order to have empty response content when
        # there are no tags at all, so that diazo does not try to
        # parse it.
        return self.events_template().strip()

    def raw(self):
        """Action for embedding activity stream into another view.
        The returned HTML does not contain a complete page with
        head / body but only the stream fragment.
        """
        return self.raw_template()

    def events(self, amount=None, last_activity=None):
        amount = int(amount or self.request.get('amount_of_events', 10))
        last_activity = last_activity or self.request.get(
            'last_activity', None)
        activities = self._lookup()
        if last_activity:
            activities = self._begin_after(int(last_activity), activities)
        activities = self._filter_activities(activities)
        activity_infos = self._batch_to(amount, activities)
        return self._lookup_renderers_for_activities(activity_infos)

    def query(self):
        return Eq('path', '/'.join(self.context.getPhysicalPath()))

    def _lookup(self):
        return query_soup(self.query(), sort_index='date', reverse=True)

    def _begin_after(self, last_activity, activities):
        found = False
        for activity in activities:
            if found:
                yield activity
            elif activity.intid == last_activity:
                found = True

    def _filter_activities(self, activities):
        filters = map(itemgetter(1),
                      getAdapters((self.context, self.request, self),
                                  IActivityFilter))
        filters.sort(key=lambda activity_filter: activity_filter.position())
        for activity_filter in filters:
            activities = activity_filter.process(activities)
        return activities

    def _batch_to(self, amount, activities):
        # The is_last_activity is True for the very last activity
        # in activities (not the last on the batch).
        # In order to set this correctly, while preserving generator
        # laziness and not yielding more activities than necessary
        # the implementation has a "previous" cache so that we can
        # look ahead first.
        previous = None
        enumerated_activities = enumerate(activities)
        for index, repr in enumerated_activities:
            if previous is not None:
                yield previous

            previous = {'activity': repr,
                        'is_last_activity': False}

            if index >= amount - 1:
                break

        if previous is not None:
            try:
                next(enumerated_activities)
            except StopIteration:
                # The previous activity yielded was actually the last one
                previous['is_last_activity'] = True
            finally:
                yield previous

    def _lookup_renderers_for_activities(self, activity_infos):
        for activity_info in activity_infos:
            activity = activity_info['activity']
            obj = activity.get_object()
            yield {'activity_id': activity.intid,
                   'activity': activity,
                   'is_last_activity': activity_info['is_last_activity'],
                   'classes': ('event activity-action-{0}'
                               ' activity-contenttype-{1}'.format(
                        normalizeString(activity.attrs['action']),
                        normalizeString(activity.attrs['portal_type']))),
                   'obj': obj,
                   'render': self._find_renderer_for_activity(activity, obj)}

    def _find_renderer_for_activity(self, activity, obj):
        for renderer in self._get_renderers():
            if renderer.match(activity, obj):
                return lambda: renderer.render(activity, obj)

    @instance.memoize
    def _get_renderers(self):
        adapters = getAdapters((self.context, self.request, self),
                               IActivityRenderer)
        renderers = map(itemgetter(1), adapters)
        renderers.sort(key=lambda renderer: renderer.position())
        return renderers
