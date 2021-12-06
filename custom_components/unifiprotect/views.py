from __future__ import annotations

from http import HTTPStatus
import logging
from typing import Any

from aiohttp import web
from homeassistant.components.http import HomeAssistantView
from homeassistant.core import HomeAssistant, HomeAssistantError
from pyunifiprotect.exceptions import NvrError

from .utils import get_ufp_instance_from_entity_id

_LOGGER = logging.getLogger(__name__)


class ThumbnailProxyView(HomeAssistantView):
    """View to proxy event thumbnails from UniFi Protect"""

    requires_auth = False
    url = "/api/ufp/thumbnail/{entity_id}/{event_id}"
    name = "api:ufp_thumbnail"

    def __init__(self, hass: HomeAssistant):
        self.hass = hass

    def _404(self, message: Any) -> web.Response:
        _LOGGER.error("Error on load thumbnail: %s", message)
        return web.Response(status=HTTPStatus.NOT_FOUND)

    async def get(
        self, request: web.Request, entity_id: str, event_id: str
    ) -> web.Response:
        """Start a get request."""

        width: int | str | None = request.query.get("w")
        height: int | str | None = request.query.get("h")

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

        try:
            _, instance = get_ufp_instance_from_entity_id(self.hass, entity_id)
        except HomeAssistantError as err:
            return self._404(err)

        try:
            thumbnail = await instance.get_event_thumbnail(
                event_id, width=width, height=height
            )
        except NvrError as err:
            return self._404(err)

        if thumbnail is None:
            return self._404("Event thumbnail not found")

        return web.Response(body=thumbnail, content_type="image/jpeg")
