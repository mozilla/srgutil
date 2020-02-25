import json

import boto3
import pytest

from moto import mock_s3

import pickle
from srgutil.cache import LazyJSONLoader
from srgutil.context import default_context as d_ctx
from srgutil.interfaces import IClock


# TODO Given that these are mocked, can they be anythin?
ADDON_LIST_BUCKET = "telemetry-parquet"
ADDON_LIST_KEY = "taar/lite/guid_coinstallation.json"
GUID_RANKING_KEY = "taar/list/guid_install_ranking.json"


@pytest.fixture
def default_ctx():
    return d_ctx()


@pytest.fixture
def MOCK_DATA():
    return {
        "a": {"b": 1},
        "b": {"a": 1},
    }


@pytest.fixture
def MOCK_GUID_RANKING():
    return {
        "a": 10,
        "b": 20,
    }


def install_mock_data(MOCK_DATA, MOCK_GUID_RANKING):
    conn = boto3.resource("s3", region_name="us-west-2")

    conn.create_bucket(Bucket=ADDON_LIST_BUCKET)

    conn.Object(ADDON_LIST_BUCKET, ADDON_LIST_KEY).put(
        Body=json.dumps(MOCK_DATA)
    )
    conn.Object(ADDON_LIST_BUCKET, GUID_RANKING_KEY).put(
        Body=json.dumps(MOCK_GUID_RANKING)
    )


@mock_s3
def test_get_json_hot_cache(default_ctx, MOCK_DATA, MOCK_GUID_RANKING):
    MOCK_DATA["s3_cached_copy"] = True
    install_mock_data(MOCK_DATA, MOCK_GUID_RANKING)
    coinstall_loader = LazyJSONLoader(
        default_ctx, ADDON_LIST_BUCKET, ADDON_LIST_KEY
    )

    actual, _ = coinstall_loader.get()
    assert "s3_cached_copy" in actual


@mock_s3
def test_pickle_lazyjson(default_ctx, MOCK_DATA, MOCK_GUID_RANKING):
    MOCK_DATA["s3_cached_copy"] = True
    install_mock_data(MOCK_DATA, MOCK_GUID_RANKING)
    coinstall_loader = LazyJSONLoader(
        default_ctx, ADDON_LIST_BUCKET, ADDON_LIST_KEY
    )

    l_pickle = pickle.dumps(coinstall_loader)
    pickle.loads(l_pickle)


@mock_s3
def test_get_json_cold_cache(default_ctx, MOCK_DATA, MOCK_GUID_RANKING):
    install_mock_data(MOCK_DATA, MOCK_GUID_RANKING)
    coinstall_loader = LazyJSONLoader(
        default_ctx, ADDON_LIST_BUCKET, ADDON_LIST_KEY
    )

    coinstall_loader._cached_copy = None

    actual, _ = coinstall_loader.get()

    # The data from the S3 mocking should be loaded here
    assert actual == MOCK_DATA


@mock_s3
def test_cache_ttl_honored(default_ctx, MOCK_DATA, MOCK_GUID_RANKING, capsys):
    install_mock_data(MOCK_DATA, MOCK_GUID_RANKING)

    class mock_clock:
        def set_time(self, time):
            self._time = time

        def time(self):
            return self._time

    clock = mock_clock()
    clock.set_time(0)

    default_ctx.set(IClock, clock)

    coinstall_loader = LazyJSONLoader(
        default_ctx, ADDON_LIST_BUCKET, ADDON_LIST_KEY, 30
    )

    # Force cached copy to be cleared
    coinstall_loader._cached_copy = None

    class check_call:
        def __init__(self, method):
            self._method = method
            self._called = False

        def __call__(self, *args, **kwargs):
            self._called = True
            return self._method(*args, **kwargs)

        def clear_call(self):
            self._called = False

        def called(self):
            return self._called

    coinstall_loader._refresh_cache = check_call(
        coinstall_loader._refresh_cache
    )

    # Check that refresh cache is called on the get from cold cache
    # state
    assert coinstall_loader._refresh_cache.called() is False
    actual, refreshed = coinstall_loader.get()
    assert refreshed is True
    assert coinstall_loader._refresh_cache.called()

    # The data from the S3 mocking should be loaded here
    assert actual == MOCK_DATA

    # Clear the call state and force lots of reloads
    coinstall_loader._refresh_cache.clear_call()
    for _ in range(200):
        actual, refreshed = coinstall_loader.get()
        assert refreshed is False
    assert coinstall_loader._refresh_cache.called() is False

    # Forward the clock to go past TTL and verify that get() forces a
    # refresh
    clock.set_time(500)
    actual, refreshed = coinstall_loader.get()
    assert refreshed is True
    assert coinstall_loader._refresh_cache.called()
