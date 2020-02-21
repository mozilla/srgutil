from srgutil.ua_parser import parse_ua, OSNAME_TO_ID


def test_user_agent_strings():
    """
    The UA String parser should only care about selecting the right
    platform for Firefox UA strings.  Any non-firefox browser should
    get all available addons.
    """
    ua_strings = {
        "windows": "Mozilla/5.0 (Windows NT x.y; rv:10.0) Gecko/20100101 Firefox/10.0",
        "macintosh": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:60.0) Gecko/20100101 Firefox/60.0",
        "linux": "Mozilla/5.0 (X11; Linux i686; rv:10.0) Gecko/20100101 Firefox/10.0",
        "android": "Mozilla/5.0 (Android; Mobile; rv:40.0) Gecko/40.0 Firefox/40.0",
    }

    not_fx_ua_strings = [
        # Chrome
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",  # noqa
        # Microsoft Edge
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246",  # noqa
        # Safari
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A",  # noqa
    ]

    # These are valid Firefox UA strings
    for platform, ua in ua_strings.items():
        platform_id = parse_ua(ua)
        assert OSNAME_TO_ID[platform] == platform_id

    # These are non-Firefox UA strings - we should expect nothing
    for ua in not_fx_ua_strings:
        actual_name = parse_ua(ua)
        assert actual_name is None
