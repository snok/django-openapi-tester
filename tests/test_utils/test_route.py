import pytest

from response_tester.route import Route
from response_tester.utils import resolve_path


def test_route_initialization():
    route = Route(*resolve_path('/api/v1/cars/correct'))
    assert route.deparameterized_path == '/api/{version}/cars/correct'
    assert route.parameterized_path == route.deparameterized_path
    assert route.counter == 0
    assert route.parameters == ['{version}']
    assert route.resolved_path.kwargs == {'version': 'v1'}


def test_route_iteration():
    route = Route(*resolve_path('/api/v1/cars/correct'))
    assert route.parameterized_path == '/api/{version}/cars/correct'
    assert route.get_path() == '/api/{version}/cars/correct'
    assert route.get_path() == '/api/v1/cars/correct'
    route.reset()
    assert route.parameterized_path == '/api/{version}/cars/correct'


def test_route_matches():
    route = Route(*resolve_path('/api/v1/cars/correct'))
    assert route.route_matches('/api/{version}/cars/correct') is True
    assert route.route_matches('/api/v1/cars/correct') is True


def test_route_iteration_index_error():
    route = Route(*resolve_path('/api/v1/cars/correct'))
    assert route.parameterized_path == '/api/{version}/cars/correct'
    assert route.get_path() == '/api/{version}/cars/correct'
    assert route.get_path() == '/api/v1/cars/correct'
    with pytest.raises(IndexError, match='No more parameters to insert'):
        route.get_path()
