import json
import unittest

import transloadit.client as client_module
from transloadit.client import Client, _unframe


def chunk(body):
    """Wrap ``body`` the way the issue #5 payload arrives: a hex
    chunk-size line, the payload, and the terminating zero chunk."""
    return b"%x\r\n%s\r\n0\r\n\r\n" % (len(body), body)


SAMPLE_JSON = {
    "ok": "ASSEMBLY_EXECUTING",
    "message": "The assembly is currently being executed.",
    "assembly_id": "6d4792703d6011e582c053c1511679dc",
    "bytes_received": 599,
    "bytes_expected": 599,
    "results": {},
}


class UnframeTest(unittest.TestCase):
    def test_plain_body_passes_through(self):
        body = json.dumps(SAMPLE_JSON).encode("utf-8")
        self.assertEqual(_unframe(body), body)

    def test_chunked_framing_is_stripped(self):
        body = json.dumps(SAMPLE_JSON).encode("utf-8")
        framed = chunk(body)
        self.assertEqual(_unframe(framed), body)

    def test_issue_sample_prefix_shape(self):
        # The payload from issue #5 begins ``9fd\r\n{...``: a hex size
        # line ahead of the JSON.  Reproduce that shape with a real
        # 0x9fd-byte body.
        base_len = len(json.dumps(SAMPLE_JSON))
        delta = len(json.dumps(dict(SAMPLE_JSON, pad=""))) - base_len
        body = json.dumps(dict(SAMPLE_JSON,
            pad="x" * (0x9FD - base_len - delta))).encode("utf-8")
        self.assertEqual(len(body), 0x9FD)
        framed = b"9fd\r\n" + body + b"\r\n0\r\n\r\n"
        self.assertEqual(_unframe(framed), body)

    def test_hex_first_line_with_wrong_length_is_untouched(self):
        # A body whose first line merely looks like a chunk size must
        # not be sliced; leave it for json.loads to reject.
        body = b"9fd\r\n{not the right length}\r\n0\r\n\r\n"
        self.assertEqual(_unframe(body), body)

    def test_hex_first_line_at_eof_is_untouched(self):
        self.assertEqual(_unframe(b"9fd\r\n"), b"9fd\r\n")


class RequestParsingTest(unittest.TestCase):
    def setUp(self):
        self.original_post = client_module.requests.post
        self.client = Client(key="k", secret="s")
        self.captured = {}

    def tearDown(self):
        client_module.requests.post = self.original_post

    def post_chunked(self, body):
        class FakeResponse(object):
            content = body

        def fake_post(url, **kwargs):
            self.captured["url"] = url
            self.captured["kwargs"] = kwargs
            return FakeResponse()

        client_module.requests.post = fake_post

    def test_chunked_response_parses(self):
        self.post_chunked(chunk(json.dumps(SAMPLE_JSON).encode("utf-8")))
        parsed = self.client.request()
        self.assertEqual(parsed["ok"], "ASSEMBLY_EXECUTING")
        self.assertEqual(parsed["assembly_id"],
                         "6d4792703d6011e582c053c1511679dc")
        self.assertEqual(parsed["results"], {})

    def test_plain_response_parses(self):
        self.post_chunked(json.dumps(SAMPLE_JSON).encode("utf-8"))
        parsed = self.client.request()
        self.assertEqual(parsed["ok"], "ASSEMBLY_EXECUTING")


if __name__ == "__main__":
    unittest.main()
