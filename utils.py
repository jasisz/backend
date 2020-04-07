from datetime import datetime
from typing import List

from flask import Request
from google.cloud import datastore
from google.cloud.datastore import Entity

DATASTORE_KIND_USERS = "Users"
ENCOUNTER_UPLOADS_DATASTORE_KIND = "Encounter Uploads"

KEY_USER_ID = "user_id"
KEY_PLATFORM = "platform"
KEY_OS_VERSION = "os_version"
KEY_DEVICE_TYPE = "device_type"
KEY_APP_VERSION = "app_version"
KEY_LANG = "lang"

datastore_client = datastore.Client()


class InvalidRequestException(Exception):
    def __init__(self, status, response):
        self.status = status
        self.response = response


class ExtraParam:
    def __init__(self, name, allow_empty=False):
        self.name = name
        self.allow_empty = allow_empty


def get_request_data(request: Request) -> dict:
    if not request.is_json:
        raise InvalidRequestException(422, {"status": "failed", "message": "invalid data"})

    return request.get_json()


def validate_request_parameters(request_data: dict, extra_params: List[ExtraParam] = None) -> None:
    for key in [KEY_USER_ID, KEY_PLATFORM, KEY_OS_VERSION, KEY_DEVICE_TYPE, KEY_APP_VERSION, KEY_LANG]:
        if key not in request_data:
            raise InvalidRequestException(422, {"status": "failed", "message": f"missing field: {key}"})
        if not request_data[key]:
            raise InvalidRequestException(422, {"status": "failed", "message": f"empty field: {key}"})

    for param in extra_params:
        if param.name not in request_data:
            raise InvalidRequestException(422, {"status": "failed", "message": f"missing field: {key}"})
        if not param.allow_empty and not request_data[param.name]:
            raise InvalidRequestException(422, {"status": "failed", "message": f"empty field: {key}"})


def get_user_from_datastore(user_id: str) -> Entity:
    key = datastore_client.key(DATASTORE_KIND_USERS, f"{user_id}")
    user_entity = datastore_client.get(key=key)
    if not user_entity:
        raise InvalidRequestException(401, {"status": "failed", "message": f"Unauthorized"})
    return user_entity


def update_user_in_datastore(
    entity: Entity, platform: str, os_version: str, app_version: str, device_type: str, lang: str
) -> None:
    entity.update(
        {
            "platform": platform,
            "os_version": os_version,
            "app_version": app_version,
            "device_type": device_type,
            "lang": lang,
            "last_status_requested": datetime.utcnow(),
        }
    )
    datastore_client.put(entity)
