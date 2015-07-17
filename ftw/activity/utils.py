from AccessControl.PermissionRole import rolesForPermissionOn
from Acquisition import aq_base
from Products.CMFCore.utils import getToolByName
import AccessControl


def roles_and_users_for_permission(obj, permission):
    """Returns a list of roles and users with a specific permission.
    """
    acl_users = getToolByName(obj, 'acl_users')

    allowed_roles = set(rolesForPermissionOn(permission, obj))
    if 'Anonymous' in allowed_roles:
        return ['Anonymous']
    if 'Authenticated' in allowed_roles:
        return ['Authenticated']

    result = set(allowed_roles)

    for user, roles in acl_users._getAllLocalRoles(obj).items():
        if set(roles) & allowed_roles:
            result.add('user:' + user)

    if 'Owner' in result:
        result.remove('Owner')
    return list(result)


def get_roles_and_users():
    """Return the roles and users values for the current user,
    which can be used to query against a roles_and_users index.
    """
    user = AccessControl.getSecurityManager().getUser()
    if user == AccessControl.SpecialUsers.nobody:
        return ['Anonymous']

    result = set(['Anonymous'])
    result.update(user.getRoles())
    result.add('user:{}'.format(user.getId()))
    if hasattr(aq_base(user), 'getGroups'):
        result.update(map('user:{}'.format, user.getGroups()))
    return list(result)
