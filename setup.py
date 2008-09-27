import os
from setuptools import setup
from setuptools import find_packages

here = os.path.abspath(os.path.dirname(__file__))
package = os.path.join(here, 'Products', 'GenericSetup')
docs = os.path.join(here, 'docs')

def _docs_doc(name):
def _package_doc(name):
    f = open(os.path.join(package, name))
    return f.read()

NAME = 'GenericSetup'

_boundary = '\n' + ('-' * 60) + '\n\n'
README = ( _docs_doc('index.rst')
         + _boundary 
         + _package_doc('CHANGES.txt')
         + _boundary 
         + "\nDownload\n========"
         )

setup(name='Products.GenericSetup',
      version=_package_doc('version.txt').strip(),
      description='Read Zope configuration state from profile dirs / tarballs',
      long_description=README,
      classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Plone",
        "Framework :: Zope2",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Zope Public License",
        "Programming Language :: Python",
        "Topic :: Software Development",
        "Topic :: System :: Archiving :: Packaging",
        "Topic :: System :: Installation/Setup",
        ],
      keywords='web application server zope zope2 cmf',
      author="Zope Corporation and contributors",
      author_email="zope-cmf@zope.org",
      url="http://pypi.python.org/pypi/Products.GenericSetup",
      license="ZPL 2.1 (http://www.zope.org/Resources/License/ZPL-2.1)",
      packages=find_packages(),
      include_package_data=True,
      namespace_packages=['Products'],
      zip_safe=False,
      setup_requires=['eggtestinfo',
                     ],
      install_requires=['setuptools',
                        'five.localsitemanager >= 0.2',
                       #'Zope2-buildout >= 2.10',
                       ],
      tests_require=['zope.testing >= 3.7.0dev',
                     'five.localsitemanager >= 0.2',
                    ],
      test_loader="zope.testing.testrunner.eggsupport:SkipLayers",
      test_suite="Products.GenericSetup.tests",
      entry_points="""
      [zope2.initialize]
      Products.GenericSetup = Products.GenericSetup:initialize
      [distutils.commands]
      ftest = zope.testing.testrunner.eggsupport:ftest
      """,
      )
