.. raw:: html

    <p align="center">
        <h1 align="center">Django Swagger Tester</h1>
    </p>
    <p align="center">
      <em>A Django test utility for validating Swagger documentation</em>
    </p>


.. raw:: html

    <p align="center">
    <a href="https://pypi.org/project/django-swagger-tester/">
        <img src="https://img.shields.io/pypi/v/django-swagger-tester.svg" alt="Package version">
    </a>
    <a href="https://django-swagger-tester.readthedocs.io/en/latest/?badge=latest">
        <img src="https://readthedocs.org/projects/django-swagger-tester/badge/?version=latest" alt="Documentation status">
    </a>
    <a href="https://codecov.io/gh/snok/django-swagger-tester">
        <img src="https://codecov.io/gh/snok/django-swagger-tester/branch/master/graph/badge.svg" alt="Code coverage">
    </a>
    <a href="https://pypi.org/project/django-swagger-tester/">
        <img src="https://img.shields.io/badge/python-3.6%2B-blue" alt="Supported Python versions">
    </a>
    <a href="https://pypi.python.org/pypi/django-swagger-tester">
        <img src="https://img.shields.io/badge/django%20versions-2.2%2B-blue" alt="Supported Django versions">
    </a>
    </p>
    <p align="center">
    <a href="https://pypi.org/project/django-swagger-tester/">
        <img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Code style Black">
    </a>
    <a href="http://mypy-lang.org/">
        <img src="http://www.mypy-lang.org/static/mypy_badge.svg" alt="Checked with mypy">
    </a>
    <a href="https://github.com/pre-commit/pre-commit">
        <img src="https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white" alt="Pre-commit enabled">
    </a>
    </p>

--------------


**Documentation**: `https://django-swagger-tester.readthedocs.io <https://django-swagger-tester.readthedocs.io/en/latest/?badge=latest>`_

**Repository**: `https://github.com/snok/django-swagger-tester <https://github.com/snok/django-swagger-tester>`_

--------------

Django Swagger Tester
=====================

Django Swagger Tester is a simple test utility for validating your Django Swagger documentation.

Its aim is to make it easy for developers to catch and correct documentation errors in their Swagger/OpenAPI docs.

Given a test-example:

.. code-block:: python

    {
      "id": 0,
      "category": {
        "id": 0,
        "name": "string"
      },
      "name": "doggie",
      "photoUrls": [
        "string"
      ],
      "tags": [
        {
          "id": 0,
          "name": "string"
        }
      ],
      "status": "available"
    }

your brain shouldn't have to manually scan this response documentation for errors

.. code-block:: python

  "responses": {
    "200": {
      "description": "successful operation",
      "schema": {
        "type": "object",
        "required": [
          "name",
          "photoUrls"
        ],
        "properties": {
          "id": {
            "type": "integer",
            "format": "int64"
          },
          "category": {
            "type": "object",
            "properties": {
              "id": {
                "type": "integer",
                "format": "int64"
              },
              "name": {
                "type": "string"
              }
            },
            "xml": {
              "name": "Category"
            }
          },
          "name": {
            "type": "string",
            "example": "doggie"
          },
          "photoUrl": {
            "type": "array",
            "xml": {
              "wrapped": true
            },
            "items": {
              "type": "string",
              "xml": {
                "name": "photoUrl"
              }
            }
          },
          "tags": {
            "type": "array",
            "xml": {
              "wrapped": true
            },
            "items": {
              "type": "object",
              "properties": {
                "id": {
                  "type": "integer",
                  "format": "int64"
                },
                "name": {
                  "type": "string"
                }
              },
              "xml": {
                "name": "Tag"
              }
            }
          },
          "status": {
            "type": "string",
            "description": "pet status in the store",
            "enum": [
              "available",
              "pending",
              "sold"
            ]
          }
        },
        "xml": {
          "name": "Pet"
        }
      }
    }
  }

when automated tests can simply tell you that ``photoUrls`` is missing a letter.

Features
--------

The package has two primary features:

-  `Testing response documentation`_
-  `Testing request body documentation`_

Support for other use cases could be added in the future, and contributions are welcome.

Implementations
---------------

This package currently supports:

- Testing of dynamically rendered OpenAPI schemas using `drf-yasg`_
- Testing of dynamically rendered OpenAPI schemas using `drf-spectacular`_
- Testing any implementation which generates a static yaml or json file (e.g., like `DRF`_)


If you're using another method to generate your documentation and would like to use this package, feel free to add an issue, or create a PR. Adding a new implementation is as easy as adding the required logic needed to load the OpenAPI schema.

Installation
============

Install using pip:

.. code:: python

   pip install django-swagger-tester

Configuration
=============

Settings
--------

To use Django Swagger Settings in your project, you first need to add a ``django_swagger_tester`` to your installed apps.

.. code:: python

    INSTALLED_APPS = [
        ...
        'django_swagger_tester',
    ]

Secondly, you need to configure the ``SWAGGER_TESTER`` package settings in your ``settings.py``:

.. code:: python

    from django_swagger_tester.loaders import DrfSpectacularSchemaLoader
    from django_swagger_tester.case_testers import is_camel_case

    SWAGGER_TESTER = {
        'SCHEMA_LOADER': DrfSpectacularSchemaLoader,
        'CASE_TESTER': is_camel_case,
        'CAMEL_CASE_PARSER': True,
        'CASE_PASSLIST': ['IP', 'DHCP'],
        'MIDDLEWARE': {
            'RESPONSE_VALIDATION': {
                'LOG_LEVEL': 'ERROR',
                'LOGGER_NAME': 'middleware_response_validation',
                'VALIDATION_EXEMPT_URLS': ['^api/v1/exempt-endpoint$'],
                'VALIDATION_EXEMPT_STATUS_CODES': [401],
                'DEBUG': True,
            }
        },
        'VIEWS': {
            'RESPONSE_VALIDATION': {
                'LOG_LEVEL': 'ERROR',
                'LOGGER_NAME': 'view_response_validation',
                'DEBUG': True,
            }
        },
    }

The only required setting, is the schema loader class.

Parameters
----------

To learn more about setting parameters, see the `parameter docs`_.

|
|

--------------

.. raw:: html

    <p align="center">
        <b>Please Note</b>
    </p>
    <p align="center">
        The following sections contain simplified versions of the
        <a href="https://django-swagger-tester.readthedocs.io/">docs</a>.
        They are included to give you a quick indication of how the package functions.
    </p>
    <p align="center">
        If you decide to implement Django Swagger Tester functions, it's better to read the <a href="https://django-swagger-tester.readthedocs.io/">docs</a>.
    </p>

--------------

|

Response Validation
===================

There are three ways to verify that your API responses match your documented responses:

1. Add static tests for each endpoint, method, and status code
2. Implement live testing for your project (middleware)
3. Implement live testing for individual views (inherit ResponseValidation in place of an APIView)

Static testing
--------------

A pytest implementation might look like this:

.. code:: python

    from django_swagger_tester.testing import validate_response

    def test_200_response_documentation(client):
        route = 'api/v1/test/1'
        response = client.get(route)
        assert response.status_code == 200
        assert response.json() == expected_response

        # test swagger documentation
        validate_response(response=response, method='GET', route=route)

A Django-test implementation might look like this:

.. code-block:: python

    from django_swagger_tester.testing import validate_response

    class MyApiTest(APITestCase):

        path = '/api/v1/test/'

        def setUp(self) -> None:
            user, _ = User.objects.update_or_create(username='test_user')
            self.client.force_authenticate(user=user)

        def test_get_200(self) -> None:
            response = self.client.get(self.path, headers={'Content-Type': 'application/json'})
            expected_response = [...]

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), expected_response)

            # test swagger documentation
            validate_response(response=response, method='GET', route=self.path)

It is also possible to test more than a single response at the time:

.. code:: python

    def test_post_endpoint_responses(client):
        # 201 - Resource created
        response = client.post(...)
        validate_response(response=response, method='POST', route='api/v1/test/')

        # 400 - Bad data
        response = client.post(...)
        validate_response(response=response, method='POST', route='api/v1/test/')

    def test_get_endpoint_responses(client):
        # 200 - Fetch resource
        response = client.get(...)
        validate_response(response=response, method='GET', route='api/v1/test/<id>')

        # 404 - Bad ID
        response = client.get(...)
        validate_response(response=response, method='GET', route='api/v1/test/<bad id>')

Live testing with a middleware
------------------------------

If you want to implement response validation for all outgoing API responses, simply add the middleware to your settings.py:

.. code:: python

    MIDDLEWARE = [
        ...
        'django_swagger_tester.middleware.ResponseValidationMiddleware',
    ]

The middleware validates all outgoing responses with the ``application/json`` content-type. Any errors/inconsistencies are then logged using a settings-specified log-level.

To avoid validating the same responses over and over, the results are cached to a database table, making sure we only validate a response once. Two responses from the same endpoint *can* trigger duplicate validation, but only if the response structure has changed, i.e., the type of a response attribute has changed.

Live testing for a single view
------------------------------

If you're using DRF's ``APIView``, you can replace that with ``django_swagger_tester.views.ResponseValidationView``, to add response validation before a response is returned to the user.

If you're not using ``APIView``, but some closely related solution, you can very easily make your own response validation class. Just have a look at the ``ResposeValidationView`` for inspiration.

Error messages
--------------

When found, errors will be raised in the following format:

.. code-block:: shell

    django_swagger_tester.exceptions.SwaggerDocumentationError: Item is misspecified:

    Summary
    -------------------------------------------------------------------------------------------

    Error:      The following properties seem to be missing from your response body: length, width.

    Expected:   {'name': 'Saab', 'color': 'Yellow', 'height': 'Medium height', 'width': 'Very wide', 'length': '2 meters'}
    Received:   {'name': 'Saab', 'color': 'Yellow', 'height': 'Medium height'}

    Hint:       Remove the key(s) from you Swagger docs, or include it in your API response.
    Sequence:   init.list

    -------------------------------------------------------------------------------------------

    * If you need more details: set `verbose=True`

- ``Expected`` describes the response data
- ``Received`` describes the schema.
- ``Hint`` will sometimes include a suggestion for what actions to take, to correct an error.
- ``Sequence`` will indicate how the response tester iterated through the data structure, before finding the error.

In this example, the response data is missing two attributes, ``height`` and ``width``, documented in the OpenAPI schema indicating that either the response needs to include more data, or that the OpenAPI schema should be corrected. It might be useful to highlight that we can't be sure whether the response or the schema is wrong; only that they are inconsistent.


Input Validation
================

To make sure your request body documentation is accurate, and will stay accurate, you can use endpoint serializers to validate your schema directly.

``validate_input_serializer`` constructs an example representation of the documented request body, and passes it to the serializer it is given. This means it's only useful if you use serializers for validating your incoming request data.

A Django test implementation of input validation for a whole project could be structured like this:

.. code:: python

    from django.test import SimpleTestCase
    from django_swagger_tester.testing import validate_input_serializer

    from api.serializers.validation.request_bodies import ...


    class TestSwaggerInput(SimpleTestCase):
        endpoints = [
            {
                'api/v1/orders/': [
                    ('POST', ValidatePostOrderBody),
                    ('PUT', ValidatePutOrderBody),
                    ('DELETE', ValidateDeleteOrderBody)
                ]
            },
            {
                'api/v1/orders/<id>/entries/': [
                    ('POST', ValidatePostEntryBody),
                    ('PUT', ValidatePutEntryBody),
                    ('DELETE', ValidateEntryDeleteBody)
                ]
            },
        ]

        def test_swagger_input(self) -> None:
            """
            Verifies that the documented request bodies are valid.
            """
            for endpoint in self.endpoints:
                for route, values in endpoint.items():
                    for method, serializer in values:
                        validate_input_serializer(serializer=serializer, method=method, route=route)

.. _`https://django-swagger-tester.readthedocs.io/`: https://django-swagger-tester.readthedocs.io/en/latest/?badge=latest
.. _Testing response documentation: https://django-swagger-tester.readthedocs.io/en/latest/implementation.html#response-validation
.. _Testing input documentation: https://django-swagger-tester.readthedocs.io/en/latest/implementation.html#input-validation
.. _ensuring your docs comply with a single parameter naming standard (case type): https://django-swagger-tester.readthedocs.io/en/latest/implementation.html#case-checking
.. _drf_yasg: https://github.com/axnsan12/drf-yasg
.. _documentation: https://django-swagger-tester.readthedocs.io/
.. _docs: https://django-swagger-tester.readthedocs.io/
.. _drf: https://www.django-rest-framework.org/topics/documenting-your-api/#generating-documentation-from-openapi-schemas
.. _drf-yasg: https://github.com/axnsan12/drf-yasg
.. _drf-spectacular: https://github.com/tfranzel/drf-spectacular
.. _parameter docs: https://django-swagger-tester.readthedocs.io/en/latest/configuration.html#parameters
.. _Testing request body documentation: https://django-swagger-tester.readthedocs.io/en/latest/implementation.html#input-validation
