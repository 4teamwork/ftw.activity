import os
from setuptools import setup, find_packages


version = '2.4.0'


tests_require = [
    'ftw.builder',
    'ftw.tabbedview',
    'ftw.testbrowser',
    'ftw.testing',
    'plone.app.dexterity',
    'plone.app.testing',
    ]


plone4_test_require = [
    'plone.app.referenceablebehavior',
]


setup(name='ftw.activity',
      version=version,
      description='An activity feed for Plone.',

      long_description=open('README.rst').read() + '\n' + \
          open(os.path.join('docs', 'HISTORY.txt')).read(),

      classifiers=[
        'Framework :: Plone',
        'Framework :: Plone :: 4.3',
        'Framework :: Plone :: 5.1',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],

      keywords='ftw activity feed',
      author='4teamwork AG',
      author_email='mailto:info@4teamwork.ch',
      url='https://github.com/4teamwork/ftw.activity',

      license='GPL2',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ftw', ],
      include_package_data=True,
      zip_safe=False,

      install_requires=[
        'Plone',
        'collective.lastmodifier >= 1.1.0',
        'collective.prettydate',
        'ftw.upgrade >= 1.14.4',
        'plone.api',
        'setuptools',
        'souper',
        'node.ext.zodb <= 1.0.1',  # Avoid pulling in ZODB 5
        ],

      tests_require=tests_require,
      extras_require={'tests': tests_require,
                      'plone4_test': plone4_test_require},

      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
