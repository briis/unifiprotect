import requests
import urllib3
import json
import time, datetime

class Invalid(Exception):
    pass


class NotAuthorized(Exception):
    pass


class NvrError(Exception):
    pass

class protectRemote(object):
    """Remote control client for Unifi Protect NVR."""

    def __init__(self, host, port, username, password, verify_ssl=False):
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._verify_ssl = verify_ssl
        self._access_key = None
        self._api_camera_list = None
        self._api_event_list = None
        self._snapshot = None

        # disable InsecureRequestWarning for unverified HTTPS requests
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        # Create Request Session
        self.req = requests.session()

        # Get Bearer Token
        self._api_auth_bearer_token =  self._get_api_auth_bearer_token()

    @property
    def cameras(self):
        """ Returns a JSON formatted list of Cameras. """
        self._api_camera_list = self._get_camera_list()
        return self._api_camera_list

    @property
    def events(self):
        """ Returns a JSON formatted list of Events. """
        self._api_event_list = self._get_motion_events()
        return self._api_event_list

    @property
    def snapshot(self, cuid):
        """Returns Snapshot Image."""
        self._snapshot = self.get_snapshot_image(cuid)


    # API Authentication
    # get bearer token using username and password of local user
    def _get_api_auth_bearer_token(self):
        auth_uri = "https://" + str(self._host) + ":" + str(self._port) + "/api/auth"
        response = self.req.post(auth_uri, json={"username": self._username, "password": self._password}, verify=self._verify_ssl)
        if response.status_code == 200:
            # print("Successfully authenticated as user " + str(username))
            authorization_header = response.headers['Authorization']
            return authorization_header
        else:
            if response.status in (401, 403):
                raise NotAuthorized('Unifi Protect reported authorization failure')
            if response.status / 100 != 2:
                raise NvrError('Request failed: %s' % response.status)

    def _get_api_access_key(self):
        access_key_uri = "https://" + str(self._host) + ":" + str(self._port) + "/api/auth/access-key"
        response = self.req.post(access_key_uri, headers={'Authorization': 'Bearer ' + self._api_auth_bearer_token}, verify=self._verify_ssl)
        if response.status_code == 200:
            # print("Successfully requested API Access Key")
            json_response = response.json()
            access_key = json_response['accessKey']
            return access_key
        else:
            # print("Failed to get access key from API. " + str(response.status_code) + " " + str(response.reason))
            return "Failed to get access key from API. " + str(response.status_code) + " " + str(response.reason)
        

    # get camera list
    def _get_camera_list(self):
        bootstrap_uri = "https://" + str(self._host) + ":" + str(self._port) + "/api/bootstrap"
        response = self.req.get(bootstrap_uri, headers={'Authorization': 'Bearer ' + self._api_auth_bearer_token}, verify=self._verify_ssl)
        if response.status_code == 200:
            # print("Successfully retrieved data from /api/bootstrap")
            json_response = response.json()
            cameras = json_response['cameras']
            # print(json.dumps(cameras))

            # print("Cameras found:")
            index = 0
            camera_list = []
            for camera in cameras:
                # print(str(camera['name']) + " (" + str(camera['id']) + ")")
                # Add rtsp streaming url if enabled
                rtsp = None
                channels = camera['channels']
                for channel in channels:
                    if (channel['isRtspEnabled']):
                        rtsp = 'rtsp://' + str(camera['connectionHost']) + ':7447/' + str(channel['rtspAlias'])
                        break
                # Add the snapshot url - must enabled anonymous snapshot on camera
                snapshot = 'http://' + str(camera['host']) + '/snap.jpeg'
                # Get if camera is online
                if (camera['state'] == 'CONNECTED'): 
                    online = True 
                else: 
                    online = False
                # Get the last time motion occured
                lastmotion = datetime.datetime.fromtimestamp(int(camera['lastMotion'])/1000).strftime('%Y-%m-%d %H:%M:%S')
                # Get when the camera came online
                upsince = datetime.datetime.fromtimestamp(int(camera['upSince'])/1000).strftime('%Y-%m-%d %H:%M:%S')
                camera_list.append({"index": str(index), "name": str(camera['name']), "id": str(camera['id']), "type": str(camera['type']), "recording_mode": str(camera['recordingSettings']['mode']), "rtsp": rtsp, 'snapshot': snapshot, 'up_since': upsince, 'last_motion': lastmotion, 'online': online})
                index += 1

            return camera_list
        else:
            # print("Error Code: " + response.status_code + " - Error Status: " + response.reason)
            return None

    # get Motion Events
    def _get_motion_events(self):
        _startTime = datetime.datetime.now() - datetime.timedelta(seconds=10000)
        _endTime = datetime.datetime.now() + datetime.timedelta(seconds=10)
        start_time = int(time.mktime(_startTime.timetuple()))
        end_time = int(time.mktime(_endTime.timetuple()))

        event_uri = "https://" + str(self._host) + ":" + str(self._port) + "/api/events?end="+ str(end_time) + "000&start=" + str(start_time) + "000&type=motion"

        response = self.req.get(event_uri, headers={'Authorization': 'Bearer ' + self._api_auth_bearer_token}, verify=self._verify_ssl)
        if response.status_code == 200:
            # print("Successfully retrieved data from /api/events")
            events = response.json()
            event_list = []
            for event in events:
                # print("Event for camera: " + str(event['camera']))
                if event['start']:
                    start_time = datetime.datetime.fromtimestamp(int(event['start'])/1000).strftime('%Y-%m-%d %H:%M:%S')
                else:
                    start_time = None
                if event['end']:
                    end_time = datetime.datetime.fromtimestamp(int(event['end'])/1000).strftime('%Y-%m-%d %H:%M:%S')
                else:
                    end_time = None
                event_list.append({"id": str(event['id']), "camera": str(event['camera']), "score": event['score'], "start": start_time, "end": end_time, "thumbnail": str(event['thumbnail'])})

            return event_list
        else:
            # print("Error Code: " + response.status_code + " - Error Status: " + response.reason)
            return None


    def update_motion(self, cuid):
        """ Returns Last Motion Status for selected Camera."""
        # Get Motion Events
        event_list = self._get_motion_events()
        #Loop Through Cameras, and see if there is motion
        event_list_sorted = sorted(event_list, key=lambda k: k['start'], reverse=True)
        is_motion = None

        for event in event_list_sorted:
            if (cuid == event['camera']):
                if (event['end'] is None):
                    is_motion = True
                else:
                    is_motion = False

                break
        return is_motion
                

    def get_motion_devices(self):
        """Returns a list with Cameras and current Motion Status."""
        #Get Cameras
        bootstrap_uri = "https://" + str(self._host) + ":" + str(self._port) + "/api/bootstrap"
        response = self.req.get(bootstrap_uri, headers={'Authorization': 'Bearer ' + self._api_auth_bearer_token}, verify=self._verify_ssl)
        if response.status_code == 200:
            json_response = response.json()
            cameras = json_response['cameras']
            camera_list = []
            for camera in cameras:
                camera_list.append({"name": str(camera['name']), "id": str(camera['id'])})

            # Get Motion Events
            event_list = self._get_motion_events()

            #Loop Through Cameras, and see if there is motion
            event_list_sorted = sorted(event_list, key=lambda k: k['start'], reverse=True)

            motion_events = []
            motion = None
            last_motion = None
            cam_iter = iter(camera_list)
            for camera in cam_iter:
                camid = camera['id']
                if not event_list_sorted:
                    break

                for event in event_list_sorted:
                    if (camid  == event['camera']):
                        if (event['end'] is None):
                            motion = True
                            last_motion = event['start']
                        else:
                            motion = False
                            last_motion = event['start']
                        break

                motion_events.append({"camera_id": camera['id'], "name": camera['name'], "last_motion": last_motion , "motion": motion})

            return motion_events
        else:
            return None

    def set_camera_recording(self, uuid, mode):
        """ Sets the camera recoding mode to what is supplied with 'mode'. 
            Valid inputs for mode: never, motion, always
        """

        cam_uri = "https://" + str(self._host) + ":" + str(self._port) + "/cameras/" + str(uuid)

        data =  {
            "recordingSettings": {
                "mode":mode,
                "prePaddingSecs":2,
                "postPaddingSecs":2,
                "minMotionEventTrigger":1000,
                "enablePirTimelapse":False
                }
        }

        header = {'Authorization': 'Bearer ' + self._api_auth_bearer_token,'Content-Type': 'application/json'}

        response = requests.patch(cam_uri, headers=header, verify=self._verify_ssl, json=data)
        if response.status_code == 200:
            return True
        else:
            return False

    def get_camera_recording(self, uuid):
        """ Returns the Camera Recording Mode. """

        cam_list = self.cameras
        recording_mode = None
        for camera in cam_list:
            if (uuid == camera['id']):
                recording_mode = camera['recording_mode']
                break
        return recording_mode

    def get_thumbnail_image(self, tuid):
        """ Returns a Thumbnail image of a recording event. """

        access_key = self._get_api_access_key()
        img_uri = "https://" + str(self._host) + ":" + str(self._port) + "/api/thumbnails/" + str(tuid) + "?accessKey=" + access_key + "&h=68&w=121"
        response = self.req.get(img_uri, verify=self._verify_ssl)
        if response.status_code == 200:
            # output = open("thumbnail.png","wb")
            # output.write(response.content)
            # output.close()
            return response.content
        else:
            print("Error Code: " + response.status_code + " - Error Status: " + response.reason)
            # return None

    def get_snapshot_image(self, tuid):
        """ Returns a Snapshot image of a recording event. """

        access_key = self._get_api_access_key()
        ts = int(time.mktime(datetime.datetime.now().timetuple()))*1000
        img_uri = "https://" + str(self._host) + ":" + str(self._port) + "/api/cameras/" + str(tuid) + "/snapshot?accessKey=" + access_key + "&ts=" + str(ts)
        response = self.req.get(img_uri, verify=self._verify_ssl)
        if response.status_code == 200:
            # output = open("snapshot.png","wb")
            # output.write(response.content)
            # output.close()
            return response.content
        else:
            # print("Error Code: " + response.status_code + " - Error Status: " + response.reason)
            return None

