from ftw.activity.portlets import activity_portlet
from ftw.builder import builder_registry
from ftw.builder.dexterity import DexterityBuilder
from ftw.builder.portlets import PlonePortletBuilder


class DxTypeBuilder(DexterityBuilder):
    portal_type = 'DxType'


builder_registry.register('dx type', DxTypeBuilder)


class ActivityPortlet(PlonePortletBuilder):
    assignment_class = activity_portlet.Assignment

builder_registry.register('activity portlet', ActivityPortlet)
