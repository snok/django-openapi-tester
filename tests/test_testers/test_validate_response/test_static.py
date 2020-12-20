from django.conf import settings as django_settings
from django.test import override_settings

from tests.test_testers.test_validate_response import GOOD_TEST_DATA, I18N_DATA

from django_swagger_tester.configuration import SwaggerTesterSettings
from django_swagger_tester.loaders import StaticSchemaLoader
from django_swagger_tester.testing import validate_response

yml_path = str(django_settings.BASE_DIR) + '/static_schemas/openapi-schema.yml'


def test_endpoints_static_schema(client, monkeypatch, transactional_db) -> None:  # noqa: TYP001
    """
    Asserts that the validate_response function validates correct schemas successfully.
    """
    with override_settings(SWAGGER_TESTER={'PATH': yml_path, 'SCHEMA_LOADER': StaticSchemaLoader}):
        settings = SwaggerTesterSettings()
        monkeypatch.setattr('django_swagger_tester.testing.settings', settings)
        for item in GOOD_TEST_DATA:
            url = '/api/v1' + item['url']
            response = client.get(url)
            assert response.status_code == 200
            assert response.json() == item['expected_response']
            validate_response(response=response, method='GET', route=url)


def test_i18n_endpoint(client, monkeypatch, transactional_db) -> None:
    """
    Asserts that the validate_response function validates correct schemas successfully.
    """
    with override_settings(
        SWAGGER_TESTER={'PATH': yml_path, 'SCHEMA_LOADER': StaticSchemaLoader, 'PARAMETERIZED_I18N_NAME': 'language'}
    ):
        settings = SwaggerTesterSettings()
        monkeypatch.setattr('django_swagger_tester.testing.settings', settings)
        for item in I18N_DATA:
            lang_prefix = '/' + item['lang']
            url = lang_prefix + '/api/v1' + item['url']
            response = client.get(url)
            assert response.status_code == 200
            validate_response(response=response, method='GET', route=url)
