
# // Unifi Protect for Home Assistant

![GitHub release (latest by date)](https://img.shields.io/github/v/release/briis/unifiprotect?style=flat-square) [![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg?style=flat-square)](https://github.com/custom-components/hacs) [![](https://img.shields.io/badge/COMMUNITY-FORUM-success?style=flat-square)](https://community.home-assistant.io/t/custom-component-unifi-protect/158041)

The Unifi Protect Integration adds support for retrieving Camera feeds and Sensor data from a Unifi Protect installation on either a Ubiquiti CloudKey+ ,Ubiquiti Unifi Dream Machine Pro or UniFi Protect Network Video Recorder.

There is support for the following device types within Home Assistant:
* Camera
  * A camera entity for each camera found on the NVR device will be created
* Sensor
  * A sensor for each camera found will be created. This sensor will hold the current recording mode.
* Binary Sensor
  * One to two binary sensors will be created per camera found. There will always be a binary sensor recording if motion is detected per camera. If the camera is a doorbell, there will also be a binary sensor created that records if the doorbell is pressed.
* Switch
  * Several switches will be created per camera found. What switches is depended on the capbability of the specific camera. But typically these switches are used to control recording mode, Infrared and Video mode settings.
* Light
  * A light entity will be created for each UniFi Floodlight found. This works as a normal light entity, and has a brightness scale also.

It supports both regular Ubiquiti Cameras and the Unifi Doorbell. Camera feeds, Motion Sensors, Doorbell Sensors, Motion Setting Sensors and Switches will be created automativally for each Camera found, once the Integration has been configured.

## Table of Contents

1. [Hardware Support](#hardware-support)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [UniFi Protect Services](#special-unifi-protect-services)
5. [Automating Services](#automating-services)
    * [Setting Recording or IR Mode](#automate-setting-recording-or-ir-mode)
    * [Person Detection](#automate-person-detection)
    * [Input Slider for Microphone Sensitivity](#create-input-slider-for-microphone-sensitivity)
6. [Contribute to Development](#contribute-to-the-project-and-developing-with-a-devcontainer)
## Hardware Support

This Integration supports all Ubiquiti Hardware that can run Unfi Protect. Currently this includes:

* Unifi Protect Network Video Recorder (**UNVR**)
* Unifi Dream Machine Pro (**UDMP**)
* Unifi Cloud Key Gen2 Plus (**CKGP**)

The first two devices run Unifi's own operating system called UnifiOS, and the CKGP with Firmware V2.0.18 or greater also runs UnifiOS. This is important to note, as you will need to know this during installation if your NVR Device runs UnifiOS or not.

Ubiquity released V2.0.24 as an official firmware release for the CloudKey+, and it is recommended that people upgrade to this UnifiOS based firmware for their CloudKey+, as this gives a much better realtime experience.

CKGP with Firmware V1.x **do NOT run UnifiOS**

In the following we are refering to Devices that do run UnifiOS as *UnifiOS Devices* and devices that do NOT run UnifiOS as *NON UnifiOS Devices*

**NOTE**: Ubiquiti has now officially launched the V2.0.24 FW for the ClodKey Gen2+ which is a UnifiOS FW. So as of V0.8.0 of this Integration, no more testing and development is done on NON UnifiOS Devices. What is already working will still be there, but there is no guarantee that new features will work on these devices.

## Prerequisites

Before you install this Integration you need to ensure that the following two settings are applied in Unifi Protect:

### UnifiOS Devices

1. **Local User**
    * Login to your *Local Portal* on your UnfiOS device, and click on *Users*
    * In the upper right corner, click on *Add User*
    * Click *Add Admin*, and fill out the form. Specific Fields to pay attention to:
      * Role: Must be *Limited Admin*
      * Account Type: *Local Access Only*
      * CONTROLLER PERMISSIONS - Under Unifi Protect, select Administrators.
    * Click *Add* in at the bottom Right.

  **HINT**: A few users have reported that they had to restart their UDMP device after creating the local user for it to work. So if you get some kind of *Error 500* when setting up the Integration, try restart the UDMP.

![ADMIN_UNIFIOS](https://github.com/briis/unifiprotect/blob/master/images/screenshots/unifi_os_admin.png)


2. **RTSP Stream**

    The Integration uses the RTSP Stream as the Live Feed source, so this needs to be enabled on each camera. With the latest versions of Unifi Protect, the stream is enabled per default, but it is recommended to just check that this is done. To check and enable the the feature
    * open Unifi Protect and click on *Devices*
    * Select *Manage* in the Menu bar at the top
    * Click on the + Sign next to RTSP
    * Enable minimum 1 stream out of the 3 available. Unifi Protect will select the Stream with the Highest resolution

### NON UnifiOS Devices (CloudKey+ with Firmware 1.x)

1. **Local User**
    * Login to Unifi Protect, and click on *Users*
    * Either select an existing User or Create a new one.
    * Specific Fields to pay attention to:
      * Roles: Must be part of *Administrators* group.
      * Local Username: Must be filled out
      * Local Password: Must be filled out

![USER Settings](https://github.com/briis/unifiprotect/blob/master/images/setup_user.png)

2. **RTSP Stream**

    The Integration uses the RTSP Stream as the Live Feed source, so this needs to be enabled on each camera. With the latest versions of Unifi Protect, the stream is enabled per default, but it is recommended to just check that this is done. To check and enable the the feature
    * open Unifi Protect and click on *Devices*
    * Select *Manage* in the Menu bar at the top
    * Click on the + Sign next to RTSP
    * Enable minimum 1 stream out of the 3 available. Unifi Protect will select the Stream with the Highest resolution

![RTSP Settings](https://github.com/briis/unifiprotect/blob/master/images/setup_rtsp.png)

## Installation
This Integration is part of the default HACS store. Search for *unifi protect* under *Integrations* and install from there. After the installation of the files you must restart Home Assistant, or else you will not be able to add UniFi Protect from the Integration Page.

If you are not familiar with HACS, or havn't installed it, I would recommend to [look through the HACS documentation](https://hacs.xyz/), before continuing. Even though you can install the Integration manually, I would recommend using HACS, as you would always be reminded when a new release is published.

**Please note**: All HACS does, is copying the needed files to Home Assistant, and placing them in the right directory. To get the Integration to work, you now need to go through the steps in the *Configuration* section.

Before you restart Home Assistant, make sure that the stream component is enabled. Open `configuration.yaml` and look for *stream:*. If not found add `stream:` somewhere in the file and save it.

## Configuration
To add *Unifi Protect* to your Home Assistant installation, go to the Integrations page inside the configuration panel and add your UniFi Protect server by providing the Host IP, Port Number, Username and Password.

**Note**: If you can't find the *Unifi Protect* integration, hard refresh your browser, when you are on the Integrations page.

If the Unifi Protect Server is found on the network it will be added to your installation. After that, you can add more Unifi Protect Servers, should you have more than one installed.

**You can only add Unifi Protect through the Integration page, Yaml configuration is no longer supported.**

### MIGRATING FROM CLOUDKEY+ V1.x
When you upgrade your CloudKey+ from FW V1.x to 2.x, your CK wil move to UnifiOS as core operating system. That also means that where you previously used port 7443 you now need to use port 443. There are two ways to fix this:
* Delete the Unifi Protect Integration and re-add it, using port 443.
* Edit the file `.storage/core.config_entries` in your Home Assistant instance. Search for Unifi Protect and change port 7443 to 443. Restart Home Assistant. (Make a backup firts)

### CONFIGURATION VARIABLES
**host**:<br>
  *(string)(Required)*<br>
  Type the IP address of your *Unifi Protect NVR*. Example: `192.168.1.1`<br>
  **Important** If you run UnifiOS this must be the IP Address. of your UDMP

**port**:<br>
  *(int)(Optional)*<br>
  The port used to communicate with the NVR. Default is 7443.<br>
  **Important** If you run UnifiOS the port *must* be specified and it must be 443.

**username**:<br>
  *(string)(Required)*<br>
  The local username you setup under the *Prerequisites* section.

**password**:<br>
  *(string)(Required)*<br>
  The local password you setup under the *Prerequisites* section.

**scan_interval**:<br>
  *(int)(Optional)*<br>
  How often the Integration polls the Unifi Protect Server for Event Updates. Set a higher value if you have many Cameras (+20). This value only is only relevant for People using a CloudKey with V1.x FW. CloudKey V2.x, UDMP and UNVR users get the data pushed, so polling not needed.<br>
  *Default value*: `2` seconds

**anonymous_snapshots**:<br>
  *(bool)(Optional)*<br>
  If you need to save a Snapshot more often than every 10 seconds, enable this function. See below for prerequisites.<br>
  *Default value*: `False`

#### ANONYMOUS SNAPSHOTS
To use the Anonymous Snapshot, you must ensure that each Camera is configured to allow this. This cannot be done in Unifi Protect, but has to be done on each individual Camera.

1. Login to each of your Cameras by going to http://CAMERA_IP. The Username is *ubnt* and the Camera Password can be found in Unifi Protect under *Settings*.
2. If you have never logged in to the Camera before, it might take you through a Setup procedure - just make sure to keep it in *Unifi Video* mode, so that it is managed by Unifi Protect.
3. Once you are logged in, you will see an option on the Front page for enabling Anonymous Snapshots. Make sure this is checked, and then press the *Save Changes* button.
4. Repeat step 3 for each of your Cameras.

## Special UniFi Protect Services
The Integration adds specific *Unifi Protect* services and supports the standard camera services. Below is a list of the *Unifi Protect* specific services:

Service | Parameters | Description
:------------ | :------------ | :-------------
`unifiprotect.save_thumbnail_image` | `entity_id` - Name of entity to retrieve thumbnail from.<br>`filename` - Filename to store thumbnail in<br>`image_width` - (Optional) Width of the image in pixels. Height will be scaled proportionally. Default is 640. | Get the thumbnail image of the last recording event (If any), from the specified camera
`unifiprotect.set_recording_mode` | `entity_id` - Name of entity to set recording mode for.<br>`recording_mode` - always, motion, never or smart| Set the recording mode for each Camera.
`unifiprotect.set_ir_mode` | `entity_id` - Name of entity to set infrared mode for.<br>`ir_mode` - auto, always_on, led_off or always_off | Set the infrared mode for each Camera.
`unifiprotect.set_status_light` | `entity_id` - Name of entity to toggle status light for.<br>`light_on` - true or false | Turn the status light on or off for each Camera.
`unifiprotect.set_doorbell_lcd_message` | `entity_id` - Name of doorbell to display message on.<br>`message` - The message to display. (Will be truncated to 30 Characters)<br>`duration` - The time in minutes the message should display. Leave blank to display always. | Display a Custom message on the LCD display on a G4 Doorbell
`unifiprotect.set_highfps_video_mode` | `entity_id` - Name of entity to toggle High FPS for.<br>`high_fps_on`  - true or false | Toggle High FPS on supported Cameras.
`unifiprotect.set_hdr_mode` | `entity_id` - Name of entity to toggle HDR for.<br>`hdr_on`  - true or false | Toggle HDR mode on supported Cameras.
`unifiprotect.set_mic_volume` | `entity_id` - Name of entity to adjust microphone volume for.<br>`level`  - a value between 0 and 100| Set Microphone sensitivity on Cameras.
`unifiprotect.set_privacy_mode` | `entity_id` - Name of entity to adjust privacy mode for.<br>`privacy_mode`  - true to enable, false to disable<br>`mic_level` - 0 to 100, where 0 is off<br>`recording_mode` - never, motion, always or smart| Set Privacy mode for a camera, where the screen goes black when enabled.
`unifiprotect.light_settings` | `entity_id` - Name of entity to adjust settings for.<br>`mode`  - When to turn on light at Motion, where off is never, motion is on motion detection and dark is only when it is dark outside.<br>`enable_at` - When motion is selected as mode, one can adjust if light turns on on motion detection. Where fulltime is always, and dark is only when dark.<br>`duration` - Number of seconds the light stays turned on. Must be one of these values: 15, 30, 60, 300, 900.<br>`sensitivity` - Motion sensitivity of the PIR. Must be a number between 1 and 100. | Adjust settings for the PIR motion sensor in the Floodlight.

**Note:** When using *camera.enable_motion_detection*, Recording in Unfi Protect will be set to *motion*. If you want to have the cameras recording all the time, you have to set that in Unifi Protect App or use the service `unifiprotect.set_recording_mode`.

## Automating Services
Below is a couple of examples on how you can automate some of the things you might do with this Integration.

### AUTOMATE SETTING RECORDING OR IR MODE
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

### CREATE INPUT SLIDER FOR MICROPHONE SENSITIVITY

To set the Microphone sensitivity you can use the Service `unifiprotect.set_mic_volume` but if you want to be able to do this from Lovelace, you can add a Input Slider for each camera and then do it from there. This shows you how you can do that.

* Go to *Configuration* and select *Helpers*.
* Click `+ ADD HELPER` and select *Number*.
* Name your Slider, and then you can leave the rest of the values as default. (Min 0, Max 100, Display mode Slider) and then click CREATE.

Now create a new Automation, that reacts to a value change of the above slider. In this case I named the slider `input_number.volume_test_cam` and the Camera is called `camera.test_cam`.

```yaml
alias: Adjust Mic Sensitivity on Test CAM
description: ''
trigger:
  - platform: state
    entity_id: input_number.volume_test_cam
condition: []
action:
  - service: unifiprotect.set_mic_volume
    data:
      entity_id: camera.test_cam
      level: '{{ states(''input_number.volume_test_cam'') | int }}'
    entity_id: ' camera.test_cam'
mode: single
```


### CONTRIBUTE TO THE PROJECT AND DEVELOPING WITH A DEVCONTAINER

1. Fork and clone the repository.

2. Open in VSCode and choose to open in devcontainer. Must have VSCode devcontainer prerequisites.

3. Run the command container start from VSCode terminal

4. A fresh Home Assistant test instance will install and will eventually be running on port 9123 with this integration running

5. When the container is running, go to http://localhost:9123 and the add Unifi Protect from the Integration Page.
