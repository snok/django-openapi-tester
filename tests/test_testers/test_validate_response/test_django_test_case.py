from django.conf import settings as django_settings

import pytest
from tests.test_testers.test_validate_response import BAD_TEST_DATA, GOOD_TEST_DATA
from tests.test_testers.test_validate_response.test_static import yml_path

from django_swagger_tester.loaders import StaticSchemaLoader
from django_swagger_tester.testing import OpenAPITestCase


def test_django_test_case(client, monkeypatch, transactional_db) -> None:  # noqa: TYP001
    """
    Asserts that the assertResponse method of the test case validates correct schemas successfully.
    """
    monkeypatch.setattr(django_settings, 'SWAGGER_TESTER', {'PATH': yml_path, 'SCHEMA_LOADER': StaticSchemaLoader})
    test_case = OpenAPITestCase()
    for item in GOOD_TEST_DATA:
        route = f"/api/v1{item['url']}"
        response = client.get(route)  # type: ignore
        assert response.status_code == 200
        # path and method explicitly pass by the user
        test_case.assertResponse(response=response, method='GET', route=route)
        # path and method inferred
        test_case.assertResponse(response=response)

    for item in BAD_TEST_DATA:
        route = f"/api/v1{item['url']}"
        with pytest.raises(Exception):
            response = client.get(route)  # type: ignore
            assert response.status_code == 400
            # path and method explicitly pass by the user
            with pytest.raises(AssertionError):
                test_case.assertResponse(response=response, method='GET', route=route)
                # path and method inferred
            with pytest.raises(AssertionError):
                test_case.assertResponse(response=response)
