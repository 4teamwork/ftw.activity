ftw.activity
============

``ftw.activity`` provides a view with an activity stream for Plone.

.. image:: https://raw.githubusercontent.com/4teamwork/ftw.activity/master/docs/screenshot.png


How it works
============

Activities are stored with event handlers into a custom `souper`_ catalog.
An activity view then renders each activity for a context (recursively) with
activity renderers.


Supported events
================

The default event handlers work for Archetypes and Dexterity objects.

- Object added
- Object changed
- Object deleted
- Object copied
- Object moved
- Workflow transition


Usage
=====


- Add ``ftw.activity`` as dependency to your package (``setup.py``) or
  to your buildout configuration:

::

    [instance]
    eggs +=
        ftw.activity

- Install the generic import profile in Plone's addons control panel.

Once the package is installed there is no link to the view.
The view is available as ``/activity`` on any context, so you might
want to place a link anywhere you like or add an action.

``ftw.activity`` also registers an
`ftw.tabbedview <https://github.com/4teamwork/ftw.tabbedview>`_
tab with the name ``tabbedview_view-activity``.


Custom activities
=================

Custom activities can easily be registered in the `souper`_ catalog and
are automatically rendered:

.. code:: python

    from ftw.activity.catalog import ActivityRecord
    from ftw.activity.catalog import get_activity_soup

    record = ActivityRecord(context, 'downloaded')
    get_activity_soup().add(record)


Activity renderers
==================

The default activity renderer renders the activity with a link to the
object (unless it was deleted), the event and the actor.

However, if you want to change how activities are rendered you can easily
do that with a custom renderer.
An activity renderer is a named multi-adapter.

Be aware that the renderer adapts the context where the activity view is rendered,
not the object on which the activity happened.
The reason for that is that the object may no longer exist.

The renderer must implement three methods, ``position``, ``match`` and ``render``.
Since there may be multiple adapters which can render an activity, the ``position``
is used to determine which renderer precedes.
The ``match`` method is used to ask the renderer whether he wants to render a certain
activity.
If the activity matches, it is renderered using the ``render`` method.

**Warning** Be aware the the object passed to match and render may be ``None``,
when the object was deleted.

Example ZCML registration:

.. code:: xml

    <adapter factory=".activity.CustomActivityRenderer" name="my.package-renderer" />


Implement the adapter (``activity.py``):

.. code:: python

    from ftw.activity.interfaces import IActivityRenderer
    from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
    from zope.component import adapts
    from zope.interface import implements
    from zope.interface import Interface


    class CustomActivityRenderer(object):
        implements(IActivityRenderer)
        adapts(Interface, Interface, Interface)

        index = ViewPageTemplateFile('templates/activity_renderer.pt')

        def __init__(self, context, request, view):
            self.context = context
            self.request = request
            self.view = view
            self.items = []

        def position(self):
            # The position of the default renderer is 1000
            return 500

        def match(self, activity, obj):
            return activity.attrs['portal_type'] == 'MyType'

        def render(self, activity, obj):
            return self.index(activity=activity, obj=obj)


In the template (``templates/activity_renderer.pt``) you may want to use
the default activity macro and extend it:

.. code:: html

  <metal:wrapper use-macro="context/@@activity_macros/macros/event">
    <metal:CONTENT fill-slot="body-content"
                   tal:define="activity nocall:activity|nocall:options/activity">

      <div tal:attributes="class string:activity-icon-{$activity/action}"></div>

    </metal:CONTENT>
  </metal:wrapper>


Store additional information on activities
==========================================

The metadata stored on the activity record can be easily extended with an event handler:

.. code:: xml

    <subscriber
        for="ftw.activity.interfaces.IActivityCreatedEvent"
        handler=".subscribers.enhance_activity_record"
        />

.. code:: python

    def enhance_activity_record(event):
        record = event.activity
        obj = event.object
        record.attrs['creator'] = obj.Creator()

Activity Filters
================

There may be various custom use cases which require activities to be dropped when rendering
the activity view.
For example system activities are recorded for internal purposes which should not show
up in the activity feed.

Activities can easily be filtered by registering an ``IActivityFilter`` adapter:

.. code:: xml

    <adapter factory=".activity.CustomActivityFilter" name="my.package-filter" />


.. code:: python

    from ftw.activity.interfaces import IActivityFilter
    from zope.component import adapts
    from zope.interface import implements
    from zope.interface import Interface


    class CustomActivityFilter(object):
        implements(IActivityFilter)
        adapts(Interface, Interface, Interface)

        def __init__(self, context, request, view):
            self.context = context
            self.request = request
            self.view = view

        def position(self):
            return 500

        def process(self, activities):
            for activity in activities:
                if activity.attrs['action'] == 'custom-action':
                    continue

                yield activity

There is a default ``FilterCloseChanges`` filter, which removes succeding "changed" activites
of the same object which happen in less than 1 Minute between each activity.
This is removes noise from the activity feed when a user edits the same object a lot in short
time, for example when using an external editor.


Local activity view
===================

The ``@@local-activity`` view is available on any context and shows only activities
of the current context but not its children.


Links
=====

- github: https://github.com/4teamwork/ftw.activity
- pypi: http://pypi.python.org/pypi/ftw.activity
- CI: https://jenkins.4teamwork.ch/search?q=ftw.activity


Copyright
=========

This package is copyright by `4teamwork <http://www.4teamwork.ch/>`_.

``ftw.activity`` is licensed under GNU General Public License, version 2.

.. _souper: https://pypi.python.org/pypi/souper
