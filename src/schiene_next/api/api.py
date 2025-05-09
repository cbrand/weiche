from datetime import datetime
from typing import Protocol

from schiene_next.objects import Association, Connection, ConnectionRequest, Location


class Api(Protocol):
    def search_locations(self, query: str, limit: int = 10) -> list[Location]:
        pass

    def search_connections(
        self,
        at: datetime,
        from_location: str,
        to_location: str,
        limit: int = 10,
    ) -> list[Connection]:
        pass

    def search_connections_ext(self, request: ConnectionRequest, limit: int = 10) -> list[Connection]:
        pass

    def get_travel_associations(self) -> list[Association]:
        pass
