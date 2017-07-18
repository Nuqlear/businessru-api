# coding: utf-8


class InvalidToken(Exception):

    def __init__(self, method, url):
        message = u'{} {} returned 401 (seems like token is invalid)'.format(method, url)


class ResponseNotValidated(Exception):

    def __init__(self, method, url):
        message = u'{} {} response is not validated'.format(method, url)
        super(ResponseNotValidated, self).__init__(message)


class UnexpectedResponse(Exception):

    def __init__(self, method, url, status_code):
        message = u'{} {} returned {}'.format(method, url, status_code)
        super(UnexpectedResponse, self).__init__(message)


class UnknownHTTPMethod(Exception):

    def __init__(self, method):
        message = u'{} is unknown HTTP method'.format(method)
        super(UnknownHTTPMethod, self).__init__(message)


class EndpointNotFound(Exception):

    def __init__(self, method, url):
        message = u'{} {} returned 405 (seems like endpoint is not found)'.format(method, url)
        super(EndpointNotFound, self).__init__(message)


class BusinessruResponseError(Exception):

    def __init__(self, error_code, error_text):
        message = u'Business.ru response data has status=error. {} {}'.format(error_code,
                                                                              error_text)
        super(BusinessruResponseError, self).__init__(message)


class TooManyRequests(Exception):

    def __init__(self, method, url):
        message = u'{} {} returned 504 (seems like too many requests)'.format(method, url)
        super(TooManyRequests, self).__init__()
