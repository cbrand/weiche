from typing import Any

from pydantic import RootModel, ValidationError

from schiene_next.objects import Association, ConnectionResponse, Location


def parse_locations(payload: list[Any]) -> list[Location]:
    return RootModel[list[Location]].model_validate(payload, by_alias=True).root


def parse_connection_response(payload: dict[str, Any]) -> ConnectionResponse:
    try:
        return ConnectionResponse.model_validate(payload, by_alias=True)
    except ValidationError as e:
        raise e


def parse_associations(payload: list[Any]) -> list[Association]:
    return RootModel[list[Association]].model_validate(payload, by_alias=True).root
