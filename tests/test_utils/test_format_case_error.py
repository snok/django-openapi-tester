from django_swagger_tester.exceptions import CaseError
from django_swagger_tester.utils import format_response_tester_case_error

case_error = CaseError(key='IP', case='camel case', origin='middleware')


def test_format_response_tester_case_error():
    assert (
        format_response_tester_case_error(case_error)
        == '''The property `IP` is not properly camel case

If this is intentional, you can skip case validation by adding `ignore_case=['IP']` to the `validate_response` function call, or by adding the key to the CASE_WHITELIST in the SWAGGER_TESTER settings'''
    )