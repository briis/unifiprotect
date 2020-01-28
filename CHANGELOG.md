# Changelog

## Version 0.1.2

* `New`:
  * Added a new *Switch* component. If enabled the system will create a switch for each camera, that can enable or disable the motion recording. You can already do this by running the services `camera.enable_motion_detection` and `camera.disable_motion_detection` but this gives a convenient way to do it from the Frontend. See the [Github README.md](https://github.com/briis/unifiprotect/blob/master/README.md) for setup instructions.

## Version 0.1.1

Minor update

* `New`:
  * Added a new attribute to each binary_sensor, called *minimum_score*. This displayes the score of the last motion recording.

## Version 0.1.0

In this release you will not see a lot of new functionality. There has been a lot of change in the backend of the system as this release introduces a complete new Unifi Protect Server Wrapper. The previous implementation had a lot of calls to the Protect Server, but with this new wrapper, I have drastically reduced those calls, as all data is now stored in a memory dataset, and the wrapper just updates this dataset. With that in place we can now call an update from HASS more often, without overstretching the Protect Server. The update of the dataset is run as an Async event from the main loop. So after this update, you can delete the file `protectnvr.py`, this has been replaced by `unifi_protect_server.py` (You can just leave it where it is, but it is no longer used)

* `New Items`:
  * Added new Configuration Option `minimum_score`. (int)(Optional) Minimum Score of Motion Event before motion is triggered. Integer between 0 and 100. Default is 0, and with that value, this option is ignored  

* `Changes`:
  * A lot of changes to all modules, due to new Unifi Protect Wrapper.

## Version 0.0.10

* `New Items`:
  * Added new Icon to the Sensor, and now the Icon is changing based on Recording Mode state, so it is clear to see if motion recording is on or off
* `Fixes`:
  * Code clean-up and now all code conforms to PEP standards

## Version 0.0.9

* `camera`:
  * **BREAKING CHANGE** The service `camera.unifiprotect_save_thumbnail` has been removed, and has been replaced by a new Service you can read more about below. The implementation was not done according to Home Assistant standards, so I decided to rewrite it. If you use this Service in any automation, please replace it with the new Service.
  * A new Service with the name of `unifiprotect.save_thumbnail_image` has been created. This Service does exactly the same as the old service, but now it conforms to Home Assistant standards, and when you select it in the *Services* area under *Developer Tools* you will now see a proper Service Description. A new optional parameter has been added called `image_width`. Here you can specify the width of the image in pixels, and the height will then be scaled propotionally.
* `core`:
  * The function `set_camera_recording` was not using the *request.session*, resulting in occasional authentication errors.

## Version 0.0.8

* `camera`:
  * Attributes update more frequently, to show recording mode and online status. Let me know if this causes any issues, as I achieve this by asking the Cameras to poll status every 30 seconds, and that is usually the case for a camera entity. In my own tests I have not seen any problems.
  * Fixed missing import of *core* component
  * Added Attribute *online* - Is true when the camera is Online else shows false. This attribute can be used to check if the camera is available before performing automations.
  * Added Attribute *up_since* - showing time when camera went Online, or Offline if Camera is not connected
  * Added Attribute *last_motion* - showing time within the last 24 hours, when motion was detected, if any.
  * If the camera is not online, the recording state will now correctly be *idle*
* `core`:
  * Fixed missing string conversion of error code
  * Fixed bug in error reporting, when Authentication Failed

## Version 0.0.7

* Fixed NoneType error when one or more cameras are offline at the time of Home Assistant start
* Minor code clean-up

## Version 0.0.6

* `binary_sensor`:
  * Changed default SCAN_INTERVAL to 3 seconds to optimize Motion Detection
* `camera`:
  * Added new service `camera.unifiprotect_save_thumbnail`. When calling this services the Thumbnail of the last recorded motion will be saved to disk, and could then be used in an automation, to send to a phone via the `notify` platform. Requires `entity_id` and `filename` as attributes.
* `sensor`:
  * Added new attribute `camera_type` to the sensor. Showing what type of Unfi Camera is attached to this sensor
* `Core Module`
  * changed size of the thumbnail image when being created.
  * fixed error when no *Last Motion* record exist
  * cleaned up the code, removing obsolete parts.
  