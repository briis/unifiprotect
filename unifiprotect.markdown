---
title: Unifi Protect
description: Instructions on how to integrate Unifi Protect into Home Assistant.
ha_category:
  - Binary Sensor
  - Camera
  - Sensor
  - Switch
ha_release: '0.115'
ha_iot_class: Cloud Polling
ha_codeowners:
  - '@briis'
ha_config_flow: true
ha_domain: unifiprotect
---

The `unifiprotect` integration adds support for retrieving Camera feeds and Sensor data from a Unifi Protect installation on either a Ubiquiti CloudKey+ ,Ubiquiti Unifi Dream Machine Pro or UniFi Protect Network Video Recorder.

There is currently support for the following device types within Home Assistant:

- [Binary Sensor](#binary-sensor)
- [Camera](#camera)
- [Sensor](#sensor)
- [Switch](#switch)

## Prerequisites

Before you install this Integration you need to ensure that the following two settings are applied in Unifi Protect:

1. **Local User** The process of creating a local users varies depending on whether you use a CloudKey+ or an UDMP/UNVR server. Please follow the manual for either device to create a local user, that has Administrative rights for Unifi Protect.

2. **RTSP Stream** Live Streaming for Cameras is enabled by activating the RTSP stream on each attached camera. Select each camera under the CAMERAS tab in the Unfi Protect App or Web Interface, click on the camera and you will get a menu on the right side. Click the MANAGE button and there will be a menu like the picture below. (If you can't see the same picture click the + sign to the right of RTSP). Make sure that at least one of the streams is set to on. It does not matter which one, or if you select more than one, the integration will pick the one with the highest resolution.

<p class='img'>
<img src='images/screenshots/unifiprotect_rtsp.png' height='350px' />
</p>


## Configuration

Go to the integrations page in your configuration and click on new integration -> Unifi Protect.

A dialog box will be presented, where the following information needs to be entered:
* **IP Address of CloudKey+ or UDMP/UNVR** - IP address of the Unifi Protect NVR
* **Port Number** - It will be 7443 for a CloudKey+ or else 443
* **Username** - Type the username of the local user created in the *Prerequisites* step
* **Password** - Type the password for the local user

The rest of the Options can be left as they are. They can all be adjusted later, using *Options* on the Widget.

YAML configuration is not available.

## Binary Sensor

Once you have enabled the `unifiprotect` integration , you can start using a binary sensor. Currently, it supports doorbell and cameras.

## Camera

The `unifiprotect` camera platform is consuming the information provided by a camera connected to a [Unifi Protect Video Recorder](https://unifi-network.ui.com/building-security). This integration allows you to view the current live stream created by the camera.

## Sensor

The `unifiprotect` sensor platform is consuming the information provided by a camera connected to a [Unifi Protect Video Recorder](https://unifi-network.ui.com/building-security). This integration allows you to view the recording state of each camera.

## Switch

The `unifiprotect` switch platform is consuming the information provided by a camera connected to a [Unifi Protect Video Recorder](https://unifi-network.ui.com/building-security). This integration allows you to quickly switch ir mode for a camera and to switch recording mode for a camera.

## Services

The Integration supports the standard Camera services like `camera.snapshot` and `camera.record`, but also adds specific *Unifi Protect* services.

### Save Thumbnail Image

`unifiprotect.save_thumbnail_image`

Get the thumbnail image of the last recording event. This requires entity id and filename to store the image in.

### Set Recording Mode

`unifiprotect.set_recording_mode`

Set the recording mode for a camera to either: never record, motion only or always record. This requires entity id and the recording mode.

### Set Infra Red Light Mode

`unifiprotect.set_ir_mode`

Set the infrared mode for a camera to either: auto, always on, always off or led off. This requires entity id and the ir mode.

### Set Camera Status Light

`unifiprotect.set_status_light`

Turn the status light on or off for a camera. This requires entity id and light on mode, that can be true or false.

