# Unifi Protect for Home Assistant
Unifi Protect Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

This is a Home Assistant Integration for Ubiquiti's Unifi Protect Surveillance system.

This Home Assistant integration is inspired by [danielfernau's video downloader program](https://github.com/danielfernau/unifi-protect-video-downloader) and the Authorization implementation is copied from there.

Basically what this does, is integrating the Camera feeds from Unifi Protect in to Home Assistant, and furthermore there is an option to get Binary Motion Sensors and Sensors that show the current Recording Settings pr. camera.

## Prerequisites
Before you install this Integration you need to ensure that the following two settings are applied in Unifi Protect:
1. **Local User needs to be added** Open Unifi Protect in your browser. Click the USERS tab and you will get a list of users. Either select and existing user, or create a new one. The important thing is that the user is part of *Administrators* and that a local username and password is set for that user.This is the username and password you will use when setting up the Integration later.<br>
2. **RTSP Stream** Select each camera under the CAMERAS tab, click on the camera and you will get a menu on the right side. Click the MANAGE button and there will be a menu like the picture below. (If you can't see the same picture click the + sign to the right of RTSP). Make sure that at least one of the streams is set to on. It does not matter whcich one, or if you select more than one. The integration will pick the one with the highest resolution.<br>

![USER Settings](https://github.com/briis/unifiprotect/blob/master/images/setup_user.png) ![RTSP Settings](https://github.com/briis/unifiprotect/blob/master/images/setup_rtsp.png)

**Note:** This has been testet on Unifi Protect Controller version 1.13.0-beta.16, and I cannot guarantee that this will work on a lower version than that.

## Manual Installation
To add Unifi Protect to your installation, create this folder structure in your /config directory:

`custom_components/unifiprotect`.
Then, drop the following files into that folder:

```yaml
__init__.py
manifest.json
sensor.py
binary_sensor.py
camera.py
protectnvr.py
```

## HACS Installation
This Integration is not yet part of the default HACS store, but will be once I am convinced it is stable. But it still supports HACS. Just go to settings in HACS and add `briis/unifiprotect` as a Custom Repository. Use *Integration* as Category.

## Configuration
Start by configuring the core platform. No matter which of the entities you activate, this has to be configured. The core platform by itself does nothing else than establish a link the *Unifi Protect NVR*, so by activating this you will not see any entities being created in Home Assistant.

Edit your *configuration.yaml* file and add the *mbweather* component to the file:
```yaml
# Example configuration.yaml entry
unifiprotect:
  host: <Internal ip address of your Unifi Protect NVR>
  username: <your local Unifi Protect username>
  password: <Your local Unifi Protect Password>
```
**host**:<br>
(string)(Required) Type the IP address of your *Unifi Protect NVR*. Example: `192.168.1.10`<br>

**username**:<br>
(string)(Required) The local username you setup under the *Prerequisites* section.<br>

**password**<br>
(string)(Required) The local password you setup under the *Prerequisites* section.<br>

### Camera
The Integration will add all Cameras currently connected to Unifi Protect. If you add more cameras, you will have to restart Home Assistant to see them in Home Assistant. 

Edit your *configuration.yaml* file and add the *mbweather* component to the file:
```yaml
# Example configuration.yaml entry
camera:
  - platform: unifiprotect
```

The Integration currently supports the following standard Home Assistant services:
1. `camera.disable_motion_detection` - This will disable motion detection on the specified camera
2. `camera.enable_motion_detection` - This will enable motion detection on the specified camera

I am planning on adding the `camera.snapshot` service in a future release
