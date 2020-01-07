# Unifi Protect for Home Assistant
This is a Home Assistant Integration for Ubiquiti's Unifi Protect Surveillance system.

This Home Assistant integration is inspired by [danielfernau's video downloader program](https://github.com/danielfernau/unifi-protect-video-downloader) and the Authorization implementation is copied from there.

Basically what this does, is integrating the Camera feeds from Unifi Protect in to Home Assistant, and furthermore there is an option to get Binary Motion Sensors and Sensors that show the current Recording Settings pr. camera.

Once setup you will have the Camera feed from Unifi Protect going into Home Assistant, and you can have Binay Motion Sensors if recording is enabled in Unifi Protect. A sensor indicating the recording state, is also created for each camera if enabled in Home Assistant.

**Note:** Please read the [README.md file on Github](https://github.com/briis/unifiprotect/blob/master/README.md) before installing, as there are some Prerequisites that need to be met, before this will work properly.

## Configuration
Start by configuring the core platform. No matter which of the entities you activate, this has to be configured. The core platform by itself does nothing else than establish a link the *Unifi Protect NVR*, so by activating this you will not see any entities being created in Home Assistant.

Edit your *configuration.yaml* file and add the *unifiprotect* component to the file:
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

**Remember** 
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
