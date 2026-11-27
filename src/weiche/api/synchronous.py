from datetime import datetime
from http import HTTPStatus

import ssl
import time
import requests
from requests.adapters import HTTPAdapter

from weiche.api.base import BaseApi
from weiche.api.parser import parse_associations, parse_connection_response, parse_locations
from weiche.const import DEFAULT_BASE_URL
from weiche.objects import Association, Connection, ConnectionRequest, Location


class SSLContextAdapter(HTTPAdapter):
    def __init__(self, ssl_context: ssl.SSLContext, **kwargs) -> None:
        self.ssl_context = ssl_context
        super().__init__(**kwargs)

    def init_poolmanager(self, *args, **kwargs):
        kwargs["ssl_context"] = self.ssl_context
        return super().init_poolmanager(*args, **kwargs)

    def proxy_manager_for(self, *args, **kwargs):
        kwargs["ssl_context"] = self.ssl_context
        return super().proxy_manager_for(*args, **kwargs)


class SynchronousApi(BaseApi):
    def __init__(self, base_url: str = DEFAULT_BASE_URL, proxy: str | None = None) -> None:
        super().__init__(base_url)
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.session.mount("https://", SSLContextAdapter(self.ssl_context))
        if proxy:
            self.session.proxies = {"http": proxy, "https": proxy}

    def get_travel_associations(self) -> list[Association]:
        response = self.session.get(self.travel_associations_url)
        assert response.status_code == HTTPStatus.OK, f"Error: {response.status_code}"
        return parse_associations(response.json())

    def search_locations(self, query: str, limit: int = 10, location_type: str = "ALL") -> list[Location]:
        tries = 0
        while True:
            tries += 1
            response = self.session.get(
                self.locations_url,
                params=self.get_locations_params(
                    query=query,
                    limit=limit,
                    location_type=location_type,
                ),
            )
            if response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
                time.sleep(tries)
                continue
            assert response.status_code == HTTPStatus.OK, f"Error: {response.status_code}"
            return parse_locations(response.json())

    def search_connections(
        self,
        at: datetime,
        from_location: str,
        to_location: str,
        limit: int = 10,
    ) -> list[Connection]:
        return self.search_connections_ext(
            self.get_connections_request_from_params(from_location, to_location, at),
            limit=limit,
        )

    def search_connections_ext(self, request: ConnectionRequest, limit: int = 10) -> list[Connection]:
        responses: list[Connection] = []
        tries = 0
        while len(responses) < limit:
            request_params = self.get_connections_ext_params(request)
            response = self.session.post(
                self.connections_url,
                json=request_params,
            )
            if response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
                tries += 1
                time.sleep(tries)
                continue
            tries = 0

            assert response.status_code in (
                HTTPStatus.OK,
                HTTPStatus.CREATED,
            ), f"Error: {response.status_code}, {response.text}"
            connection_response = parse_connection_response(response.json())
            responses.extend(connection_response.connections)
            if limit and len(responses) > limit:
                responses = responses[:limit]

            if not connection_response.has_more:
                break

            request.paging_reference = connection_response.next_pointer

        return responses
