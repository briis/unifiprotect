"""UniFi Protect Integration views."""
from __future__ import annotations

import collections
from http import HTTPStatus
import logging
from typing import Any

from aiohttp import web
from homeassistant.components.http import KEY_AUTHENTICATED, HomeAssistantView
from homeassistant.core import HomeAssistant
from pyunifiprotect.api import ProtectApiClient
from pyunifiprotect.exceptions import NvrError

from .const import DOMAIN
from .data import ProtectData

_LOGGER = logging.getLogger(__name__)


class ThumbnailProxyView(HomeAssistantView):
    """View to proxy event thumbnails from UniFi Protect."""

    requires_auth = False
    url = "/api/ufp/thumbnail/{event_id}"
    name = "api:ufp_thumbnail"

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize a thumbnail proxy view."""
        self.hass = hass
        self.data = hass.data[DOMAIN]

    def _get_access_tokens(
        self, entity_id: str
    ) -> tuple[collections.deque, ProtectApiClient] | None:

        entries: list[ProtectData] = list(self.data.values())
        for entry in entries:
            if entity_id in entry.access_tokens:
                return entry.access_tokens[entity_id], entry.api
        return None

    def _404(self, message: Any) -> web.Response:
        _LOGGER.error("Error on load thumbnail: %s", message)
        return web.Response(status=HTTPStatus.NOT_FOUND)

    async def get(self, request: web.Request, event_id: str) -> web.Response:
        """Start a get request."""

        entity_id: str | None = request.query.get("entity_id")
        width: int | str | None = request.query.get("w")
        height: int | str | None = request.query.get("h")
        token: str | None = request.query.get("token")

        if width is not None:
            try:
                width = int(width)
            except ValueError:
                return self._404("Invalid width param")
        if height is not None:
            try:
                height = int(height)
            except ValueError:
                return self._404("Invalid height param")

        access_tokens: list[str] = []
        if entity_id is not None:
            items = self._get_access_tokens(entity_id)
            if items is None:
                return self._404(f"Could not find entity with device_id {entity_id}")

            access_tokens = list(items[0])
            instance = items[1]

        authenticated = request[KEY_AUTHENTICATED] or token in access_tokens
        if not authenticated:
            raise web.HTTPUnauthorized()

        try:
            thumbnail = await instance.get_event_thumbnail(
                event_id, width=width, height=height
            )
        except NvrError as err:
            return self._404(err)

        if thumbnail is None:
            return self._404("Event thumbnail not found")

        return web.Response(body=thumbnail, content_type="image/jpeg")
