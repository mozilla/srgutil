import time

import pytest
from srgutil import s3data
from srgutil.context import Context
from srgutil.base import Clock, JSONCache

EXPECTED_JSON = {"foo": 42}
EXPECTED_S3_JSON = {"foo": "bar"}


class Mocks3data:
    def __init__(self):
        self._fetch_count = 0
        self._get_count = 0

    def fetch_json(self, url):
        self._fetch_count += 1
        return EXPECTED_JSON

    def get_s3_json_content(self, s3_bucket, s3_key):
        self._get_count += 1
        return EXPECTED_S3_JSON


@pytest.fixture
def test_ctx():
    ctx = Context()
    ctx['s3data'] = s3data
    ctx['clock'] = Clock()
    ctx['cache'] = JSONCache(ctx)
    return ctx


def test_clock():
    cl = Clock()
    actual = cl.time()
    expected = time.time()

    # The clock should be pretty accurate to now
    assert abs(actual - expected) < 0.1


def test_fetch_json():
    """ Just test a URL that we know will fail """
    ctx = Context()
    ctx['s3data'] = s3data = Mocks3data()
    ctx['clock'] = Clock()
    cache = JSONCache(ctx)
    jdata = cache.fetch_json("http://127.0.0.1:9001/some-nonexistant-url-foo.json")
    assert jdata == EXPECTED_JSON

    assert s3data._fetch_count == 1
    for i in range(10):
        cache.fetch_json("http://127.0.0.1:9001/some-nonexistant-url-foo.json")
    assert s3data._fetch_count == 1


def test_get_s3_json_content():
    """ Just test an S3 bucket and key that doesn't exist """
    ctx = Context()
    ctx['s3data'] = s3data = Mocks3data()
    ctx['clock'] = Clock()
    cache = JSONCache(ctx)
    jdata = cache.get_s3_json_content("taar_not_my_bucket", "this/is/not/a/valid/path")
    assert jdata == EXPECTED_S3_JSON

    assert s3data._get_count == 1
    for i in range(10):
        cache.get_s3_json_content("taar_not_my_bucket", "this/is/not/a/valid/path")
    assert s3data._get_count == 1


def test_expiry():
    """ Just test a URL that we know will fail """
    class MockClock:
        def __init__(self):
            self._now = 100

        def time(self):
            return self._now

    ctx = Context()
    s3data = Mocks3data()
    ctx['s3data'] = s3data
    ctx['clock'] = MockClock()

    cache = JSONCache(ctx)

    cache._ttl = 0  # Set TTL to nothing
    cache.refresh_expiry()

    jdata = cache.fetch_json("http://127.0.0.1:9001/some-nonexistant-url-foo.json")
    assert jdata == EXPECTED_JSON
    jdata = cache.get_s3_json_content("taar_not_my_bucket", "this/is/not/a/valid/path")
    assert jdata == EXPECTED_S3_JSON

    assert s3data._get_count == 1
    assert s3data._fetch_count == 1

    for i in range(10):
        cache.fetch_json("http://127.0.0.1:9001/some-nonexistant-url-foo.json")
        cache.get_s3_json_content("taar_not_my_bucket", "this/is/not/a/valid/path")

    # Cache expires each time
    assert s3data._get_count == 11
    assert s3data._fetch_count == 11
