from ftw.activity.browser.renderer import DefaultRenderer
from ftw.activity.interfaces import IActivityRenderer
from unittest2 import TestCase
from zope.interface.verify import verifyClass


class TestDefaultRenderer(TestCase):

    def test_implements_interface_correctly(self):
        verifyClass(IActivityRenderer, DefaultRenderer)
