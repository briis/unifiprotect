# Changelog

## Version 0.1.0

* `New Items`:
  * Added new Configuration Option `minimum_score`. With this option you can supply an integer between 0 and 100. This

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
  