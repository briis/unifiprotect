---
title: Ubiquiti UniFi Protect
description: Instructions on how to configure UniFi Protect integration by Ubiquiti.
ha_category:
  - Hub
  - Camera
  - Light
  - Number
  - Sensor
  - Select
  - Switch
ha_release: 2022.1
ha_iot_class: Local Push
ha_config_flow: true
ha_quality_scale: platinum
ha_codeowners:
  - '@briis'
ha_domain: unifiprotect
ha_ssdp: true
ha_platforms:
  - camera
  - binary_sensor
  - sensor
  - light
  - switch
  - select
  - number
---

The [UniFi Protect Integration](https://ui.com/camera-security) by [Ubiquiti Networks, inc.](https://www.ui.com/), adds support for retrieving Camera feeds and Sensor data from a UniFi Protect installation on either a Ubiquiti CloudKey+, Ubiquiti UniFi Dream Machine Pro or UniFi Protect Network Video Recorder.

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


{% include integrations/config_flow.md %}

### Hardware

This Integration supports all Ubiquiti Hardware that can run UniFi Protect. Currently this includes:

* UniFi Protect Network Video Recorder (**UNVR**)
* UniFi Dream Machine Pro (**UDMP**)
* UniFi Cloud Key Gen2 Plus (**CKGP**) Minimum required Firmware version is **2.0.24** Below that this Integration will not run on a CloudKey+

### Software Versions
* UniFi Protect minimum version is **1.20.0**
* Home Assistant minimum version is **2021.9.0**


## Services

### Service unifi.reconnect_client

Try to get a wireless client to reconnect to the network.

| Service data attribute | Optional | Description                                                                 |
| ---------------------- | -------- | --------------------------------------------------------------------------- |
| `device_id`            | No       | String representing a device ID related to a UniFi integration.             |

### Service unifi.remove_clients

Clean up clients on the UniFi Controller that has only been associated with the controller for a short period of time. The difference between first seen and last seen needs to be less than 15 minutes and the client can not have a fixed IP, hostname or name associated with it.

## Switch

### Block network access for clients

Allow control of network access to clients configured in the integration options by adding MAC addresses. Items in this list will have a Home Assistant switch created, using the UniFi Device name, allowing for blocking and unblocking.

### Control clients powered by POE

Entities appear automatically for each connected POE client. If no POE client device is in operation, no entity will be visible. Note: UniFi infrastructure devices such as access points and other switches are not (yet) supported, even if they are powered over ethernet themselves.

Note that POE control actually configures the network port of the switch which the client is connected to.

### Control DPI Traffic Restrictions

Entities appear automatically for each restriction group. If there are no restrictions in a group, no entity will be visible. Toggling the switch in Home Assistant will enable or disable all restrictions inside a group.

## Sensor

### Bandwidth sensor

Get entities reporting receiving and transmitting bandwidth per network client.

### Uptime sensor

Get entities reporting uptime per network client.

## Debugging integration

If you have problems with UniFi or the integration you can add debug prints to the log.

```yaml
logger:
  default: info
  logs:
    aiounifi: debug
    homeassistant.components.unifi: debug
    homeassistant.components.device_tracker.unifi: debug
    homeassistant.components.switch.unifi: debug
```
