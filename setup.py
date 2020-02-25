from setuptools import find_packages, setup

setup(
    # Meta
    author="Mozilla Foundation",
    author_email="fx-data-dev@mozilla.org",
    description="SRG utilities",
    license="MPL 2.0",
    long_description="""srgutil provides set of common tools required
    for use with TAAR and other SRG applications.

    Among other things, srgutil provides:

    * a context to inject dependencies into to reduce dependencies
      between modules
    * logging configuration that complies to mozlog format
    * clock interfaces to make testing easier when wall clock time is
      required
    * S3 APIs to write date stamped files into S3 in a consistent
      manner.
    """,
    name="mozilla-srgutil",
    url="https://github.com/mozilla/srgutil",
    version="0.2.0",
    # Dependencies
    # Note that we only care about unversioned requirements in
    # setup.py.  We pin those versions with requirements.txt
    # Packaging
    include_package_data=True,
    packages=find_packages(exclude=["tests", "tests/*"]),
    zip_safe=False,
    # Classifiers
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment :: Mozilla",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
)
