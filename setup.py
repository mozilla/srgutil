from setuptools import find_packages, setup

setup(
    name='mozilla-srgutil',
    version='0.1.6',
    setup_requires=['pytest-runner', 'dockerflow'],
    tests_require=['pytest'],
    include_package_data=True,
    packages=find_packages(exclude=['tests', 'tests/*']),
    description='SRG utilities',
    author='Mozilla Foundation',
    author_email='fx-data-dev@mozilla.org',
    url='https://github.com/mozilla/srgutil',
    license='MPL 2.0',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment :: Mozilla',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Scientific/Engineering :: Information Analysis'
    ],
    zip_safe=False,
)
