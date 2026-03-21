"""Tests for channel identifier parsing"""

import pytest

from src.analyzer.fetcher import parse_channel_identifier


class TestParseChannelIdentifier:
    def test_full_https_link(self):
        assert parse_channel_identifier("https://t.me/durov") == "durov"

    def test_http_link(self):
        assert parse_channel_identifier("http://t.me/testchannel") == "testchannel"

    def test_at_mention(self):
        assert parse_channel_identifier("@durov") == "durov"

    def test_plain_username(self):
        assert parse_channel_identifier("durov") == "durov"

    def test_with_whitespace(self):
        assert parse_channel_identifier("  @durov  ") == "durov"

    def test_link_with_trailing_slash(self):
        assert parse_channel_identifier("https://t.me/mychannel") == "mychannel"

    def test_invalid_empty(self):
        with pytest.raises(ValueError):
            parse_channel_identifier("")

    def test_invalid_too_short(self):
        with pytest.raises(ValueError):
            parse_channel_identifier("ab")

    def test_invalid_special_chars(self):
        with pytest.raises(ValueError):
            parse_channel_identifier("not a channel!!!")

    def test_underscore_prefix(self):
        assert parse_channel_identifier("_test_channel") == "_test_channel"
