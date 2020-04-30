"""Unifi Protect Server Wrapper."""

import datetime
import requests
import time
import urllib3


class Invalid(Exception):
    """Invalid return from Authorization Request."""

    pass


class NotAuthorized(Exception):
    """Wrong username and/or Password."""

    pass


class NvrError(Exception):
    """Other error."""

    pass


class UpvServer:
    """Updates device States and Attributes."""

    def __init__(
        self, host, port, username, password, verify_ssl=False, minimum_score=0
    ):
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._verify_ssl = verify_ssl
        self._minimum_score = minimum_score
        self.access_key = None
        self.device_data = {}

        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.req = requests.session()
        self._api_auth_bearer_token = self._get_api_auth_bearer_token()
        self.update()

    @property
    def devices(self):
        """ Returns a JSON formatted list of Devices. """
        return self.device_data

    def update(self):
        """Updates the status of devices."""
        self._get_camera_list()
        self._get_motion_events(10)

    def _get_api_auth_bearer_token(self):
        """get bearer token using username and password of local user."""

        auth_uri = "https://" + str(self._host) + ":" + str(self._port) + "/api/auth"
        response = self.req.post(
            auth_uri,
            headers={"Connection": "keep-alive"},
            json={"username": self._username, "password": self._password},
            verify=self._verify_ssl,
        )
        if response.status_code == 200:
            authorization_header = response.headers["Authorization"]
            return authorization_header
        else:
            if response.status_code in (401, 403):
                raise NotAuthorized("Unifi Protect reported authorization failure")
            if response.status_code / 100 != 2:
                raise NvrError("Request failed: %s" % response.status_code)

    def _get_api_access_key(self):
        """get API Access Key."""

        access_key_uri = (
            "https://"
            + str(self._host)
            + ":"
            + str(self._port)
            + "/api/auth/access-key"
        )
        response = self.req.post(
            access_key_uri,
            headers={"Authorization": "Bearer " + self._api_auth_bearer_token},
            verify=self._verify_ssl,
        )
        if response.status_code == 200:
            json_response = response.json()
            access_key = json_response["accessKey"]
            return access_key
        else:
            raise NvrError(
                "Request failed: %s - Reason: %s" % (response.status_code, response.reason)
            )

    async def _get_camera_list(self):
        """Get a list of Cameras connected to the NVR."""

        bootstrap_uri = (
            "https://" + str(self._host) + ":" + str(self._port) + "/api/bootstrap"
        )
        response = self.req.get(
            bootstrap_uri,
            headers={"Authorization": "Bearer " + self._api_auth_bearer_token},
            verify=self._verify_ssl,
        )
        if response.status_code == 200:
            json_response = response.json()
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
                "Fetching Camera List failed: %s - Reason: %s"
                % (response.status_code, response.reason)
            )

    async def _get_motion_events(self, lookback=86400):
        """Load the Event Log and loop through items to find motion events."""

        event_start = datetime.datetime.now() - datetime.timedelta(seconds=lookback)
        event_end = datetime.datetime.now() + datetime.timedelta(seconds=10)
        start_time = int(time.mktime(event_start.timetuple())) * 1000
        end_time = int(time.mktime(event_end.timetuple())) * 1000

        event_uri = (
            "https://"
            + str(self._host)
            + ":"
            + str(self._port)
            + "/api/events?end="
            + str(end_time)
            + "&start="
            + str(start_time)
            + "&type=motion"
        )

        response = self.req.get(
            event_uri,
            headers={"Authorization": "Bearer " + self._api_auth_bearer_token},
            verify=self._verify_ssl,
        )
        if response.status_code == 200:
            events = response.json()
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
                    self.device_data[camera_id]["motion_thumbnail"] = event["thumbnail"]
        else:
            raise NvrError(
                "Fetching Eventlog failed: %s - Reason: %s"
                % (response.status_code, response.reason)
            )
                      
    def get_thumbnail(self, camera_id, width=640):
        """Returns the last recorded Thumbnail, based on Camera ID."""

        self._get_motion_events()

        thumbnail_id = self.device_data[camera_id]["motion_thumbnail"]

        if thumbnail_id is not None:
            height = float(width) / 16 * 9
            access_key = self._get_api_access_key()
            img_uri = (
                "https://"
                + str(self._host)
                + ":"
                + str(self._port)
                + "/api/thumbnails/"
                + str(thumbnail_id)
                + "?accessKey="
                + access_key
                + "&h="
                + str(height)
                + "&w="
                + str(width)
            )
            response = self.req.get(img_uri, verify=self._verify_ssl)
            if response.status_code == 200:
                return response.content
            else:
                raise NvrError(
                    "Thumbnail Request failed: %s - Reason: %s"
                    % (response.status_code, response.reason)
                )
        else:
            return None

    def get_snapshot_image(self, camera_id):
        """ Returns a Snapshot image of a recording event. """

        access_key = self._get_api_access_key()
        time_since = int(time.mktime(datetime.datetime.now().timetuple())) * 1000
        model_type = self.device_data[camera_id]["type"]
        if (model_type.find("G4") != -1):
            image_width = "1280"
            image_height = "720"
        else:
            image_width = "1024"
            image_height = "576"

        img_uri = (
            "https://"
            + str(self._host)
            + ":"
            + str(self._port)
            + "/api/cameras/"
            + str(camera_id)
            + "/snapshot?accessKey="
            + access_key
            + "&ts="
            + str(time_since)
            + "&h=" + image_height + "&w=" + image_width
        )
        response = self.req.get(img_uri, verify=self._verify_ssl)
        if response.status_code == 200:
            return response.content
        else:
            print(
                "Error Code: "
                + str(response.status_code)
                + " - Error Status: "
                + response.reason
            )
            return None

    def set_camera_recording(self, camera_id, mode):
        """ Sets the camera recoding mode to what is supplied with 'mode'.
            Valid inputs for mode: never, motion, always
        """

        cam_uri = (
            "https://"
            + str(self._host)
            + ":"
            + str(self._port)
            + "/cameras/"
            + str(camera_id)
        )

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
            "Authorization": "Bearer " + self._api_auth_bearer_token,
            "Content-Type": "application/json",
        }

        response = self.req.patch(
            cam_uri, headers=header, verify=self._verify_ssl, json=data
        )
        if response.status_code == 200:
            self.device_data[camera_id]["recording_mode"] = mode
            return True
        else:
            raise NvrError(
                "Set Recording Mode failed: %s - Reason: %s"
                % (response.status_code, response.reason)
            )

    def set_camera_ir(self, camera_id, mode):
        """ Sets the camera infrared settings to what is supplied with 'mode'. 
            Valid inputs for mode: auto, on, autoFilterOnly
        """
        if mode == "led_off":
            mode = "autoFilterOnly"
        elif mode == "always_on":
            mode = "on"
        elif mode == "always_off":
            mode = "off"

        cam_uri = "https://" + str(self._host) + ":" + str(self._port) + "/cameras/" + str(camera_id)

        data =  {
            "ispSettings": {
                "irLedMode":mode,
                "irLedLevel":255
                }
        }

        header = {'Authorization': 'Bearer ' + self._api_auth_bearer_token,'Content-Type': 'application/json'}

        response = requests.patch(cam_uri, headers=header, verify=self._verify_ssl, json=data)
        if response.status_code == 200:
            self.device_data[camera_id]["ir_mode"] = mode
            return True
        else:
            raise NvrError(
                "Set IR Mode failed: %s - Reason: %s"
                % (response.status_code, response.reason)
            )
