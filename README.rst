ftw.activity
===============

``ftw.activity`` provides a view with an activity stream for Plone.

.. image:: https://raw.githubusercontent.com/4teamwork/ftw.activity/master/docs/screenshot.png


How it works
============

The feed is based on a simple catalog query restricted to the current
context, ordered by modified date so that the newest modifications are
on top.

**Limitations:**

- The ordering by modified date is not exactly accurate since the
  precision of the catalog index is only down to the minute.
- Since it is based on a catalog query each object only appears once
  even when it is edited multiple times in a row.
- Only existing objects are listed, so deleting objects will not appear
  in the feed at all.
- Only actions which change the modification date are covered.
- We do not register any links or actions, so that you can integrate
  it into Plone as you like. See the usage sections.


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


Custom event representations
============================

By default the each event is represented by some metadata
(e.g. author with portrait, action, etc) and the title of the modified
object.

If you'd like to display more information you can do this by registering
a custom representation adapter in your custom code.

Register the adapter in your ZCML:

.. code:: xml

  <adapter factory=".activity.IssueResponseRepresentation"
           for="..interfaces.IIssueResponse *"
           provides="ftw.activity.interfaces.IActivityRepresentation"
           />

create the adapter class (example `./activity.py`):

.. code:: python

  from ftw.activity.browser.representations import DefaultRepresentation
  from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

  class IssueResponseRepresentation(DefaultRepresentation):
      index = ViewPageTemplateFile('templates/issue_representation.pt')

      # helper methods when needed

and a template (example `./templates/issue_representation.pt`):

.. code:: html

  <metal:wrapper use-macro="context/@@activity_macros/macros/event">
    <metal:CONTENT fill-slot="body-content">

      <div class="issue-text"
           tal:content="context/text" />

    </metal:CONTENT>
  </metal:wrapper>

take a look at the
`activity_macros <https://github.com/4teamwork/ftw.activity/blob/master/ftw/activity/browser/templates/activity_macros.pt>`_
for details on what slots you can fill.



Links
-----

- github: https://github.com/4teamwork/ftw.testbrowser
- pypi: http://pypi.python.org/pypi/ftw.testbrowser
- CI: https://jenkins.4teamwork.ch/search?q=ftw.testbrowser


Copyright
---------

This package is copyright by `4teamwork <http://www.4teamwork.ch/>`_.

``ftw.activity`` is licensed under GNU General Public License, version 2.
