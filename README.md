
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
* The component is **not working** directly with *UnifiOS*, that is currently being shipped with the Unifi Dream Machine Pro in the US. I have no access to a system like that, but [Mark Lopez](@Silvenga) has made a proxy container, that can take care of the new Authentication that UnifiOS introduces. Have a look [here](https://github.com/Silvenga/unifi-udm-api-proxy) for setup instructions.

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
  port: <Port used to communicate with your Unifi Protect NVR>
  image_width: <Size of the Thumbnail Image>
  minimum_score: <minimum score before motion detection is activated>
```

**host**:  
(string)(Required) Type the IP address of your *Unifi Protect NVR*. Example: `192.168.1.10`  

**username**:  
(string)(Required) The local username you setup under the *Prerequisites* section.  

**password**  
(string)(Required) The local password you setup under the *Prerequisites* section.  

**port**  
(int)(Optional) The port used to communicate with the NVR. Default is 7443.

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

The Integration adds specific *Unifi Protect* services and supports the standard camera services. Below is a list of the *Unifi Protect* specific services:

Service | Parameters | Description
:------------ | :------------ | :-------------
`unifiprotect.save_thumbnail_image` | `entity_id` - Name of entity to retrieve thumbnail from.<br>`filename` - Filename to store thumbnail in<br>`image_width` - (Optional) Width of the image in pixels. Height will be scaled proportionally. Default is 640. | Get the thumbnail image of the last recording event (If any), from the specified camera
`unifiprotect.set_recording_mode` | `entity_id` - Name of entity to set recording mode for.<br>`recording_mode` - always, motion or never | Set the recording mode for each Camera.
`unifiprotect.set_ir_mode` | `entity_id` - Name of entity to set infrared mode for.<br>`ir_mode` - auto, always_on, led_off or always_off | Set the infrared mode for each Camera.

**Note:** When using *camera.enable_motion_detection*, Recording in Unfi Protect will be set to *motion*. If you want to have the cameras recording all the time, you have to set that in Unifi Protect App or use the service `unifiprotect.set_recording_mode`.

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
3. Enable or disable Infrared sensors. This switch also supports extra options to define what setting is ON and what settings is OFF. See more below.

In order to use the Switch component, add the following to your *configuration.yaml* file:

```yaml
# Example configuration.yaml entry
switch:
  - platform: unifiprotect
    ir_on: <Optional, type what mode defines on for Infrared>
    ir_off: <Optional, type what mode defines off for Infrared>
```

**ir_on**  
(string)(Optional) The mode that defines Infrared On. Values are: *auto* and *always_on*. Default is *auto*

**ir_off**  
(string)(Optional) The mode that defines Infrared OF. Values are: *led_off* and *always_off*. Default is *always_off*

## Automating Services

If you want to change *Recording Mode* or *Infrared Mode* for a camera, this can be done through the two services `unifiprotect.set_recording_mode` and `unifiprotect.set_ir_mode`.
These Services support more than 2 different modes each, and as such it would be good to have a list to select from when switching the mode of those settings. I have not found a way to create a listbox as Custom Component, but it is fairly simpel to use an *input_select* integration and an *Automation* to achieve a UI friendly way of changing these modes. Below is an example that creates an *input*select* integration for one of the Cameras and then an example of an automation that is triggered whenever the user selects a new value in the dropdown list.

Start by creating the *input_select* integration. If you are on Version 107.x or greater that can now be done directly from the menu under *Configuration* and then *Helpers*. Click the PLUS sign at the bottom and use the *Dropdown* option.  
**Important** Fill in the *Option* part as seen below for the Infrared Service.  
If you do it manually add the following to your *configuration.yaml* file:

```yaml
# Example configuration.yaml entry
input_select:
  camera_office_ir_mode:
    name: IR Mode for Camera Office
    options:
      - auto
      - always_on
      - led_off
      - always_off
    icon: mdi:brightness-4
```

If you did it manually, you need to restart Home Assistant, else you can continue.

Now add a new Automation, like the following:

```yaml
- id: '1585900471122'
  alias: Camera Office IR Mode Change
  description: ''
  trigger:
  - entity_id: input_select.camera_office_ir_mode
    platform: state
  condition: []
  action:
  - data_template:
      entity_id: camera.camera_office
      ir_mode: '{{ states(''input_select.camera_office_ir_mode'') }}'
    entity_id: camera.camera_office
    service: unifiprotect.set_ir_mode
```

Thats it. Whenever you now select a new value from the Dropdown, the automation is activated, and the service is called to change the IR mode. The same can then be achieved for the *recording_mode* by changing the options and the service call in the automation.