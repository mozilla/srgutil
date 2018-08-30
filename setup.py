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
    version="0.1.10",
    # Dependencies
    # Note that we only care about unversioned requirements in
    # setup.py.  We pin those versions with requirements.txt
    install_requires=[
        "boto3==1.7.2",  # 1.7.2 won't break with moto >=1.3.5.
        # More recent versions of boto3
        # will die under test
        "dockerflow>=2018.4.0",
        "requests>=2.19.1",
    ],
    tests_require=[
        "moto>=1.3.5",
        "pytest>=3.7.4",
        "pytest-cov>=2.5.1",
        "pytest-flake8>=1.0.2",
        "requests-mock>=1.5.2",
    ],
    setup_requires=["pytest-runner", "dockerflow"],
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
