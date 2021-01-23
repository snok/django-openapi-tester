from __future__ import annotations

from collections.abc import Callable, KeysView
from typing import Any, Optional, Union, cast

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from rest_framework.response import Response
from rest_framework.test import APITestCase

from openapi_tester import type_declarations as td
from openapi_tester.constants import OPENAPI_PYTHON_MAPPING
from openapi_tester.exceptions import DocumentationError, UndocumentedSchemaSectionError
from openapi_tester.loaders import DrfSpectacularSchemaLoader, DrfYasgSchemaLoader, StaticSchemaLoader


class SchemaTester:
    """ SchemaTester class """

    def __init__(
        self,
        case_tester: Optional[Callable[[str], None]] = None,
        ignore_case: Optional[list[str]] = None,
        schema_file_path: Optional[str] = None,
    ) -> None:
        """
        Iterates through an OpenAPI schema objet and an API response/request object to check that they match at every level.

        :param schema: Response/request OpenAPI schema section
        :param data: API response/request data
        :raises: openapi_tester.exceptions.DocumentationError or ImproperlyConfigured
        """
        self.case_tester = case_tester
        self.ignore_case = ignore_case or []

        if schema_file_path is not None:
            self.loader = StaticSchemaLoader(schema_file_path)  # type: ignore
        elif 'drf_spectacular' in settings.INSTALLED_APPS:
            self.loader = DrfSpectacularSchemaLoader()  # type: ignore
        elif 'drf_yasg' in settings.INSTALLED_APPS:
            self.loader = DrfYasgSchemaLoader()  # type: ignore
        else:
            raise ImproperlyConfigured('No loader is configured.')

    def _test_key_casing(
        self, key: str, case_tester: Optional[Callable[[str], None]] = None, ignore_case: Optional[list[str]] = None
    ) -> None:
        tester = case_tester or getattr(self, 'case_tester', None)
        ignore_case = [*self.ignore_case, *(ignore_case or [])]
        if tester and key not in ignore_case:
            tester(key)

    @staticmethod
    def handle_all_of(**kwargs: dict) -> dict:
        properties: dict[str, Any] = {}
        for entry in kwargs.pop('allOf'):
            for key, value in entry['properties'].items():
                if key in properties:
                    if isinstance(value, dict):
                        properties[key] = {**properties[key], **value}
                    elif isinstance(value, list):
                        properties[key] = [*properties[key], *value]
                    else:
                        properties[key] = value
                else:
                    properties[key] = value
        return {**kwargs, 'type': 'object', 'properties': properties}

    @staticmethod
    def _check_openapi_type(schema_type: str, value: Any) -> bool:
        if schema_type == 'boolean':
            return isinstance(value, bool)
        if schema_type in ['string', 'file']:
            return isinstance(value, str)
        if schema_type == 'integer':
            return isinstance(value, int)
        if schema_type == 'number':
            return isinstance(value, (int, float))
        if schema_type == 'object':
            return isinstance(value, dict)
        if schema_type == 'array':
            return isinstance(value, list)

    @staticmethod
    def _get_key_value(schema: dict, key: str, error_addon: str = '') -> dict:
        """
        Indexes schema by string variable.

        :param schema: Schema to index
        :param key: Variable to index by
        :param error_addon: Additional error info to be included in the printed error message
        :return: Indexed schema
        :raises: IndexError
        """
        try:

            return schema[key]
        except KeyError:
            raise UndocumentedSchemaSectionError(
                f'Error: Unsuccessfully tried to index the OpenAPI schema by `{key}`. {error_addon}'
            )

    def _route_error_text_addon(self, paths: KeysView) -> str:
        route_error_text = ''
        pretty_routes = '\n\t• '.join(paths)
        route_error_text += f'\n\nFor debugging purposes, other valid routes include: \n\n\t• {pretty_routes}'
        return route_error_text

    @staticmethod
    def _method_error_text_addon(methods: KeysView) -> str:
        return f'\n\nAvailable methods include: {", ".join(method.upper() for method in methods if method.upper() != "PARAMETERS")}.'

    @staticmethod
    def _responses_error_text_addon(status_code: Union[int, str], response_status_codes: KeysView) -> str:
        return f'\n\nDocumented responses include: {", ".join(response_status_codes)}. Is the `{status_code}` response documented?'

    def get_response_schema_section(self, response: td.Response) -> dict:
        """
        Indexes schema by url, HTTP method, and status code to get the schema section related to a specific response.

        :param response: DRF Response Instance
        :return Response schema
        """
        path = response.request['PATH_INFO']
        method = response.request['REQUEST_METHOD']
        status_code = str(response.status_code)

        schema = self.loader.get_schema()
        parameterized_path = self.loader.parameterize_path(path)

        paths_object = self._get_key_value(schema=schema, key='paths')
        route_object = self._get_key_value(
            schema=paths_object,
            key=parameterized_path,
            error_addon=self._route_error_text_addon(paths_object.keys()),
        )
        method_object = self._get_key_value(
            schema=route_object, key=method.lower(), error_addon=self._method_error_text_addon(route_object.keys())
        )
        responses_object = self._get_key_value(schema=method_object, key='responses')
        status_code_object = self._get_key_value(
            schema=responses_object,
            key=status_code,
            error_addon=self._responses_error_text_addon(status_code, responses_object.keys()),
        )
        if 'openapi' in schema:
            content_object = self._get_key_value(schema=status_code_object, key='content')
            json_object = self._get_key_value(schema=content_object, key='application/json')
            return self._get_key_value(schema=json_object, key='schema')
        else:
            # openapi 2.0, i.e. "swagger" has a different structure than openapi 3.0 status sub-schemas
            return self._get_key_value(schema=status_code_object, key='schema')

    def test_schema_section(
        self,
        schema_section: dict,
        data: Any,
        reference: str,
        case_tester: Optional[Callable[[str], None]] = None,
        ignore_case: Optional[list[str]] = None,
    ) -> None:
        """
        This method orchestrates the testing of a schema section
        """

        if 'allOf' in schema_section:
            merged_schema = self.handle_all_of(**schema_section)
            schema_section = merged_schema

        schema_section_type = schema_section['type']

        if data is None and self.is_nullable(schema_section):
            return
        if data is None or not self._check_openapi_type(schema_section_type, data):
            raise DocumentationError(
                message=f'Mismatched types, expected {OPENAPI_PYTHON_MAPPING[schema_section_type]} but received {type(data).__name__}.',
                response=data,
                schema=schema_section,
                reference=reference,
            )
        if schema_section_type == 'object':
            if 'properties' in schema_section:
                properties = schema_section['properties']
            elif 'additionalProperties' in schema_section:
                properties = {'': schema_section['additionalProperties']}
            else:
                # FIXME: temporary
                properties = {}
            response_keys = data.keys()
            schema_section_keys = properties.keys()

            if len(schema_section_keys) != len(response_keys):
                if len(response_keys) > len(schema_section_keys):
                    missing_keys = ', '.join(
                        f'`{key}`' for key in sorted(list(set(response_keys) - set(schema_section_keys)))
                    )
                    hint = 'Add the key(s) to your OpenAPI docs, or stop returning it in your view.'
                    message = f'The following properties seem to be missing from your documentation: {missing_keys}.'
                else:
                    missing_keys = ', '.join(
                        f'{key}' for key in sorted(list(set(schema_section_keys) - set(response_keys)))
                    )
                    hint = 'Remove the key(s) from your OpenAPI docs, or include it in your API response.'
                    message = f'The following properties are missing from the tested data: {missing_keys}.'
                raise DocumentationError(
                    message=message,
                    response=data,
                    schema=schema_section,
                    reference=reference,
                    hint=hint,
                )

            for schema_key, response_key in zip(schema_section_keys, response_keys):
                self._test_key_casing(schema_key, case_tester, ignore_case)
                self._test_key_casing(response_key, case_tester, ignore_case)
                if schema_key not in response_keys:
                    raise DocumentationError(
                        message=f'Schema key `{schema_key}` was not found in the tested data.',
                        response=data,
                        schema=schema_section,
                        reference=reference,
                        hint='You need to add the missing schema key to the response, or remove it from the documented response.',
                    )
                if response_key not in schema_section_keys:
                    raise DocumentationError(
                        message=f'Key `{response_key}` not found in the OpenAPI schema.',
                        response=data,
                        schema=schema_section,
                        reference=reference,
                        hint='You need to add the missing schema key to your documented response, or stop returning it in your API.',
                    )

                schema_value = properties[schema_key]
                response_value = data[schema_key]
                self.test_schema_section(
                    schema_section=schema_value,
                    data=response_value,
                    reference=f'{reference}.dict:key:{schema_key}',
                    case_tester=case_tester,
                    ignore_case=ignore_case,
                )
        elif schema_section_type == 'array':
            items = schema_section['items']
            if not items and data is not None:
                raise DocumentationError(
                    message='Mismatched content. Response array contains data, when schema is empty.',
                    response=data,
                    schema=schema_section,
                    reference=reference,
                    hint='Document the contents of the empty dictionary to match the response object.',
                )

            for datum in data:
                self.test_schema_section(
                    schema_section=items,
                    data=datum,
                    reference=f'{reference}.list',
                    case_tester=case_tester,
                    ignore_case=ignore_case,
                )

    @staticmethod
    def is_nullable(schema_item: dict) -> bool:
        """
        Checks if the item is nullable.

        OpenAPI 3 ref: https://swagger.io/docs/specification/data-models/data-types/#null
        OpenApi 2 ref: https://help.apiary.io/api_101/swagger-extensions/

        :param schema_item: schema item
        :return: whether or not the item can be None
        """
        openapi_schema_3_nullable = 'nullable'
        swagger_2_nullable = 'x-nullable'
        return any(
            nullable_key in schema_item and schema_item[nullable_key]
            for nullable_key in [openapi_schema_3_nullable, swagger_2_nullable]
        )

    def validate_response(
        self,
        response: td.Response,
        case_tester: Optional[Callable[[str], None]] = None,
        ignore_case: Optional[list[str]] = None,
    ):
        """
        Verifies that an OpenAPI schema definition matches an API response.

        :param response: The HTTP response
        :param case_tester: Optional Callable that checks a string's casing
        :param ignore_case: List of strings to ignore when testing the case of response keys
        :raises: ``openapi_tester.exceptions.DocumentationError`` for inconsistencies in the API response and schema.
                 ``openapi_tester.exceptions.CaseError`` for case errors.
        """

        if not isinstance(response, Response):
            raise ValueError('expected response to be an instance of DRF Response')

        response_schema = self.get_response_schema_section(response)
        self.test_schema_section(
            schema_section=response_schema,
            data=response.json(),
            reference='init',
            case_tester=case_tester,
            ignore_case=ignore_case,
        )

    def test_case(self) -> APITestCase:
        validate_response = self.validate_response

        def assert_response(
            response: td.Response,
            case_tester: Optional[Callable[[str], None]] = None,
            ignore_case: Optional[list[str]] = None,
        ) -> None:
            """
            Assert response matches the OpenAPI spec.
            """
            validate_response(response=response, case_tester=case_tester, ignore_case=ignore_case)

        return cast(APITestCase, type('OpenAPITestCase', (APITestCase,), {'assertResponse': assert_response}))
