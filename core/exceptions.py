from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:

        # Validation errors
        if isinstance(response.data, dict):

            first_key = next(iter(response.data))
            first_error = response.data[first_key]

            if isinstance(first_error, list):
                first_error = first_error[0]

            response.data = {
                "success": False,
                "field": first_key,
                "errors": str(first_error).capitalize()
            }

        else:
            response.data = {
                "success": False,
                "errors": "Something went wrong."
            }

    return response