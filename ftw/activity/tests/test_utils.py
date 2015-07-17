from ftw.activity.testing import FUNCTIONAL_TESTING
from ftw.activity.utils import get_roles_and_users
from ftw.activity.utils import roles_and_users_for_permission
from ftw.builder import Builder
from ftw.builder import create
from plone.app.testing import login
from plone.app.testing import logout
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from unittest2 import TestCase


PERMISSION = 'FTP access'


class TestRolesAndUsersForPermission(TestCase):
    layer = FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_includes_global_roles(self):
        self.portal.manage_permission(PERMISSION, ['Contributor', 'Reader'],
                                      acquire=False)
        page = create(Builder('page'))
        self.assertEquals(
            ['Contributor', 'Reader'],
            roles_and_users_for_permission(page, PERMISSION))

    def test_includes_local_roles(self):
        self.portal.manage_permission(PERMISSION, [], acquire=False)
        page = create(Builder('page'))
        page.manage_permission(PERMISSION, ['Reader'])
        create(Builder('user').with_roles('Reader', on=page))
        self.assertEquals(
            ['user:john.doe', 'Reader'],
            roles_and_users_for_permission(page, PERMISSION))

    def test_includes_inherited_local_roles(self):
        self.portal.manage_permission(PERMISSION, [], acquire=False)
        parent = create(Builder('folder'))
        parent.manage_permission(PERMISSION, ['Reader'])
        create(Builder('user').with_roles('Reader', on=parent))
        child = create(Builder('page').within(parent))
        self.assertEquals(
            ['user:john.doe', 'Reader'],
            roles_and_users_for_permission(child, PERMISSION))

    def test_respects_block_inheriting_local_roles(self):
        self.portal.manage_permission(PERMISSION, [], acquire=False)
        parent = create(Builder('folder'))
        parent.manage_permission(PERMISSION, ['Reader'])
        create(Builder('user').with_roles('Reader', on=parent))
        child = create(Builder('page').within(parent))
        child.__ac_local_roles_block__ = True
        self.assertEquals(
            ['Reader'],
            roles_and_users_for_permission(child, PERMISSION))

    def test_supports_groups(self):
        self.portal.manage_permission(PERMISSION, [], acquire=False)
        page = create(Builder('page'))
        page.manage_permission(PERMISSION, ['Reader'])
        create(Builder('group')
               .titled('Does')
               .with_roles('Reader', on=page)
               .with_members(create(Builder('user'))))
        self.assertEquals(
            ['user:does', 'Reader'],
            roles_and_users_for_permission(page, PERMISSION))

    def test_merges_to_anonymous_when_possible(self):
        # All users have the Anonymous role, therefore we don't need
        # to resolve roles and users when Anonymous has the permission.
        self.portal.manage_permission(PERMISSION, ['Anonymous', 'Reader'])
        page = create(Builder('page'))
        create(Builder('user').with_roles('Reader', on=page))
        self.assertEquals(
            ['Anonymous'],
            roles_and_users_for_permission(page, PERMISSION))

    def test_merges_to_authenticated_when_possible(self):
        # All users have the Authenticated role, therefore we don't need
        # to resolve roles and users when Authenticated has the permission.
        self.portal.manage_permission(PERMISSION, ['Authenticated', 'Reader'])
        page = create(Builder('page'))
        create(Builder('user').with_roles('Reader', on=page))
        self.assertEquals(
            ['Authenticated'],
            roles_and_users_for_permission(page, PERMISSION))


class TestGetRolesAndUsers(TestCase):
    layer = FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def test_anonymous_users_get_anonymous_role_only(self):
        logout()
        self.assertEquals(['Anonymous'], get_roles_and_users())

    def test_includes_userid(self):
        john = create(Builder('user'))
        login(self.portal, john.getId())
        self.assertIn('user:john.doe', get_roles_and_users())

    def test_includes_global_roles(self):
        setRoles(self.portal, TEST_USER_ID, ['Manager', 'Contributor'])
        self.assertEquals(['Authenticated',
                           'user:AuthenticatedUsers',
                           'user:test_user_1_',
                           'Manager',
                           'Anonymous',
                           'Contributor'], get_roles_and_users())

    def test_includes_group_ids(self):
        john = create(Builder('user'))
        create(Builder('group').titled('Does').with_members(john))
        login(self.portal, john.getId())
        self.assertIn('user:does', get_roles_and_users())

    def test_always_includes_authenticated(self):
        john = create(Builder('user'))
        login(self.portal, john.getId())
        self.assertIn('Authenticated', get_roles_and_users())

    def test_always_includes_anonymous(self):
        john = create(Builder('user'))
        login(self.portal, john.getId())
        self.assertIn('Anonymous', get_roles_and_users())
