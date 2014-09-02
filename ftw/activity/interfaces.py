from zope.interface import Interface


class IActivityRepresentation(Interface):
    """An adapter for representing a object activity.
    """

    def __init__(context, request):
        """Adapts a context and the request.
        """

    def visible():
        """The activity is only visible when ``True`` is returned here.
        """

    def render():
        """Renders the activity and returns HTML.
        """
