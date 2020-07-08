from rest_framework.views import exception_handler
from rest_framework import status
from rest_framework.exceptions import APIException


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        response.data['status_code'] = response.status_code

    return response


class CustomValidation(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'サーバーで問題が発生しています。'

    def __init__(self, detail, status_code):
        if status_code is not None:
            self. status_code = status_code
        if detail is not None:
            self.detail = detail
        else:
            self.detail = self.default_detail
