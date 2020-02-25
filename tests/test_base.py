import time
import boto3
import json

import pickle
import pytest
import requests_mock
from moto import mock_s3
from srgutil.context import default_context
from srgutil.base import Clock, S3CacheDelegate
from srgutil.interfaces import IS3Data, IMozLogging

EXPECTED_JSON = {"foo": 42}
EXPECTED_S3_JSON = {"foo": "bar"}


@pytest.fixture
def ctx():
    return default_context()


def test_clock():
    cl = Clock()
    actual = cl.time()
    expected = time.time()

    # The clock should be pretty accurate to now
    assert abs(actual - expected) < 0.1


@mock_s3
def test_fetch_json(ctx):
    """ Just test a URL that we know will fail """
    with requests_mock.mock() as m:
        uri = "http://127.0.0.1:9001/some-nonexistant-url-foo.json"
        m.get(uri, text=json.dumps(EXPECTED_JSON))
        jdata = ctx.impl(IS3Data).fetch_json(
            "http://127.0.0.1:9001/some-nonexistant-url-foo.json"
        )
        assert jdata == EXPECTED_JSON


@mock_s3
def test_get_s3_json_content(ctx):
    """ Just test an S3 bucket and key that doesn't exist """
    conn = boto3.resource("s3", region_name="us-west-2")

    bucket = "taar_not_my_bucket"
    key = "this/is/not/a/valid/path"

    conn.create_bucket(Bucket=bucket)
    conn.Object(bucket, key).put(Body=json.dumps(EXPECTED_S3_JSON))

    s3data = ctx.get(IS3Data)
    s3data.get_s3_json_content(bucket, key)
    jdata = s3data.get_s3_json_content(bucket, key)
    assert jdata == EXPECTED_S3_JSON


@mock_s3
def test_serialize_ctx_with_logging(ctx):
    ctx = ctx.child()
    c_pickle = pickle.dumps(ctx)
    pickle.loads(c_pickle)


@mock_s3
def test_logger_name(ctx, capsys):
    logging = ctx.get(IMozLogging)

    assert logging.get_prefix().startswith("srg")
    logging.set_prefix("srgutil")

    logger = logging.get_logger("foo")
    logger.info("some log info")

    captured = capsys.readouterr()
    """
    A typical dockerflow JSON message looks like:

    {"Timestamp": 1524503396935840000,
     "Hostname": "some_local_host",
     "Type": "srgutil.foo",
     "Fields": {"msg": "some log info"},
     "Severity": 6,
     "Logger": "srgutil",
     "EnvVersion": "2.0",
     "Pid": 7313}
    """

    jdata = json.loads(captured.err)
    assert jdata["Logger"] == "srgutil"

    # The logger.get_logger method uses the application namespace as a
    # prefix
    assert jdata["Type"] == "srgutil.foo"

    assert jdata["Fields"]["msg"] == "some log info"


def test_s3cachedelegate_pickle(ctx):
    s3d = S3CacheDelegate(ctx)
    s3d_pickle = pickle.dumps(s3d)
    pickle.loads(s3d_pickle)
