
# // Unifi Protect for Home Assistant

![GitHub release (latest by date)](https://img.shields.io/github/v/release/briis/unifiprotect?style=flat-square) [![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg?style=flat-square)](https://github.com/custom-components/hacs) [![](https://img.shields.io/badge/COMMUNITY-FORUM-success?style=flat-square)](https://community.home-assistant.io/t/custom-component-unifi-protect/158041)

The Unifi Protect Integration adds support for retrieving Camera feeds and Sensor data from a Unifi Protect installation on either a Ubiquiti CloudKey+ or Ubiquiti Unifi Dream Machine Pro.

There is support for the following device types within Home Assistant:
* Camera
* Sensor
* Binary Sensor
* Switch

It supports both regular Ubiquiti Cameras and the Unifi Doorbell. Camera feeds, Motion Sensors, Doorbell Sensors, Motion Setting Sensors and Switches will be created automativally for each Camera found, once the Integration has been configured.

## Prerequisites

Before you install this Integration you need to ensure that the following two settings are applied in Unifi Protect:

1. **Local User**
  * If Unifi Protect is installed on a **UDMP**, then you can skip this step, and instead use the username and password you use to login to the UDMP. But it is recommended that you add a specific user on your UDMP, as described [here](https://community.home-assistant.io/t/custom-component-unifi-protect/158041/138?u=briis)
  * If your are on a **CloudKey+** then open Unifi Protect in your browser. Click the USERS tab and you will get a list of users. Either select an existing user, or create a new one. The important thing is that the user is part of *Administrators* and that a local username and password is set for that user. This is the username and password you will use when setting up the Integration later.
2. **RTSP Stream** Select each camera under the CAMERAS tab, click on the camera and you will get a menu on the right side. Click the MANAGE button and there will be a menu like the picture below. (If you can't see the same picture click the + sign to the right of RTSP). Make sure that at least one of the streams is set to on. It does not matter which one, or if you select more than one, the integration will pick the one with the highest resolution.

![USER Settings](https://github.com/briis/unifiprotect/blob/master/images/setup_user.png) ![RTSP Settings](https://github.com/briis/unifiprotect/blob/master/images/setup_rtsp.png)

**Note:**

* This has been testet on a Cloud Key Gen2+ with Unifi Protect Controller version 1.13.3-beta.4 and higher. It will not work on a lower version than that due to the support of the Doorbell.
* As of version 0.3.0, this Integration also supports the UDM Pro with UnifiOS, thanks to the work of @msvinth. You need the version of Unifi Protect that supports the Doorbell, or this Integration will fail.

## Installation
This Integration is part of the default HACS store. Search for *unifi protect* under *Integrations* and install from there.

## Configuration
To add *Unifi Protect* to your Home Assistant installation, go to the Integrations page inside the configuration panel and add a CloudKey+ or UDMP by providing the Host IP, Port Number, Username and Password.

If the Unifi Protect Server is found on the network it will be added to your installation. After that, you can add more Unifi Protect Servers, should have more than one installed.

**You can only add Unifi Protect through the Integration page, Yaml configuration is no longer supported.**

### CONFIGURATION VARIABLES
**host**:<br>
  *(string)(Required)*<br>
  Type the IP address of your *Unifi Protect NVR*. Example: `192.168.1.10`<br>
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
  How often the Integration polls the Unifi Protect Server for Event Updates. Set a higher value if you have many Cameras (+20).<br>
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

### SPECIAL UNIFI PROTECT SERVICES
The Integration adds specific *Unifi Protect* services and supports the standard camera services. Below is a list of the *Unifi Protect* specific services:

Service | Parameters | Description
:------------ | :------------ | :-------------
`unifiprotect.save_thumbnail_image` | `entity_id` - Name of entity to retrieve thumbnail from.<br>`filename` - Filename to store thumbnail in<br>`image_width` - (Optional) Width of the image in pixels. Height will be scaled proportionally. Default is 640. | Get the thumbnail image of the last recording event (If any), from the specified camera
`unifiprotect.set_recording_mode` | `entity_id` - Name of entity to set recording mode for.<br>`recording_mode` - always, motion or never | Set the recording mode for each Camera.
`unifiprotect.set_ir_mode` | `entity_id` - Name of entity to set infrared mode for.<br>`ir_mode` - auto, always_on, led_off or always_off | Set the infrared mode for each Camera.

**Note:** When using *camera.enable_motion_detection*, Recording in Unfi Protect will be set to *motion*. If you want to have the cameras recording all the time, you have to set that in Unifi Protect App or use the service `unifiprotect.set_recording_mode`.

### AUTOMATING SERVICES
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

### CONTRIBUTE TO THE PROJECT AND DEVELOPING WITH A DEVCONTAINER

1. Fork and clone the repository.

2. Open in VSCode and choose to open in devcontainer. Must have VSCode devcontainer prerequisites.

3. Run the command container start from VSCode terminal

4. A fresh Home Assistant test instance will install and will eventually be running on port 9123 with this integration running

5. When the container is running, go to http://localhost:9123 and the add Unifi Protect from the Integration Page.
