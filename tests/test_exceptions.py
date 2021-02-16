from openapi_tester.exceptions import CaseError, DocumentationError
from openapi_tester.schema_tester import Instance


def test_documentation_error_message():
    instance = Instance(
        schema_section={
            "title": "object_type_title",
            "type": "object",
            "properties": {
                "key2": {
                    "description": "This is a string type",
                    "type": "string",
                },
                "key3": {
                    "description": "This is a string type",
                    "type": "string",
                },
                "key1": {
                    "description": "This is a string type",
                    "type": "string",
                },
                "key4": {"type": "array", "items": {"type": "integer"}},
            },
        },
        data={"key3": "test", "key2": "test", "key1": "test", "key4": [1, 2, 3]},
        reference="test:reference",
        version=30,
    )
    error = DocumentationError(
        message="Test error message",
        instance=instance,
        hint="test:hint",
    )

    expected = """
Test error message

Expected: {key1: str, key2: str, key3: str, key4: [int]}

Received: {"key1": "test", "key2": "test", "key3": "test", "key4": [1, 2, 3]}

Hint: test:hint

Sequence: test:reference
"""
    assert error.args[0].strip() == expected.strip()


def test_case_error_message():
    error = CaseError(key="test-key", case="camelCase", expected="testKey")
    assert error.args[0].strip() == "The response key `test-key` is not properly camelCase. Expected value: testKey"
