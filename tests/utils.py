from copy import deepcopy

import yaml
from django.conf import settings as django_settings

from tests import yml_path

default_settings = django_settings.RESPONSE_TESTER
default_middleware_settings = default_settings['MIDDLEWARE']
default_middleware_response_validation_settings = default_middleware_settings['RESPONSE_VALIDATION']
default_project_middlewares = django_settings.MIDDLEWARE
default_view_settings = default_settings['VIEWS']
default_view_response_validation_settings = default_view_settings['RESPONSE_VALIDATION']


def remove_middleware():
    return default_project_middlewares[:-1]


def patch_settings(key, value) -> dict:
    patched_settings = deepcopy(default_settings)
    patched_settings[key] = value
    return patched_settings


def patch_middleware_settings(key, value) -> dict:
    patched_middleware_settings = deepcopy(default_middleware_settings)
    patched_middleware_settings[key] = value
    settings = deepcopy(default_settings)
    settings['MIDDLEWARE'] = patched_middleware_settings
    return settings


def patch_response_validation_middleware_settings(key, value) -> dict:
    patched_middleware_settings = deepcopy(default_middleware_response_validation_settings)
    patched_middleware_settings[key] = value
    middleware_settings = deepcopy(default_middleware_settings)
    middleware_settings['RESPONSE_VALIDATION'] = patched_middleware_settings
    settings = deepcopy(default_settings)
    settings['MIDDLEWARE'] = middleware_settings
    return settings


def patch_view_settings(key, value) -> dict:
    patched_view_settings = deepcopy(default_view_settings)
    patched_view_settings[key] = value
    settings = deepcopy(default_settings)
    settings['VIEWS'] = patched_view_settings
    return settings


def patch_response_validation_view_settings(key, value) -> dict:
    patched_view_settings = deepcopy(default_middleware_response_validation_settings)
    patched_view_settings[key] = value
    view_settings = deepcopy(default_middleware_settings)
    view_settings['RESPONSE_VALIDATION'] = patched_view_settings
    settings = deepcopy(default_settings)
    settings['VIEWS'] = view_settings
    return settings


class MockRoute:
    def __init__(self, x):
        self.x = x
        self.counter = 0
        self.parameters = [2, 2]

    def get_path(self):
        self.counter += 1
        if self.counter == 2:
            raise IndexError
        return self.x


def ret_schema(*args, **kwargs):
    with open(yml_path) as f:
        content = f.read()
    return yaml.load(content, Loader=yaml.FullLoader)
