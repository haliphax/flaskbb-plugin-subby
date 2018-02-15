'Adds RSS and email subscriptions to FlaskBB'

from setuptools import setup, find_packages

setup(
    name='flaskbb-plugin-subby',
    packages=find_packages('.'),
    include_package_data=True,
    package_data={'': ['subby/templates', 'subby/migrations']},
    version='1.0',
    author='haliphax',
    author_email='haliphax@github.com',
    description='Adds RSS and email subscriptions for new posts',
    url='https://github.com/haliphax/flaskbb-plugin-subby',
    long_description=__doc__,
    zip_safe=False,
    platforms='any',
    entry_points={'flaskbb_plugins':
                  ['subby = subby']},
    classifiers=[
        'Environment :: Web Environment',
        'Environment :: Plugins',
        'Framework :: Flask',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)
