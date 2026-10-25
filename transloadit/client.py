import hashlib
import hmac
import json
import re
from datetime import datetime, timedelta

import requests

ASSEMBLY_API_URL = 'http://api2.transloadit.com/assemblies'

# A response body that still carries HTTP chunked-encoding framing starts
# with a hex chunk-size line (issue #5 reports ``9fd\r\n{...}\r\n0\r\n\r\n``).
_CHUNK_PREFIX = re.compile(rb'^([0-9a-fA-F]+)\r\n')


def _unframe(body):
    """Return ``body`` without chunked-encoding framing, when the framing
    is embedded in the body itself.

    The framing is only stripped when the declared chunk size exactly
    covers the remainder of the body up to the CRLF that precedes the
    terminating zero chunk; anything else is returned untouched.
    """
    match = _CHUNK_PREFIX.match(body)
    if not match:
        return body
    size = int(match.group(1), 16)
    start = match.end()
    if size == 0 or len(body) < start + size + 1 or body[start + size] != 0x0D:
        return body
    return body[start:start + size]


class Client(object):
    def __init__(self, key, secret, api=None):
        self.key = key
        self.secret = secret
        if api:
            self.api = api
        else:
            self.api = ASSEMBLY_API_URL

    def _sign_request(self, params):
        secret = self.secret
        if not isinstance(secret, bytes):
            secret = secret.encode('utf-8')
        return hmac.new(secret, json.dumps(params).encode('utf-8'),
            hashlib.sha1).hexdigest()

    def request(self, files=None, **params):
        if 'auth' not in params:
            params['auth'] = {
                'key': self.key,
                'expires': (datetime.now() +
                    timedelta(days=1)).strftime('%Y/%m/%d %H:%M:%S')
            }

        response = requests.post(ASSEMBLY_API_URL, data={'params': json.dumps(params),
            'signature': self._sign_request(params)}, files=files)

        return json.loads(_unframe(response.content))
