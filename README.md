# // UniFi Protect for Home Assistant

-----
## ⚠️ ⚠️ WARNING ABOUT Home Assistant v2022.2
The `unifiprotect` integration will be in Home Assistant core v2022.2. If you are running **0.10.x or older** of the HACS integration, **do not install v2022.2.x of Home Assistant core**.

If you are running 0.11.x or the 0.12.0, you should be safe to delete the HACS version as part of your upgrade. The 0.11.x branch is designed to be compatible with the 0.12.0-beta and the HA core version. The latest version of 0.12.0-beta will be the version of `unifiprotect` in HA core in v2022.0.

This repo is now **deprecated** in favor of the Home Assistant core version. This repo will be archived and removed from HACS after the 2022.4 release of Home Assistant.

### Migration to HA Core Version Steps

If you have Smart Sensor devices and you are **not** running `0.12.0-beta10` or newer, it is recommended you just delete your UniFi Protect integration config and re-add it. If you do not have Smart Sensor devices, you can migrate to the Home Assistant core version by following the steps below:

1. Upgrade to the 0.12.0 version for the HACS unifiprotect integration and restart Home Assistant.
2. Remove your HACS `unifiprotect` integration. It is safe to ignore the warning about needing to remove your config first.
3. Do *not* restart HA yet.
4. Upgrade to Home Assistant 2022.2.x

You **must** remove the HACS integration efore upgrading to 2022.2.0 first to prevent a conflicting version of `pyunifiprotect` from being installed.

### Differences between HACS version 0.12.0 and HA 2022.2.0b1 version:

#### HACS Only

* Migration code for updating from `0.10.x` or older still exists; this code has been _removed_ in the HA core version

#### HA Core Only

* Full language support. All of the languages HA core supports via Lokalise has been added to the ingration.

* Auto-discovery. If you have a Dream machine or a Cloud Key/UNVR on the same VLAN, the UniFi Protect integration will automatically be discovered and prompted for setup.

* UP Doorlock support. The HA core version has full support for the newly release EA UP Doorlock.

-----

![GitHub release (latest by date)](https://img.shields.io/github/v/release/briis/unifiprotect?style=flat-square) [![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg?style=flat-square)](https://github.com/custom-components/hacs) [![](https://img.shields.io/badge/COMMUNITY-FORUM-success?style=flat-square)](https://community.home-assistant.io/t/custom-component-unifi-protect/158041)

The UniFi Protect Integration adds support for retrieving Camera feeds and Sensor data from a UniFi Protect installation on either an Ubiquiti CloudKey+, Ubiquiti UniFi Dream Machine Pro or UniFi Protect Network Video Recorder.

There is support for the following device types within Home Assistant:
* Camera
  * A camera entity for each camera channel and RTSP(S) combination found on the NVR device will be created
* Sensor
  * **Cameras**: (only for cameras with Smart Detections) Currently detected object
  * **Sensors**: Sensors for battery level, light level, humidity and temperate
  * **All Devices** (Disabled by default): a sensor for uptime, BLE signal (only for bluetooth devices), link speed (only for wired devices), WiFi signal (only for WiFi devices)
  * **Cameras** (Disabled by default): sensors for bytes transferred, bytes received, oldest recording, storage used by camera recordings, write rate for camera recordings
  * **Doorbells** (Disabled by default, requires UniFi Protect 1.20.1+) current voltage sensor
  * **NVR** (Disabled by default): sensors for uptime, CPU utilization, CPU temp, memory utilization, storage utilization, percent distribution of timelapse, continuos, and detections video on disk, percentage of HD video, 4K video and free space of disk, estimated recording capacity
* Binary Sensor
  * **Cameras** and **Flood Lights**: sensors for if it is dark, if motion is detected
  * **Doorbells**: sensor if the doorbell is currently being rung
  * **Sensors**: sensors for if the door is open, battery is low and if motion is detected
  * **NVR** (Disabled by default): a sensor for the disk health for each disk
    * **NOTE**: The disk numbers here are _not guaranteed to match up to the disk numbers shown in UniFiOS_
* Switch
  * **Cameras**: switches to enabled/disable status light, HDR, High FPS mode, "Privacy Mode", System Sounds (if the camera has speakers), toggles for the Overlay information, toggles for smart detections objects (if the camera has smart detections)
    * **Privacy Mode**: Turning on Privacy Mode adds a privacy zone that blacks out the camera so nothing can be seen, turn microphone sensitivity to 0 and turns off recording
  * **Flood Lights**: switch to enable/disable status light
  * **All Devices** (Disabled by default): Switch to enable/disable SSH access
* Light
  * A light entity will be created for each UniFi Floodlight found. This works as a normal light entity, and has a brightness scale also.
* Select
  * **Cameras**: selects to choose between the recording mode and the current infrared settings (if the camera has IR LEDs)
  * **Doorbells**: select to choose between the currently disable text options on the LCD screen
  * **Flood Lights**: select to choose between the light turn on mode and the paired camera (used for motion detections)
  * **Viewports**: select to choose between the currently active Liveview display on the Viewport
* Number
  * **Cameras**: number entities for the current WDR setting (only if the camera does not have HDR), current microphone sensitivity level, current optical zoom level (if camera has optical zoom),
  * **Doorbells**: number entity for the current chime duration
  * **Flood Lights**: number entities for the current motion sensitivity level and auto-shutdown duration after the light triggers on
* Media Player
  * A media player entity is added for any camera that has speakers that allow talkback
* Button
  * A button entity is added for every adoptable device (anything except the UniFiOS console) to allow you to reboot the device

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

**verify ssl**:<br>
  *(bool)(Required)*<br>
  If your UniFi Protect instance has a value HTTPS cert, you can enforce validation of the cert

**deactivate rtsp stream**<br>
  *(bool)Optional*<br>
  If this box is checked, the camera stream will not use the RTSP stream, but instead jpeg push. This gives a realtime stream, but does not include Audio.

**realtime metrics**<br>
  *(bool)Optional*<br>
  Enable processing of all Websocket events from UniFi Protect. This enables realtime updates for many sensors that are disabled by default. If this is disabled, those sensors will only update once every 15 minutes. **Will greatly increase CPU usage**, do not enable unless you plan to use it.

**override connection host**
  *(bool)Optional*<br>
  By default uses the connection host provided by your UniFi Protect instance for connecting to cameras for RTSP(S) streams. If you would like to force the integration to use the same IP address you provided above, set this to true.

## Special UniFi Protect Services

The Integration adds specific *UniFi Protect* services and supports the standard camera services. Below is a list of the *UniFi Protect* specific services:

Service | Parameters | Description
:------------ | :------------ | :-------------
`unifiprotect.add_doorbell_text` | `device_id` - A device for your current UniFi Protect instance (in case you have multiple).<br>`message` - custom message text to add| Adds a new custom message for Doorbells.\*
`unifiprotect.remove_doorbell_text` | `device_id` - A device for your current UniFi Protect instance (in case you have multiple).<br>`message` - custom message text to remove| Remove an existing custom message for Doorbells.\*
`unifiprotect.set_default_doorbell_text` | `device_id` - A device for your current UniFi Protect instance (in case you have multiple).<br>`message` - default text for doorbell| Sets the "default" text for when a message is reset or none is set.\*
`unifiprotect.set_doorbell_message` | `device_id` - A device for your current UniFi Protect instance (in case you have multiple).<br>`message` - text for doorbell| Dynamically sets text for doorbell.\*\*
`unifiprotect.profile_ws_messages` | `device_id` - A device for your current UniFi Protect instance (in case you have multiple).<br>`duration` - how long to provide| Debug service to help profile the processing of Websocket messages from UniFi Protect.

\*: Adding, removing or changing a doorbell text option requires you to restart your Home Assistant instance to be able to use the new ones. This is a limitation of how downstream entities and integrations subscribe to options for select entities. They cannot be dynamic.

\*\*: The `unifiprotect.set_doorbell_message` service should _only_ be used for setting the text of your doorbell dynamically. i.e. if you want to set the current time or outdoor temp on it. If you want to set a static message, use the select entity already provided. See the [Dynamic Doorbell](#dynamic-doorbell-messages) blueprint for an example.

## Automating Services

As part of the integration, we provide a couple of blueprints that you can use or extend to automate stuff.

### Doorbell Notifications

[![Open your Home Assistant instance and show the blueprint import dialog with a specific blueprint pre-filled.](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fraw.githubusercontent.com%2Fbriis%2Funifiprotect%2Fmaster%2Fblueprints%2Fautomation%2Funifiprotect%2Fpush_notification_doorbell_event.yaml)

### Motion Notifications

[![Open your Home Assistant instance and show the blueprint import dialog with a specific blueprint pre-filled.](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fraw.githubusercontent.com%2Fbriis%2Funifiprotect%2Fmaster%2Fblueprints%2Fautomation%2Funifiprotect%2Fpush_notification_motion_event.yaml)

### Smart Detection Notifications

[![Open your Home Assistant instance and show the blueprint import dialog with a specific blueprint pre-filled.](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fraw.githubusercontent.com%2Fbriis%2Funifiprotect%2Fmaster%2Fblueprints%2Fautomation%2Funifiprotect%2Fpush_notification_smart_event.yaml)

### Dynamic Doorbell Messages

[![Open your Home Assistant instance and show the blueprint import dialog with a specific blueprint pre-filled.](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fraw.githubusercontent.com%2Fbriis%2Funifiprotect%2Fmaster%2Fblueprints%2Fautomation%2Funifiprotect%2Fdynamic_doorbell.yaml)

### Enable Debug Logging

If logs are needed for debugging or reporting an issue, use the following configuration.yaml:

```yaml
logger:
  default: error
  logs:
    pyunifiprotect: debug
    custom_components.unifiprotect: debug
```

### CONTRIBUTE TO THE PROJECT AND DEVELOPING WITH A DEVCONTAINER

1. Fork and clone the repository.

2. Open in VSCode and choose to open in devcontainer. Must have VSCode devcontainer prerequisites.

3. Run the command container start from VSCode terminal

4. A fresh Home Assistant test instance will install and will eventually be running on port 9123 with this integration running

5. When the container is running, go to http://localhost:9123 and the add UniFi Protect from the Integration Page.
