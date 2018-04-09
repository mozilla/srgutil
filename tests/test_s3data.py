from srgutil import s3data


def test_fetch_json():
    """ Just test a URL that we know will fail """
    jdata = s3data.fetch_json("http://127.0.0.1:9001/some-nonexistant-url-foo.json")
    assert jdata is None


def test_get_s3_json_content():
    """ Just test an S3 bucket and key that doesn't exist """
    jdata = s3data.get_s3_json_content("taar_not_my_bucket", "this/is/not/a/valid/path")
    assert jdata is None
