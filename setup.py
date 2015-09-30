import os
from setuptools import setup, find_packages


version = '2.0.0'


tests_require = [
    'ftw.builder',
    'ftw.testbrowser',
    'ftw.testing',
    'plone.app.dexterity',
    'plone.app.referenceablebehavior',
    'plone.app.testing',
    ]


setup(name='ftw.activity',
      version=version,
      description='An activity feed for Plone.',

      long_description=open('README.rst').read() + '\n' + \
          open(os.path.join('docs', 'HISTORY.txt')).read(),

      classifiers=[
        'Framework :: Plone',
        'Framework :: Plone :: 4.3',
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
        ],

      tests_require=tests_require,
      extras_require={'tests': tests_require},

      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
