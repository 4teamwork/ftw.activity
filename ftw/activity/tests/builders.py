from ftw.builder import builder_registry
from ftw.builder.dexterity import DexterityBuilder


class DxTypeBuilder(DexterityBuilder):
    portal_type = 'DxType'


builder_registry.register('dx type', DxTypeBuilder)
