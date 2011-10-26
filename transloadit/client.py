import hashlib
import hmac
import urlparse
import httplib
import mimetypes
from datetime import datetime, timedelta


try:
    from django.utils import simplejson as json
except ImportError:
    import simplejson as json


BASE_API = 'http://api2.transloadit.com/assemblies'
FILE_BOUNDARY = '----------Python_Transloadit_Client_Boundary_$'
CRLF = '\r\n'


class Client(object):
    def __init__(self, key, secret, api=None):
        self.key = key
        self.secret = secret
        if api:
            self.api = api
        else:
            self.api = BASE_API

    def _sign_request(self, params):
        return hmac.new(self.secret, json.dumps(params),
            hashlib.sha1).hexdigest()

    def _send_request(self, files, **fields):
        parts = urlparse.urlparse(self.api)
        content_type, body = self._encode_request(fields, files)
        req = httplib.HTTP(parts[1])
        req.putrequest('POST', parts[2])
        req.putheader('Content-Type', content_type)
        req.putheader('Content-Length', str(len(body)))
        req.endheaders()
        req.send(body)
        errcode, errmsg, headers = req.getreply()
        return json.loads(req.file.read())

    def _encode_request(self, fields, files):
        payload = []

        for key, value in fields.iteritems():
            payload.append('--' + FILE_BOUNDARY)
            payload.append('Content-Disposition: form-data; name="%s"' % key)
            payload.append('')
            payload.append(value)

        if files:
            for key, filename, value in files:
                content_type = self._get_content_type(filename)
                payload.append('--' + FILE_BOUNDARY)
                payload.append('Content-Disposition: form-data;' + \
                    ' name="%s"; filename="%s"' % (key, filename))
                payload.append('Content-Type: %s' % content_type)
                payload.append('')
                payload.append(value)

        payload.append('--%s--' % FILE_BOUNDARY)
        payload.append('')
        body = CRLF.join(payload)
        content_type = 'multipart/form-data; boundary=%s' % FILE_BOUNDARY
        return content_type, body

    def _get_content_type(self, filename):
        return mimetypes.guess_type(filename)[0] or 'application/octet-stream'

    def request(self, files=None, **params):
        if 'auth' not in params:
            params['auth'] = {
                'key': self.key,
                'expires': (datetime.now() +
                    timedelta(days=1)).strftime('%Y/%m/%d %H:%M:%S')
            }

        fields = {
            'params': json.dumps(params),
            'signature': self._sign_request(params)
        }

        return self._send_request(files, **fields)
