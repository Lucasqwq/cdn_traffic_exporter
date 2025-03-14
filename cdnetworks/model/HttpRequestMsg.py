import json
from urllib.parse import urlparse
from Constant.Constant import Constant


class HttpRequestMsg:
    def __init__(self):
        self.uri = None
        self.url = None
        self.host = None
        self.method = None
        self.protocol = None
        self.params = {}
        self.headers = {}
        self.body = None
        self.signed_headers = None
        self.msg = None

        self.put_header('Content-Type', Constant.APPLICATION_JSON)
        self.put_header(Constant.X_CNC_AUTH_METHOD, Constant.AUTH_METHOD)

    def put_param(self, name, value):
        self.params[name] = value

    def get_param(self, name):
        return self.params.get(name)

    def get_query_string(self):
        if self.method == 'POST' or not self.uri:
            return ''
        parsed_url = urlparse(self.uri)
        return parsed_url.query

    def put_header(self, name, value):
        self.headers[name.lower()] = value

    def get_header(self, name):
        return self.headers.get(name.lower())

    def get_header_any(self, *names):
        for name in names:
            value = self.get_header(name)
            if value is not None:
                return value
        return None

    def remove_header(self, name):
        key_to_remove = name.lower()
        if key_to_remove in self.headers:
            del self.headers[key_to_remove]

    def set_json_body(self, obj):
        self.body = json.dumps(obj)
