from zope.component.interfaces import IObjectEvent
from zope.interface import Attribute
from zope.interface import Interface


class IActivityRenderer(Interface):
    """An activity renderer renders an activity to HTML.

    It is a named multi-adapter, adapting any context, request and
    the activity view.
    The adapted context is not the object on which the activity happened,
    but the context where the stream is rendered.

    The name of the multi-adapter is for distinguishing the renderers and
    for beeing able to query multiple renderes (getAdapter), but the name is
    in fact irrelevant.

    The ordering is done with the ``position`` method.

    The call order is:

    - ``position`` for determining the renderer position in the chain
    - ``match`` for testing whether the renderer knows how to render
      an activity
    - ``render`` for rendering the previously matche activity (if ``match``
      returned a true value)
    - ``match`` for testing the next activity
    - ``render`` for rendering the second activity
    etc.
    """

    def __init__(context, request, view):
        """Adapts a context, request and activity view.
        """

    def position():
        """The position of this renderer in the chain.
        All renderers are ordered by their position.
        The default renderer position is 1000, renderers with lower positions
        precede.
        The default renderer should always be the last in the chain.
        """

    def match(activity, obj):
        """Test whether the renderer can render this ``activity``.
        The ``obj`` may be ``None`` when the object does no longer exist.
        When ``match`` returns a true value, ``render`` will be called for
        this activity.
        """

    def render(activity, obj):
        """Renders the activity.
        """


class IActivityCreatedEvent(IObjectEvent):
    """The activity created event is fired when a new activity record is created.
    """

    activity = Attribute('The activity record.')
    action = Attribute('The activity action.')


class IActivityFilter(Interface):
    """An activity filter can filter activities so that they do not appear
    in the activity view.

    The filters are chained into a pipeline of filters, each filter can drop
    any activity based on its own conditions.

    The filters should be implemented as generators because of performance.

    The filters are ordered by their ``position`` in the pipeline.

    Each activity filter is a named multi-adapter, adapting context, request
    and the activity view.
    """

    def __init__(context, request, view):
        """Adapts a context, request and view.
        """

    def position():
        """The position of this filter in the pipeline.
        This should be a positive integer.
        Small numbers will lead in an early position in the pipeline.
        """

    def process(activities):
        """The process method is called with a iterable (generator) of activity
        records.
        The method is expected to yield all activities which should be kept and
        drop unwanted activites by doing nothing with them.

        The process method may try to get the object of each activity.
        The method should be implemented as generator, otherwise it will break
        the lazy batching and result in processing all activities, even when
        they are not rendered because of the batching.
        """


class IActivitySoupCatalogFactoryExtension(Interface):
    """Adapter interface for extending the catalog factory.
    The **named** adapter adapts the repoze catalog
    (repoze.catalog.interfaces.ICatalog) and may add additional indexes.
    """

    def __init__(catalog):
        """Adapts the catalog.
        """

    def __call__():
        """Extend the catalog with indexes.
        """


class ILocalActivityView(Interface):
    """Marker interface for the local-activity view.
    """
