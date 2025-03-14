import hashlib
import hmac
import time
from urllib.parse import unquote

from Constant.Constant import Constant
from exception.ApiAuthException import ApiAuthException
from model.HttpRequestMsg import HttpRequestMsg
from util.HttpUtils import HttpUtils


class AkSkAuth:
    @staticmethod
    def post(ak_sk_config, payload):
        request_msg = HttpRequestMsg()
        request_msg.uri = ak_sk_config["uri"]
        request_msg.method = "POST"
        request_msg.signed_headers = AkSkAuth.get_signed_headers(ak_sk_config["signed_headers"])
        request_msg.json_body = payload

        return AkSkAuth.invoke_with_key(request_msg, ak_sk_config["access_key"], ak_sk_config["secret_key"])

    @staticmethod
    def get(ak_sk_config):
        request_msg = HttpRequestMsg()
        request_msg.uri = ak_sk_config["uri"]
        request_msg.method = "GET"

        return AkSkAuth.invoke_with_key(request_msg, ak_sk_config["access_key"], ak_sk_config["secret_key"])

    @staticmethod
    def put(ak_sk_config, payload):
        request_msg = HttpRequestMsg()
        request_msg.uri = ak_sk_config["uri"]
        request_msg.method = "PUT"
        request_msg.signed_headers = AkSkAuth.get_signed_headers(ak_sk_config["signed_headers"])
        request_msg.json_body = payload

        return AkSkAuth.invoke_with_key(request_msg, ak_sk_config["access_key"], ak_sk_config["secret_key"])

    @staticmethod
    def delete(ak_sk_config):
        request_msg = HttpRequestMsg()
        request_msg.uri = ak_sk_config["uri"]
        request_msg.method = "DELETE"

        return AkSkAuth.invoke_with_key(request_msg, ak_sk_config["access_key"], ak_sk_config["secret_key"], ak_sk_config["custom_headers"])

    @staticmethod
    def invoke_with_key(request_msg, access_key, secret_key, custom_headers):
        try:
            AkSkAuth.get_auth_and_set_headers(request_msg, access_key, secret_key, custom_headers)
            return HttpUtils.call(request_msg)
        except Exception as e:
            raise ApiAuthException("API invoke failed.") from e

    @staticmethod
    def invoke(ak_sk_config, json_body):
        try:
            request_msg = AkSkAuth.transfer_http_request_msg(ak_sk_config, json_body)
            AkSkAuth.get_auth_and_set_headers(request_msg, ak_sk_config.access_key, ak_sk_config.secret_key, ak_sk_config.custom_headers)
            return HttpUtils.call(request_msg)
        except Exception as e:
            raise ApiAuthException("API invoke failed.") from e

    @staticmethod
    def transfer_http_request_msg(ak_sk_config, json_body):
        request_msg = HttpRequestMsg()
        request_msg.uri = ak_sk_config.uri
        if ak_sk_config.end_point and ak_sk_config.end_point != Constant.END_POINT:
            request_msg.host = ak_sk_config.end_point
            request_msg.url = f"{Constant.HTTPS_REQUEST_PREFIX}{ak_sk_config.end_point}{request_msg.uri}"

        request_msg.method = ak_sk_config.method
        request_msg.signed_headers = AkSkAuth.get_signed_headers(ak_sk_config.signed_headers)
        if ak_sk_config.method in {"POST", "PUT", "PATCH", "DELETE"}:
            request_msg.body = json_body

        return request_msg

    @staticmethod
    def get_auth_and_set_headers(request_msg, access_key, secret_key, custom_headers):
        try:
            timestamp = str(int(time.time()))
            request_msg.headers["Host"] = request_msg.host
            request_msg.headers[Constant.HEAD_SIGN_ACCESS_KEY] = access_key
            request_msg.headers[Constant.HEAD_SIGN_TIMESTAMP] = timestamp
            signature = AkSkAuth.get_signature(request_msg, secret_key, timestamp)
            authorization = AkSkAuth.gen_authorization(access_key,
                                                       AkSkAuth.get_signed_headers(request_msg.signed_headers),
                                                       signature)
            request_msg.headers["Authorization"] = authorization
            if custom_headers:
                request_msg.headers.update(custom_headers)
        except Exception as e:
            raise Exception("AK/SK get authorization failed.") from e

    @staticmethod
    def gen_authorization(access_key, signed_headers, signature):
        return f"{Constant.HEAD_SIGN_ALGORITHM} Credential={access_key}, SignedHeaders={signed_headers}, Signature={signature}"

    @staticmethod
    def get_signature(request_msg, secret_key, timestamp):
        method = request_msg.method
        body_str = request_msg.body if method in ["POST", "PUT"] and request_msg.body else ""
        hashed_request_payload = hashlib.sha256(body_str.encode()).hexdigest()
        canonical_request = f"{method}\n{request_msg.uri.split('?')[0]}\n" \
                            f"{unquote(request_msg.get_query_string())}\n" \
                            f"{AkSkAuth.get_canonical_headers(request_msg.headers, AkSkAuth.get_signed_headers(request_msg.signed_headers))}\n" \
                            f"{AkSkAuth.get_signed_headers(request_msg.signed_headers)}\n{hashed_request_payload}"
        string_to_sign = f"{Constant.HEAD_SIGN_ALGORITHM}\n{timestamp}\n{hashlib.sha256(canonical_request.encode()).hexdigest()}"
        return hmac.new(secret_key.encode(), string_to_sign.encode(), hashlib.sha256).hexdigest().lower()

    @staticmethod
    def get_canonical_headers(headers, signed_headers):
        header_names = signed_headers.split(";")
        canonical_headers = []
        for header_name in header_names:
            canonical_headers.append(f"{header_name}:{AkSkAuth.get_value_by_header(header_name, headers).lower()}\n")
        return "".join(canonical_headers)

    @staticmethod
    def get_signed_headers(signed_headers):
        if not signed_headers:
            return "content-type;host"
        headers = signed_headers.split(";")
        signed_header_set = sorted(set(header.lower() for header in headers))
        return ";".join(signed_header_set)

    @staticmethod
    def get_value_by_header(name, custom_header_map):
        for key, value in custom_header_map.items():
            if key.lower() == name.lower():
                return value
        return ''
