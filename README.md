# // UniFi Protect for Home Assistant

![GitHub release (latest by date)](https://img.shields.io/github/v/release/briis/unifiprotect?style=flat-square) [![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg?style=flat-square)](https://github.com/custom-components/hacs) [![](https://img.shields.io/badge/COMMUNITY-FORUM-success?style=flat-square)](https://community.home-assistant.io/t/custom-component-unifi-protect/158041)

The UniFi Protect Integration adds support for retrieving Camera feeds and Sensor data from a UniFi Protect installation on either an Ubiquiti CloudKey+, Ubiquiti UniFi Dream Machine Pro or UniFi Protect Network Video Recorder.

There is support for the following device types within Home Assistant:
* Camera
  * A camera entity for each camera found on the NVR device will be created
* Sensor
  * A sensor for each camera found will be created. This sensor will hold the current recording mode.
  * A sensor for each Floodlight device found will be created. This sensor will hold the status of when light will turn on.
* Binary Sensor
  * One to two binary sensors will be created per camera found. There will always be a binary sensor recording if motion is detected per camera. If the camera is a doorbell, there will also be a binary sensor created that records if the doorbell is pressed.
* Switch
  * For each camera supporting High Dynamic Range (HDR) a switch will be created to turn this setting on or off.
  * For each camera supporting High Frame Rate recording a switch will be created to turn this setting on or off.
  * For each camera a switch will be created to turn the status light on or off.
* Light
  * A light entity will be created for each UniFi Floodlight found. This works as a normal light entity, and has a brightness scale also.
* Select
  * For each Camera found there will be a Select entity created from where you can set the cameras recording mode.
  * For each Doorbell found, there will be a Select entity created that makes it possible to set the LCD Text. If you make a list of Texts in the Integration configuration, you can both set the standard texts and custom text that you define here.
  * For each Camera found there will be a Select entity created from where you can set the behaviour of the Infrared light on the Camera
  * For each Viewport found, there will be a Select entity from where you change the active View being displayed on the Viewport.
  * For each Floodlight device there be a Select entity to set the behaviour of the built-in motion sensor.
* Number
  * For each camera supporting WDR, a number entity will be setup to set the active value.
  * For each camera a number entity will be created from where you can set the microphone sensitivity level.
  * For each camera supporting Optical Zoom, a number entity will be setup to set the zoom position.

It supports both regular Ubiquiti Cameras and the UniFi Doorbell. Camera feeds, Motion Sensors, Doorbell Sensors, Motion Setting Sensors and Switches will be created automatically for each Camera found, once the Integration has been configured.

## Table of Contents

1. [UniFi Protect Support](#unifi-protect-support)
2. [Hardware Support](#hardware-support)
3. [Prerequisites](#prerequisites)
4. [Installation](#installation)
5. [UniFi Protect Services](#special-unifi-protect-services)
6. [UniFi Protect Events](#unifi-protect-events)
7. [Automating Services](#automating-services)
    * [Send a notification when the doorbell is pressed](#send-a-notification-when-the-doorbell-is-pressed)
    * [Person Detection](#automate-person-detection)
    * [Input Slider for Doorbell Chime Duration](#create-input-slider-for-doorbell-chime-duration)
8. [Enable Debug Logging](#enable-debug-logging)
9. [Contribute to Development](#contribute-to-the-project-and-developing-with-a-devcontainer)

## UniFi Protect Support

In general, stable/beta version of this integration mirror stable/beta versions of UniFi Protect. That means:

**Stable versions of this integration require the latest stable version of UniFi Protect to run.**

**Beta versions / `master` branch of this integration require the latest beta version of UniFi Protect to run (or the latest stable if there is no beta)**

We try our best to avoid breaking changes so you may need to use older versions of UniFi Protect with newer versions of the integration. Just keep in mind, we may not be able to support you if you do.

## Docs for Old Versions

If you are not using the latest beta of the integration, you can view old versions of this README at any time in GitHub at `https://github.com/briis/unifiprotect/tree/{VERSION}`. Example, docs for v0.9.1 can be found at [https://github.com/briis/unifiprotect/tree/v0.9.1](https://github.com/briis/unifiprotect/tree/v0.9.1)

## Minimal Versions

As of v0.10 of the integration, the following versions of HA and UniFi Protect are _required_ to even install the integration:

* UniFi Protect minimum version is **1.20.0**
* Home Assistant minimum version is **2021.11.0**

## Hardware Support

This Integration supports all UniFiOS Consoles that can run UniFi Protect. Currently this includes:

* UniFi Protect Network Video Recorder (**UNVR**)
* UniFi Protect Network Video Recorder Pro (**UNVRPRO**)
* UniFi Dream Machine Pro (**UDMP**)
* UniFi Cloud Key Gen2 Plus (**CKGP**) firmware version v2.0.24+

Ubiquity released V2.0.24 as an official firmware release for the CloudKey+, and it is recommended that people upgrade to this UniFiOS based firmware for their CloudKey+, as this gives a much better realtime experience.

CKGP with Firmware V1.x **do NOT run UniFiOS**, you must upgrade to firmware v2.0.24 or newer.

**NOTE**: If you are still running a version of UniFi Protect without a UniFiOS Console, you can use a V0.8.x as it is the last version fully supported by NON UniFiOS devices. However, please note NON UniFiOS devices are not supported by us anymore.

## Prerequisites

Before you install this Integration you need to ensure that the following two settings are applied in UniFi Protect:

1. **Local User**
    * Login to your *Local Portal* on your UniFiOS device, and click on *Users*
    * In the upper right corner, click on *Add User*
    * Click *Add Admin*, and fill out the form. Specific Fields to pay attention to:
      * Role: Must be *Limited Admin*
      * Account Type: *Local Access Only*
      * CONTROLLER PERMISSIONS - Under UniFi Protect, select Administrators.
    * Click *Add* in at the bottom Right.

    **HINT**: A few users have reported that they had to restart their UDMP device after creating the local user for it to work. So if you get some kind of *Error 500* when setting up the Integration, try restart the UDMP.

    ![ADMIN_UNIFIOS](https://github.com/briis/unifiprotect/blob/master/images/screenshots/unifi_os_admin.png)

2. **RTSP Stream**

    The Integration uses the RTSP Stream as the Live Feed source, so this needs to be enabled on each camera. With the latest versions of UniFi Protect, the stream is enabled per default, but it is recommended to just check that this is done. To check and enable the the feature
    * open UniFi Protect and click on *Devices*
    * Select *Manage* in the Menu bar at the top
    * Click on the + Sign next to RTSP
    * Enable minimum 1 stream out of the 3 available. UniFi Protect will select the Stream with the Highest resolution

## Installation

This Integration is part of the default HACS store. Search for *unifi protect* under *Integrations* and install from there. After the installation of the files you must restart Home Assistant, or else you will not be able to add UniFi Protect from the Integration Page.

If you are not familiar with HACS, or haven't installed it, I would recommend to [look through the HACS documentation](https://hacs.xyz/), before continuing. Even though you can install the Integration manually, I would recommend using HACS, as you would always be reminded when a new release is published.

**Please note**: All HACS does, is copying the needed files to Home Assistant, and placing them in the right directory. To get the Integration to work, you now need to go through the steps in the *Configuration* section.

Before you restart Home Assistant, make sure that the stream component is enabled. Open `configuration.yaml` and look for *stream:*. If not found add `stream:` somewhere in the file and save it.

## Configuration

To add *UniFi Protect* to your Home Assistant installation, go to the Integrations page inside the configuration panel, click on `+ ADD INTEGRATION`, find *UniFi Protect*, and add your UniFi Protect server by providing the Host IP, Port Number, Username and Password.

**Note**: If you can't find the *UniFi Protect* integration, hard refresh your browser, when you are on the Integrations page.

If the UniFi Protect Server is found on the network it will be added to your installation. After that, you can add more UniFi Protect Servers, should you have more than one installed.

**You can only add UniFi Protect through the Integration page, Yaml configuration is no longer supported.**

### MIGRATING FROM CLOUDKEY+ V1.x

When you upgrade your CloudKey+ from FW V1.x to 2.x, your CK wil move to UniFiOS as core operating system. That also means that where you previously used port 7443 you now need to use port 443. There are two ways to fix this:

* Delete the UniFi Protect Integration and re-add it, using port 443.
* Edit the file `.storage/core.config_entries` in your Home Assistant instance. Search for UniFi Protect and change port 7443 to 443. Restart Home Assistant. (Make a backup first)

### CONFIGURATION VARIABLES

**host**:<br>
  *(string)(Required)*<br>
  Type the IP address of your *UniFi Protect NVR*. Example: `192.168.1.1`

**port**:<br>
  *(int)(Optional)*<br>
  The port used to communicate with the NVR. Default is 443.

**username**:<br>
  *(string)(Required)*<br>
  The local username you setup under the *Prerequisites* section.

**password**:<br>
  *(string)(Required)*<br>
  The local password you setup under the *Prerequisites* section.

**deactivate rtsp stream**<br>
  *(bool)Optional*<br>
  If this box is checked, the camera stream will not use the RTSP stream, but instead jpeg push. This gives a realtime stream, but does not include Audio.

**doorbell text**<br>
  *(string)Optional*<br>
  If a Doorbell is attached to UniFi Protect, you can use this field to write a list of Custom Texts that can be displayed on the Doorbell LCD Screen. The list must be comma separated and will be truncated to 30 characters per item. Example: `RING THE BELL, WE ARE SLEEPING, GO AWAY`

## Special UniFi Protect Services

The Integration adds specific *UniFi Protect* services and supports the standard camera services. Below is a list of the *UniFi Protect* specific services:

Service | Parameters | Description
:------------ | :------------ | :-------------
`unifiprotect.set_recording_mode` | `entity_id` - Name of entity to set recording mode for.<br>`recording_mode` - always, detections or never| Set the recording mode for each Camera.
`unifiprotect.set_ir_mode` | `entity_id` - Name of entity to set infrared mode for.<br>`ir_mode` - auto, autoFilterOnly, on, off | Set the infrared mode for each Camera.
`unifiprotect.set_status_light` | `entity_id` - Name of entity to toggle status light for.<br>`light_on` - true or false | Turn the status light on or off for each Camera.
`unifiprotect.set_doorbell_lcd_message` | `entity_id` - Name of doorbell to display message on.<br>`message` - The message to display. (Will be truncated to 30 Characters)<br>`duration` - The time in minutes the message should display. Leave blank to display always. | Display a Custom message on the LCD display on a G4 Doorbell
`unifiprotect.set_highfps_video_mode` | `entity_id` - Name of entity to toggle High FPS for.<br>`high_fps_on`  - true or false | Toggle High FPS on supported Cameras.
`unifiprotect.set_hdr_mode` | `entity_id` - Name of entity to toggle HDR for.<br>`hdr_on`  - true or false | Toggle HDR mode on supported Cameras.
`unifiprotect.set_mic_volume` | `entity_id` - Name of entity to adjust microphone volume for.<br>`level`  - a value between 0 and 100| Set Microphone sensitivity on Cameras.
`unifiprotect.set_privacy_mode` | `entity_id` - Name of entity to adjust privacy mode for.<br>`privacy_mode`  - true to enable, false to disable<br>`mic_level` - 0 to 100, where 0 is off<br>`recording_mode` - always, detections or never| Set Privacy mode for a camera, where the screen goes black when enabled.
`unifiprotect.light_settings` | `entity_id` - Name of entity to adjust settings for.<br>`mode`  - When to turn on light at Motion, where off is never, motion is on motion detection and dark is only when it is dark outside.<br>`enable_at` - When motion is selected as mode, one can adjust if light turns on motion detection. Where fulltime is always, and dark is only when dark.<br>`duration` - Number of seconds the light stays turned on. Must be one of these values: 15, 30, 60, 300, 900.<br>`sensitivity` - Motion sensitivity of the PIR. Must be a number between 1 and 100. | Adjust settings for the PIR motion sensor in the Floodlight.
`unifiprotect.set_doorbell_chime_duration` | `entity_id` - The Doorbell attached to the Chime.<br>`chime_duration`  - 0 to 10000 | Set Doorbell Chime duration.

**Note:** When using the HA Service *camera.enable_motion_detection*, Recording in UniFi Protect will be set to *detections*. If you want to have the cameras recording all the time, you have to set that in UniFi Protect App or use the service `unifiprotect.set_recording_mode`.

## UniFi Protect Events

The following UniFi Protect events are triggered when running this Integration:

Event Type | Description | Data
:------------ | :------------ | :-------------
`unifiprotect_doorbell` | Triggers when the doorbell button is pressed | `ring`: true, `entity_id`: The entity that triggers the event
`unifiprotect_motion` | Triggers when motion is detected on a camera | `motion_on`: true, `entity_id`: The entity that triggers the event

## Automating Services

Below is a couple of examples on how you can automate some of the things you might do with this Integration.

### SEND A NOTIFICATION WHEN THE DOORBELL IS PRESSED

Below is a very basic example on how to perform an action when the doorbell is pressed. Modify the action part to what you want to happen.

```yaml
alias: Detect Doorbell Pressed
description: Notify User when the doorbell is pressed
mode: single
trigger:
  - platform: event
    event_type: unifiprotect_doorbell
condition: []
action:
  - service: notify.notify
    data:
      message: There is somebody at your door
      title: The doorbell has been pressed
```

### AUTOMATE PERSON DETECTION

If you have G4 Series Cameras, it is possible to do object detection directly on the Camera. Currently they only seem to support detecting a Person, but maybe Cars, Animals etc. will be added in the future.
Here is an example of how you can use this to send a notification to your phone if a Person is detected on a Camera, where Recording mode is set to `motion` or `always`. In this example the camera is called `camera.outdoor`, so the corresponding Binary Motion Sensor is called `binary_sensor.motion_outdoor`. It is a very basic example, sending a Notification via the Notify Service Pushover, when a person has been detected, but it can be used to illustrate the use case.

```yaml
- id: '1603355532588'
  alias: Send message when person detected
  description: ''
  trigger:
  - platform: state
    entity_id: binary_sensor.motion_outdoor
    to: person
    attribute: event_object
  condition: []
  action:
  - service: notify.pushover
    data:
      message: A person has been detected on the Camera
  mode: single
```

### CREATE INPUT SLIDER FOR DOORBELL CHIME DURATION

To set the Doorbell chime duration you can use the Service `unifiprotect.set_doorbell_chime_duration` but if you want to be able to do this from Lovelace, you can add a Input Slider for each doorbell and then do it from there. This shows you how you can do that.

* Go to *Configuration* and select *Helpers*.
* Click `+ ADD HELPER` and select *Number*.
* Name your Slider, set Min to 0, Max to 10000 and step to 100 and then click CREATE.

Now create a new Automation, that reacts to a value change of the above slider. In this case I named the slider `input_number.doorbell_chime` and the Camera is called `camera.test_doorbell`.

```yaml
alias: Adjust Doorbell Chime Durationon Test Doorbell
description: ''
trigger:
  - platform: state
    entity_id: input_number.doorbell_chime
condition: []
action:
  - service: unifiprotect.set_doorbell_chime_duration
    data:
      entity_id: camera.test_doorbell
      chime_duration: '{{ states(''input_number.doorbell_chime'') | int }}'
    entity_id: ' camera.test_doorbell'
mode: single
```

### Enable Debug Logging

If logs are needed for debugging or reporting an issue, use the following configuration.yaml:

```yaml
logger:
  default: error
  logs:
    custom_components.unifiprotect: debug
```

### CONTRIBUTE TO THE PROJECT AND DEVELOPING WITH A DEVCONTAINER

1. Fork and clone the repository.

2. Open in VSCode and choose to open in devcontainer. Must have VSCode devcontainer prerequisites.

3. Run the command container start from VSCode terminal

4. A fresh Home Assistant test instance will install and will eventually be running on port 9123 with this integration running

5. When the container is running, go to http://localhost:9123 and the add UniFi Protect from the Integration Page.
