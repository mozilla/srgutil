import pytest
from srgutil.context import default_context
from srgutil.interfaces import IS3Data


@pytest.fixture
def test_ctx():
    """
    This sets up a basic context for use for testing
    """
    return default_context()


def test_fetch_json(test_ctx):
    """ Just test a URL that we know will fail """
    jdata = test_ctx.impl(IS3Data).fetch_json("http://127.0.0.1:9001/nonexistant-url-foo.json")
    assert jdata is None


def test_get_s3_json_content(test_ctx):
    """ Just test an S3 bucket and key that doesn't exist """
    jdata = test_ctx.impl(IS3Data).get_s3_json_content("taar_not_my_bucket",
                                                       "this/is/not/a/valid/path")
    assert jdata is None
