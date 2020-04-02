
# Unifi Protect for Home Assistant

![GitHub release (latest by date including pre-releases)](https://img.shields.io/github/v/release/briis/unifiprotect?include_prereleases&style=flat-square) [![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs)

This is a Home Assistant Integration for Ubiquiti's Unifi Protect Surveillance system.

This Home Assistant integration is inspired by [danielfernau's video downloader program](https://github.com/danielfernau/unifi-protect-video-downloader) and the Authorization implementation is copied from there.

Basically what this does, is integrating the Camera feeds from Unifi Protect in to Home Assistant, and furthermore there is an option to get Binary Motion Sensors and Sensors that show the current Recording Settings pr. camera.

## Prerequisites

Before you install this Integration you need to ensure that the following two settings are applied in Unifi Protect:

1. **Local User needs to be added** Open Unifi Protect in your browser. Click the USERS tab and you will get a list of users. Either select an existing user, or create a new one. The important thing is that the user is part of *Administrators* and that a local username and password is set for that user. This is the username and password you will use when setting up the Integration later.
2. **RTSP Stream** Select each camera under the CAMERAS tab, click on the camera and you will get a menu on the right side. Click the MANAGE button and there will be a menu like the picture below. (If you can't see the same picture click the + sign to the right of RTSP). Make sure that at least one of the streams is set to on. It does not matter which one, or if you select more than one, the integration will pick the one with the highest resolution.  

![USER Settings](https://github.com/briis/unifiprotect/blob/master/images/setup_user.png) ![RTSP Settings](https://github.com/briis/unifiprotect/blob/master/images/setup_rtsp.png)

**Note:**  

* This has been testet on a Cloud Key Gen2+ with Unifi Protect Controller version 1.13.0-beta.16 and higher. I cannot guarantee that this will work on a lower version than that.
* It is **not working** with *UnifiOS* that is currently being shipped with the Unifi Dream Machine Pro in the US. I have no access to a system like that, so I don't know when and if, that can be supported.

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
switch.py
unifi_protect_server.py
services.yaml
```

## HACS Installation

This Integration is part of the default HACS store. Search for *unifi protect* under *Integrations* and install from there.

## Configuration

Start by configuring the core platform. No matter which of the entities you activate, this has to be configured. The core platform by itself does nothing else than establish a link the *Unifi Protect NVR*, so by activating this you will not see any entities being created in Home Assistant.

Edit your *configuration.yaml* file and add the *unifiprotect* component to the file:

```yaml
# Example configuration.yaml entry
unifiprotect:
  host: <Internal ip address of your Unifi Protect NVR>
  username: <your local Unifi Protect username>
  password: <Your local Unifi Protect Password>
  image_width: <Size of the Thumbnail Image>
  minimum_score: <minimum score before motion detection is activated>
```

**host**:  
(string)(Required) Type the IP address of your *Unifi Protect NVR*. Example: `192.168.1.10`  

**username**:  
(string)(Required) The local username you setup under the *Prerequisites* section.  

**password**  
(string)(Required) The local password you setup under the *Prerequisites* section.  

**image_width**  
(int)(Optional) The width of the Thumbnail Image. Default is 640px  

**minimum_score**  
(int)(Optional) Minimum Score of Motion Event before motion is triggered. Integer between 0 and 100. Default is 0, and with that value, this option is ignored  

### Camera

The Integration will add all Cameras currently connected to Unifi Protect. If you add more cameras, you will have to restart Home Assistant to see them in Home Assistant.

#### Remember

* if you already setup the camera using another platform, like the `Generic IP Platform` then remove those before you setup this Platform, as cameras with the same name cannot co-exist.
* Also, if you are running your Home Assistant installation directly on a Mac, you might need to enable `stream:` in your `configuration.yaml` to be able to do live streaming.

Edit your *configuration.yaml* file and add the *unifiprotect* component to the file:

```yaml
# Example configuration.yaml entry
camera:
  - platform: unifiprotect
```

The Integration adds specific *Unifi Protect* services and supports the standard camera services. Not all have been testet but the following are working:

Service | Parameters | Description
:------------ | :------------ | :-------------
`camera.disable_motion_detection` | `entity_id` - camera to disable motion on | Disable motion detection on the specified camera
`camera.enable_motion_detection` | `entity_id` - camera to enable motion on | Enable motion detection on the specified camera
`camera.snapshot` | `entity_id` - Name of entity to create snapshots from.<br>`filename` - Filename to store snapshot in | Take a snapshot of the current image on the specified camera and stor in a file
`camera.record` | `entity_id` - camera to record from<br>`filename` - Template of a Filename. Variable is entity_id. Must be mp4.<br>`duration` - (Optional) Target recording length (in seconds).<br>`lookback` - (Optional) Target lookback period (in seconds) to include in addition to duration. Only available if there is currently an active HLS stream. | Record the current stream to a file
`unifiprotect.save_thumbnail_image` | `entity_id` - Name of entity to retrieve thumbnail from.<br>`filename` - Filename to store thumbnail in<br>`image_width` - (Optional) Width of the image in pixels. Height will be scaled proportionally. Default is 640. | Get the thumbnail image of the last recording event (If any), from the specified camera
`unifiprotect.set_recording_mode` | `entity_id` - Name of entity to set recording mode for.<br>`recording_mode` - always, motion or never< | Set the recording mode for each Camera.

**Note:** When using *camera.enable_motion_detection*, Recording in Unfi Protect will be set to *motion*. If you want to have the cameras recording all the time, you have to set that in Unifi Protect App.

### Binary Sensor

If this component is enabled a Binary Motion Sensor for each camera configured, will be created.

In order to use the Binary Sensors, add the following to your *configuration.yaml* file:

```yaml
# Example configuration.yaml entry
binary_sensor:
  - platform: unifiprotect
```

There is a little delay for when this will be triggered, as the way the data is retrieved is through the Unifi Protect event log, and that has a small delay before updated.

**Note:** This will only work if Recording state is set to `motion` or `always` as there is nothing written to the event log, if recording is disabled.

### Sensor

If this component is enabled a Sensor describing the current Recording state for each camera configured, will be created.

In order to use the Sensors, add the following to your *configuration.yaml* file:

```yaml
# Example configuration.yaml entry
sensor:
  - platform: unifiprotect
```

The sensor can have 3 different states:

1. `never` - There will be no recording on the camera
2. `motion` - Recording will happen only when motion is detected
3. `always` - The camera will record everything, and motion events will be logged in Unfi Protect

### Switch

If this component is enabled three Switches are created per Camera.

1. Enable or disable motion recording
2. Enable or disable constant recording
3. Enable or disable Infrared on the Camera

In order to use the Switch component, add the following to your *configuration.yaml* file:

```yaml
# Example configuration.yaml entry
switch:
  - platform: unifiprotect
```
