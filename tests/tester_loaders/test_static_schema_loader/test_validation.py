import pytest
from django.core.exceptions import ImproperlyConfigured
from django.test import override_settings

from openapi_tester.configuration import SwaggerTesterSettings
from openapi_tester.loaders import StaticSchemaLoader
from tests import yml_path


def test_static_schema_loader_validation(monkeypatch):
    """
    Verify that validation runs successfully for the demo project.
    """
    with override_settings(RESPONSE_TESTER={'PATH': yml_path, 'SCHEMA_LOADER': StaticSchemaLoader}):
        settings = SwaggerTesterSettings()
        assert settings.loader_class.path == yml_path


def test_missing_path(monkeypatch):
    """
    Verify that validation runs successfully for the demo project.
    """
    with override_settings(RESPONSE_TESTER={'SCHEMA_LOADER': StaticSchemaLoader}):
        with pytest.raises(
            ImproperlyConfigured,
            match='PATH is required to load static OpenAPI schemas. Please add PATH to the RESPONSE_TESTER settings',
        ):
            SwaggerTesterSettings().validate()


def test_bad_path_type(monkeypatch):
    """
    Verify that validation runs successfully for the demo project.
    """
    with override_settings(RESPONSE_TESTER={'PATH': 2, 'SCHEMA_LOADER': StaticSchemaLoader}):
        with pytest.raises(
            ImproperlyConfigured, match='`PATH` needs to be a string. Please update your RESPONSE_TESTER settings.'
        ):
            SwaggerTesterSettings().validate()
