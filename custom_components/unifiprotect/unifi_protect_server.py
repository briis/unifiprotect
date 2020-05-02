"""Unifi Protect Server Wrapper."""

import datetime
import logging
import time
import urllib3

import aiohttp


class Invalid(Exception):
    """Invalid return from Authorization Request."""

    pass


class NotAuthorized(Exception):
    """Wrong username and/or Password."""

    pass


class NvrError(Exception):
    """Other error."""

    pass


_LOGGER = logging.getLogger(__name__)


class UpvServer:
    """Updates device States and Attributes."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        host: str,
        port: int,
        username: str,
        password: str,
        verify_ssl: bool = False,
        minimum_score: int = 0,
    ):
        self._host = host
        self._port = port
        self._base_url = f"https://{host}:{port}"
        self._username = username
        self._password = password
        self._verify_ssl = verify_ssl
        self._minimum_score = minimum_score
        self.access_key = None
        self.device_data = {}

        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.req = session
        self._api_auth_bearer_token = None

    @property
    def devices(self):
        """ Returns a JSON formatted list of Devices. """
        return self.device_data

    async def update(self) -> dict:
        """Updates the status of devices."""
        if self._api_auth_bearer_token is None:
            self._api_auth_bearer_token = await self._get_api_auth_bearer_token()
        await self._get_camera_list()
        await self._get_motion_events(10)
        return self.devices

    async def _get_api_auth_bearer_token(self) -> str:
        """get bearer token using username and password of local user."""
        auth_uri = f"{self._base_url}/api/auth"
        async with self.req.post(
            auth_uri,
            headers={"Connection": "keep-alive"},
            json={"username": self._username, "password": self._password},
            verify_ssl=self._verify_ssl,
        ) as response:
            if response.status == 200:
                return response.headers["Authorization"]
            else:
                if response.status in (401, 403):
                    raise NotAuthorized("Unifi Protect reported authorization failure")
                if response.status / 100 != 2:
                    raise NvrError(f"Request failed: {response.status}")

    async def _get_api_access_key(self) -> str:
        """get API Access Key."""
        access_key_uri = f"{self._base_url}/api/auth/access-key"
        async with self.req.post(
            access_key_uri,
            headers={"Authorization": f"Bearer {self._api_auth_bearer_token}"},
            verify_ssl=self._verify_ssl,
        ) as response:
            if response.status == 200:
                json_response = await response.json()
                return json_response["accessKey"]
            else:
                raise NvrError(
                    f"Request failed: {response.status} - Reason: {response.reason}"
                )

    async def _get_camera_list(self) -> None:
        """Get a list of Cameras connected to the NVR."""
        bootstrap_uri = f"{self._base_url}/api/bootstrap"
        async with self.req.get(
            bootstrap_uri,
            headers={"Authorization": f"Bearer {self._api_auth_bearer_token}"},
            verify_ssl=self._verify_ssl,
        ) as response:
            if response.status == 200:
                json_response = await response.json()
                cameras = json_response["cameras"]

                for camera in cameras:
                    # Get if camera is online
                    if camera["state"] == "CONNECTED":
                        online = True
                    else:
                        online = False
                    # Get Recording Mode
                    recording_mode = str(camera["recordingSettings"]["mode"])
                    # Get Infrared Mode
                    ir_mode = str(camera["ispSettings"]["irLedMode"])
                    # Get the last time motion occured
                    lastmotion = (
                        None
                        if camera["lastMotion"] is None
                        else datetime.datetime.fromtimestamp(
                            int(camera["lastMotion"]) / 1000
                        ).strftime("%Y-%m-%d %H:%M:%S")
                    )
                    # Get when the camera came online
                    upsince = (
                        "Offline"
                        if camera["upSince"] is None
                        else datetime.datetime.fromtimestamp(
                            int(camera["upSince"]) / 1000
                        ).strftime("%Y-%m-%d %H:%M:%S")
                    )

                    if camera["id"] not in self.device_data:
                        # Add rtsp streaming url if enabled
                        rtsp = None
                        channels = camera["channels"]
                        for channel in channels:
                            if channel["isRtspEnabled"]:
                                rtsp = (
                                    "rtsp://"
                                    + str(camera["connectionHost"])
                                    + ":7447/"
                                    + str(channel["rtspAlias"])
                                )
                                break

                        item = {
                            str(camera["id"]): {
                                "name": str(camera["name"]),
                                "type": str(camera["type"]),
                                "recording_mode": recording_mode,
                                "ir_mode": ir_mode,
                                "rtsp": rtsp,
                                "up_since": upsince,
                                "last_motion": lastmotion,
                                "online": online,
                                "motion_start": None,
                                "motion_score": 0,
                                "motion_thumbnail": None,
                                "motion_on": False,
                            }
                        }
                        self.device_data.update(item)
                    else:
                        camera_id = camera["id"]
                        self.device_data[camera_id]["last_motion"] = lastmotion
                        self.device_data[camera_id]["online"] = online
                        self.device_data[camera_id]["up_since"] = upsince
                        self.device_data[camera_id]["recording_mode"] = recording_mode
                        self.device_data[camera_id]["ir_mode"] = ir_mode
            else:
                raise NvrError(
                    f"Fetching Camera List failed: {response.status} - Reason: {response.reason}"
                )

    async def _get_motion_events(self, lookback: int = 86400) -> None:
        """Load the Event Log and loop through items to find motion events."""
        event_start = datetime.datetime.now() - datetime.timedelta(seconds=lookback)
        event_end = datetime.datetime.now() + datetime.timedelta(seconds=10)
        start_time = int(time.mktime(event_start.timetuple())) * 1000
        end_time = int(time.mktime(event_end.timetuple())) * 1000

        event_uri = f"{self._base_url}/api/events"
        params = {
            "end": str(end_time),
            "start": str(start_time),
            "type": "motion",
        }
        async with self.req.get(
            event_uri,
            params=params,
            headers={"Authorization": f"Bearer {self._api_auth_bearer_token}"},
            verify_ssl=self._verify_ssl,
        ) as response:
            if response.status == 200:
                events = await response.json()
                for event in events:
                    if event["start"]:
                        start_time = datetime.datetime.fromtimestamp(
                            int(event["start"]) / 1000
                        ).strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        start_time = None
                    if event["end"]:
                        motion_on = False
                    else:
                        if int(event["score"]) >= self._minimum_score:
                            motion_on = True
                        else:
                            motion_on = False

                    camera_id = event["camera"]
                    self.device_data[camera_id]["motion_start"] = start_time
                    self.device_data[camera_id]["motion_score"] = event["score"]
                    self.device_data[camera_id]["motion_on"] = motion_on
                    if (
                        event["thumbnail"] is not None
                    ):  # Only update if there is a new Motion Event
                        self.device_data[camera_id]["motion_thumbnail"] = event[
                            "thumbnail"
                        ]
            else:
                raise NvrError(
                    f"Fetching Eventlog failed: {response.status} - Reason: {response.reason}"
                )

    async def get_thumbnail(self, camera_id: str, width: int = 640) -> bytes:
        """Returns the last recorded Thumbnail, based on Camera ID."""
        await self._get_motion_events()

        thumbnail_id = self.device_data[camera_id]["motion_thumbnail"]

        if thumbnail_id is not None:
            height = float(width) / 16 * 9
            img_uri = f"{self._base_url}/api/thumbnails/{thumbnail_id}"
            params = {
                "accessKey": await self._get_api_access_key(),
                "h": str(height),
                "w": str(width),
            }
            async with self.req.get(
                img_uri, params=params, verify_ssl=self._verify_ssl
            ) as response:
                if response.status == 200:
                    return await response.read()
                else:
                    raise NvrError(
                        f"Thumbnail Request failed: {response.status} - Reason: {response.reason}"
                    )
        return None

    async def get_snapshot_image(self, camera_id: str) -> bytes:
        """ Returns a Snapshot image of a recording event. """
        access_key = await self._get_api_access_key()
        time_since = int(time.mktime(datetime.datetime.now().timetuple())) * 1000
        model_type = self.device_data[camera_id]["type"]
        if model_type.find("G4") != -1:
            image_width = "1280"
            image_height = "720"
        else:
            image_width = "1024"
            image_height = "576"

        img_uri = f"{self._base_url}/api/cameras/{camera_id}/snapshot"
        params = {
            "accessKey": access_key,
            "h": image_height,
            "ts": str(time_since),
            "w": image_width,
        }
        async with self.req.get(
            img_uri, params=params, verify_ssl=self._verify_ssl
        ) as response:
            if response.status == 200:
                return await response.read()
            else:
                _LOGGER.warning(
                    f"Error Code: {response.status} - Error Status: {response.reason}"
                )
                return None

    async def set_camera_recording(self, camera_id: str, mode: str) -> bool:
        """ Sets the camera recoding mode to what is supplied with 'mode'.
            Valid inputs for mode: never, motion, always
        """
        cam_uri = f"{self._base_url}/cameras/{camera_id}"
        data = {
            "recordingSettings": {
                "mode": mode,
                "prePaddingSecs": 2,
                "postPaddingSecs": 2,
                "minMotionEventTrigger": 1000,
                "enablePirTimelapse": False,
            }
        }
        header = {
            "Authorization": f"Bearer {self._api_auth_bearer_token}",
            "Content-Type": "application/json",
        }

        async with self.req.patch(
            cam_uri, headers=header, verify_ssl=self._verify_ssl, json=data
        ) as response:
            if response.status == 200:
                self.device_data[camera_id]["recording_mode"] = mode
                return True
            else:
                raise NvrError(
                    f"Set Recording Mode failed: {response.status} - Reason: {response.reason}"
                )

    async def set_camera_ir(self, camera_id: str, mode: str) -> bool:
        """ Sets the camera infrared settings to what is supplied with 'mode'.
            Valid inputs for mode: auto, on, autoFilterOnly
        """
        if mode == "led_off":
            mode = "autoFilterOnly"
        elif mode == "always_on":
            mode = "on"
        elif mode == "always_off":
            mode = "off"

        cam_uri = f"{self._base_url}/cameras/{camera_id}"
        data = {"ispSettings": {"irLedMode": mode, "irLedLevel": 255}}
        header = {
            "Authorization": f"Bearer {self._api_auth_bearer_token}",
            "Content-Type": "application/json",
        }

        async with self.req.patch(
            cam_uri, headers=header, verify_ssl=self._verify_ssl, json=data
        ) as response:
            if response.status == 200:
                self.device_data[camera_id]["ir_mode"] = mode
                return True
            else:
                raise NvrError(
                    "Set IR Mode failed: %s - Reason: %s"
                    % (response.status, response.reason)
                )
