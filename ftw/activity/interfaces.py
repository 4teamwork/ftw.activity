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
