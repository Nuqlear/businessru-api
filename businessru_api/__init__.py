# coding: utf-8
import hashlib
import requests
import json
import logging
from collections import OrderedDict
from functools import partial
from time import sleep

from .exceptions import (
    InvalidToken,
    ResponseNotValidated,
    UnexpectedResponse,
    UnknownHTTPMethod,
    BusinessruResponseError,
    TooManyRequests,
    EndpointNotFound
)


import sys
if (sys.version_info > (3, 0)):
    from urllib.parse import urlencode
    from functools import partialmethod
    STR_TYPES = (str,)
else:
    from urllib import urlencode
    from functools import partial

    class partialmethod(partial):
        def __get__(self, instance, owner):
            if instance is None:
                return self
            return partial(self.func,
                           instance,
                           *(self.args or ()), **(self.keywords or {}))

    STR_TYPES = (str, unicode)



class BusinessruAPI(object):

    def __init__(self, account, app_id, secret, max_retry=10):
        self.base_url = 'https://{}.business.ru/api/rest/'.format(account)
        self.app_id = app_id
        self.secret = secret
        self.max_retry = max_retry
        self.logger = logging.getLogger(__name__)
        self.decoder = json.JSONDecoder(object_pairs_hook=OrderedDict)
        self.token = None
        self.repair_token()

    def _calc_md5(self, string):
        return hashlib.md5(string.encode('utf-8')).hexdigest()

    def _get_collection_base_url(self, collection):
        return '{}{}.json'.format(self.base_url, collection)

    def _get_url_with_params(self, url, options, without_token=False):
        options['app_id'] = self.app_id
        options_sorted = []

        def append_option(key, value):
            if isinstance(value, bool):
                value = '1' if value else '0'
            elif not isinstance(value, STR_TYPES):
                value = str(value)
            options_sorted.append((key, value.encode('utf-8')))

        for key in sorted(options.keys(), key=lambda k: (k.isdigit(), k)):
            value = options[key]
            if isinstance(value, list):
                for index, sub_value in enumerate(value):
                    append_option("{}[{}]".format(key, index), sub_value)
                continue
            append_option(key, value)
        params_string = urlencode(options_sorted)
        app_psw = str()
        if without_token is False:
            app_psw = self._calc_md5(self.token + self.secret + params_string)
        else:
            app_psw = self._calc_md5(self.secret + params_string)
        params_string = '{}&app_psw={}'.format(params_string, app_psw)
        return '{}?{}'.format(url, params_string)

    def _validate_response(self, response_data, without_token=False):
        app_psw = response_data.pop('app_psw', None)
        if app_psw is None:
            return False
        result_json_str = json.dumps(response_data, separators=(',', ':'))
        result_json_str = result_json_str.replace('/', '\\/')
        expected_app_psw = str()
        if without_token is False:
            expected_app_psw = self._calc_md5(self.token + self.secret + result_json_str)
        else:
            expected_app_psw = self._calc_md5(self.secret + result_json_str)
        if app_psw != expected_app_psw:
            return False
        self.token = response_data.pop('token')
        return True

    def _request_url(self, method, url, options):
        url = self._get_url_with_params(url, options)
        attrs = [method, url]
        f = getattr(requests, method.lower(), None)
        if f is None:
            raise UnknownHTTPMethod(method)
        response = f(url)
        if response.status_code == 200:
            response_data = self.decoder.decode(response.content.decode('utf-8'))
            if not self._validate_response(response_data):
                raise ResponseNotValidated(*attrs)
            if response_data['status'] == 'error':
                raise BusinessruResponseError(response_data['error_code'],
                                              response_data['error_text'])
            return response_data
        elif response.status_code == 401:
            raise InvalidToken(*attrs)
        elif response.status_code == 503:
            raise TooManyRequests(*attrs)
        elif response.status_code == 405:
            raise EndpointNotFound(*attrs)
        else:
            raise UnexpectedResponse(*(attrs + [response.status_code]))

    def _try_request_url(self, method, url, options):
        repair = False
        errors_occured = 0
        while errors_occured < self.max_retry:
            try:
                if repair is False:
                    self.logger.info('try {} {}'.format(method, url))
                    data = self._request_url(method, url, options)
                    return data
                else:
                    self.repair_token()
                    repair = False
            except (TooManyRequests, InvalidToken) as e:
                if errors_occured == self.max_retry - 1:
                    raise
                errors_occured += 1
                if isinstance(e, TooManyRequests):
                    self.logger.debug('TooManyRequests')
                    sleep(20.)
                else:
                    self.logger.debug('InvalidToken')
                    repair = True

    def repair_token(self):
        request_url = self._get_url_with_params(
            self._get_collection_base_url('repair'), {}, True)
        response = requests.get(request_url)
        if response.status_code != 200:
            if response.status_code == 503:
                raise TooManyRequests('get', request_url)
            else:
                raise UnexpectedResponse('get', request_url, response.status_code)
        response_data = response.json()
        if not self._validate_response(response_data, True):
            raise ResponseNotValidated(request_url)

    def request(self, method, collection, **kwargs):
        url = self._get_collection_base_url(collection)
        return self._try_request_url(method, url, kwargs)


for method in ('get', 'post', 'put'):
    setattr(BusinessruAPI, method, partialmethod(BusinessruAPI.request, method))
