# // Changelog

## 0.12.0

0.12.0 was originally planned as a beta only release, but after giving it more thought, I figured it would be be great to mark it as stable for the folks that cannot upgrade to the HA core version in 2022.2.

This release is primarily fixes from the HA core process. There is also full support added for the G4 Doorbell Pro, the UP Sense.

This will be the **last** HACS release. After this point, the HACS repo is considered deprecated. We will still take issues in the repo as if people prefer to make them here instead of the HA core repo. But after a month or 2 we plan to archive the repo and have the integration removed from HACS.

### Differences between HACS version 0.12.0 and HA 2022.2.0b1 version:

#### HACS Only

* Migration code for updating from `0.10.x` or older still exists; this code has been _removed_ in the HA core version

#### HA Core Only

* Full language support. All of the languages HA core supports via Lokalise has been added to the ingration.

* Auto-discovery. If you have a Dream machine or a Cloud Key/UNVR on the same VLAN, the UniFi Protect integration will automatically be discovered and prompted for setup.

* UP Doorlock support. The HA core version has full support for the newly release EA UP Doorlock.

### Changes

* `CHANGE`: **BREAKING CHANGE** Removes all deprecations outlined in the 0.11.x release.

* `CHANGE`: **BREAKING CHANGE** The "Chime Duration" number entity has been replaced with a "Chime Type" select entity. This makes Home Assistant work the same way as UniFi Protect. (https://github.com/briis/unifiprotect/issues/451)

* `CHANGE`: **BREAKING CHANGE** Smart Sensor support has been overhauled and improved. If you have Smart Sensors, it is _highly recommended to delete your UniFi Protect integration config and re-add it_. Some of the categories for the sensors have changed and it is not easy to change those without re-adding the integration. The sensors for the Smart Sensor are may also appear unavaiable if that sensor is not configured to be abled. For example, if your have motion disabled on your Sensor in UniFi Protect, the motion sensor will be unavaiable in Home Assistnat. Full list of new Smart Sensor entites:

  * Alarm Sound and Tampering binary sensors
  * Motion Sensitivity number
  * Mount Type and Paired Camera selects
  * Status Light switch
  * Configuration switches for various sensors:
    * Motion Detection switch
    * Temperature Sensor switch
    * Humidity Sensor switch
    * Light Sensor switch
    * Alarm Sound Detection switch

* `CHANGE`: **BREAKING CHANGE** Removes `profile_ws` debug service. Core plans to add a more centralized way of getting debug information from an integration. This will be back in some form after that feature is added (estimate: 1-2 major core releases).

* `CHANGE`: **BREAKING CHANGE** Removes `event_thumbnail` attribute and associated `ThumbnailProxyView`. After a lot of discussion, core does not want to add more attributes with access tokens inside of attributes. We plan to add back event thumbnails in some form again. If you would like to follow along with the dicussion, checkout the [architecure dicussion for it](https://github.com/home-assistant/architecture/discussions/705).

* `CHANGE`: Switches Doorbell binary_sensor to use `is_ringing` attr, should great improve relaiability of the sensor

* `CHANGE`: Dynamic select options for Doorbell Text

* `CHANGE`: Improves names for a number of entities

* `CHANGE`: Adds a bunch of extra debug logging for entity updates

* `NEW`: Adds full support for the package camera for the G4 Doorbell Pro. It should now always be enabled by default (if you are upgrading from an older version, it will still be disabled). The snapshot for the Package Camera has also been fixed. Since the camera if only 2 FPS, _streaming is disabled_ to prevent buffering.

* `FIX`: Overhaul of the Websocket code. Websocket reconnects should be drastically improved. Hopefully all reconnnect issues should be gone now.

* `FIX`: Fixes NVR memory sensor if no data is reported

* `FIX`: Fixes spelling typo with Recording Capacity sensor (https://github.com/briis/unifiprotect/issues/440)

* `FIX`: Fixes `is_connected` check for cameras

* `FIX`: Adds back `last_trip_time` attribute to camera motion entity

* `FIX`: Fixes NVR memory sensor if no data is reported

* `FIX`: Fixes spelling typo with Recording Capacity sensor (https://github.com/briis/unifiprotect/issues/440)

* `FIX`: Further improves relibility of Doorbell binary_sensor

* `FIX`: Fixes voltage unit for doorbell voltage sensor

* `FIX`: Fixes `connection_host` for Cameras so it can have DNS hosts in addition to IPs.

* `FIX`: Improves relibility of entities when UniFi Protect goes offline and/or a device goes offline. Everything recovery seemlessly when UniFi Protect upgrades or firmware updates are applied (fixes https://github.com/briis/unifiprotect/issues/432).

* `FIX`: Improves relibility of `media_player` entities so they should report state better and be able to play longer audio clips.

* `FIX`: Fixes stopping in progress audio for `media_player` entities.

* `FIX`: Allows DNS hosts in addition to IP addresses (fixes https://github.com/briis/unifiprotect/issues/431).

* `FIX`: Fixes selection of default camera entity for when it is not the High Quality channel.

* `FIX`: Fixes https://github.com/briis/unifiprotect/issues/428. All string enums are now case insensitive.

* `FIX`: Fixes https://github.com/briis/unifiprotect/issues/427, affected cameras will automatically be converted to Detections recording mode.

## 0.12.0-beta10

This is the last planned release for the HACS version. This release primarily adds new features for the G4 Doorbell Pro and the Smart Sensor. This release does unfortunatly have a couple of breaking changes for people with doorbells and Smart Sensors which are avoidable due to how soon the Home Assistant core release is.

* `CHANGE`: **BREAKING CHANGE** The "Chime Duration" number entity has been replaced with a "Chime Type" select entity. This makes Home Assistant work the same way as UniFi Protect. (https://github.com/briis/unifiprotect/issues/451)

* `CHANGE`: **BREAKING CHANGE** Smart Sensor support has been overhauled and improved. If you have Smart Sensors, it is _highly recommended to delete your UniFi Protect integration config and re-add it_. Some of the categories for the sensors have changed and it is not easy to change those without re-adding the integration. The sensors for the Smart Sensor are may also appear unavaiable if that sensor is not configured to be abled. For example, if your have motion disabled on your Sensor in UniFi Protect, the motion sensor will be unavaiable in Home Assistnat. Full list of new Smart Sensor entites:

  * Alarm Sound and Tampering binary sensors
  * Motion Sensitivity number
  * Mount Type and Paired Camera selects
  * Status Light switch
  * Configuration switches for various sensors:
    * Motion Detection switch
    * Temperature Sensor switch
    * Humidity Sensor switch
    * Light Sensor switch
    * Alarm Sound Detection switch

* `CHANGE`: Adds full support for the package camera for the G4 Doorbell Pro. It should now always be enabled by default (if you are upgrading from an older version, it will still be disabled). The snapshot for the Package Camera has also been fixed. Since the camera if only 2 FPS, _streaming is disabled_ to prevent buffering.

* `FIX`: Overhaul of the Websocket code. Websocket reconnects should be drastically improved. Hopefully all reconnnect issues should be gone now.

## 0.12.0-beta9

Home Assistant core port complete! The version that is in `2022.2` will officially have all of the same features. This is the final backport version to make sure the two versions are equal. The only difference between `0.12.0-beta9` and the code in `2022.2` is

* Migration code from `< 0.11.x` has been dropped. You must be on at least `0.11.0` or newer to migrate to the Home Assistant core version.

Additionally, we could not add _every_ feature from the HACS version to the HA core version so there are 2 additional breaking changes in this release (sorry!):

* `CHANGE`: **BREAKING CHANGE** Removes `profile_ws` and `take_sample` debug services. Core plans to add a more centralized way of getting debug information from an integration. This will be back in some form after that feature is added (estimate: 1-2 major core releases).

* `CHANGE`: **BREAKING CHANGE** Removes `event_thumbnail` attribute and associated `ThumbnailProxyView`. After a lot of discussion, core does not want to add more attributes with access tokens inside of attributes. We plan to add back event thumbnails in some form again. If you would like to follow along with the dicussion, checkout the [architecure dicussion for it](https://github.com/home-assistant/architecture/discussions/705).

Going forward, there will be some new features for the 0.12.0-beta / core version that will be developed for core version and then be backported to the HACS version. These include improvements for the G4 Doorbell Pro and the UP Sense devices.

## 0.12.0-beta8

* `FIX`: Fixes NVR memory sensor if no data is reported

* `FIX`: Fixes spelling typo with Recording Capacity sensor (https://github.com/briis/unifiprotect/issues/440)

* `FIX`: Fixes `is_connected` check for cameras

* `FIX`: Adds back `last_trip_time` attribute to camera motion entity

## 0.12.0-beta7

* `FIX`: Fixes NVR memory sensor if no data is reported

* `FIX`: Fixes spelling typo with Recording Capacity sensor (https://github.com/briis/unifiprotect/issues/440)

* `FIX`: Fixes is_connected check for cameras

* `FIX`: Adds back `last_trip_time` attribute to camera motion entity

## 0.12.0-beta7

* `FIX`: Improve relibility of Websocket reconnects

* `FIX`: Further improves relibility of Doorbell binary_sensor

## 0.12.0-beta6

* `CHANGE`: Switches Doorbell binary_sensor to use `is_ringing` attr, should great improve relaiability of the sensor

* `NEW`: Adds `take_sample` service to help with debugging/issue reporting

* `FIX`: Fixes voltage unit for doorbell voltage sensor

Backports changes from Home Assistant core merge process:

* `CHANGE`: Dynamic select options for Doorbell Text

* `CHANGE`: Improves names for a number of entities

* `CHANGE`: Adds a bunch of extra debug logging for entity updates

## 0.12.0-beta5

* `FIX`: Fixes `connection_host` for Cameras so it can have DNS hosts in addition to IPs.

## 0.12.0-beta4

Backports fixes from Home Assistant core merge process:

* `FIX`: Improves relibility of entities when UniFi Protect goes offline and/or a device goes offline. Everything recovery seemlessly when UniFi Protect upgrades or firmware updates are applied (fixes https://github.com/briis/unifiprotect/issues/432).

* `FIX`: Improves relibility of `media_player` entities so they should report state better and be able to play longer audio clips.

* `FIX`: Fixes stopping in progress audio for `media_player` entities.

* `FIX`: Allows DNS hosts in addition to IP addresses (fixes https://github.com/briis/unifiprotect/issues/431).

* `FIX`: Fixes selection of default camera entity for when it is not the High Quality channel.

## 0.12.0-beta3

* `FIX`: Fixes https://github.com/briis/unifiprotect/issues/428. All string enums are now case insensitive.

## 0.12.0-beta2

* `FIX`: Fixes https://github.com/briis/unifiprotect/issues/427, affected cameras will automatically be converted to Detections recording mode.

## 0.12.0-beta1

The 0.12.0-beta is designed to be a "beta only" release. There will not be a stable release for it. It is designed to test the final changes needed to merge the unifiprotect into Home Assistant core.

* `CHANGE`: **BREAKING CHANGE** Removes all deprecations outlined in the 0.11.x release.

## 0.11.2

* `FIX`: Setting up camera entities will no longer error if a camera does not have a channel. Will now result in log and continue

* `FIX`: Unadopted entities are ignored (fixes #420)

* `FIX`: Event thumbnails now return instantly using newer endpoint from UniFi Protect. They appear to come back as a camera snapshot until after the events ends, but they should always return an image now.

## 0.11.1

### Deprecations

As an amended to the deprecations from 0.11.0, the `last_tripped_time` is _no longer_ deprecated as `last_changed` is not a full replacement (#411)

### Other changes

* `FIX`: Bumps version of `pyunifiprotect` to 1.3.4. This will fix talkback for all cameras that was not working as expected

## 0.11.0

### Deprecations

0.11 is last major release planned before we merge the `unifiprotect` integration into core. As a result, a number of features are being removed when we merged into core.

The following services will be removed in the next version:

* `unifiprotect.set_recording_mode` -- use the select introduced in 0.10 instead
* `unifiprotect.set_ir_mode` -- use the select entity introduced in 0.10 instead
* `unifiprotect.set_status_light` -- use the switch entity on the camera device instead
* `unifiprotect.set_hdr_mode` -- use the switch entity on the camera device instead
* `unifiprotect.set_highfps_video_mode` -- use the switch entity on the camera device instead
* `unifiprotect.set_doorbell_lcd_message` -- use the select entity introduced in 0.10 instead
* `unifiprotect.set_mic_volume` -- use the number entity introduced in 0.10 instead
* `unifiprotect.set_privacy_mode` -- use the switch entity introduced in 0.10 instead
* `unifiprotect.set_zoom_position` -- use the number entity introduced in 0.10 instead
* `unifiprotect.set_wdr_value` -- use the number entity introduced in 0.10 instead
* `unifiprotect.light_settings` -- use the select entity introduced in 0.10 instead
* `unifiprotect.set_viewport_view` -- use the select entity introduced in 0.10 instead

The following events will be removed in the next version:

* `unifiprotect_doorbell` -- use a State Changed event on "Doorbell" binary sensor on the device instead
* `unifiprotect_motion` -- use a State Changed event on the "Motion" binary sensor on the device instead

The following entities will be removed in the next version:

* The "Motion Recording" sensor for cameras (in favor of the "Recording Mode" select)
* The "Light Turn On" sensor for flood lights (in favor of the "Lighting" select)

All of following attributes should be duplicated data that can be gotten from other devices/entities and as such, they will be removed in the next version.

* `device_model` will be removed from all entities -- provided in the UI as part of the "Device Info"
* `last_tripped_time` will be removed from binary sensor entities -- use the `last_changed` value provided by the [HA state instead](https://www.home-assistant.io/docs/configuration/state_object/)
* `up_since` will be removed from camera and light entities -- now has its own sensor. The sensor is disabled by default so you will need to enable it if you want to use it.
* `enabled_at` will be removed from light entities -- now has its own sensor
* `camera_id` will be removed from camera entities -- no services need the camera ID anymore so it does not need to be exposed as an attribute. You can still get device IDs for testing/debugging from the Configuration URL in the "Device Info" section
* `chime_duration`, `is_dark`, `mic_sensitivity`, `privacy_mode`, `wdr_value`, and `zoom_position`  will be removed from camera entities -- all of them have now have their own sensors
* `event_object` will be removed from the Motion binary sensor. Use the dedicated Detected Object sensor.

### Breaking Changes in this release

* `CHANGE`: **BREAKING CHANGE** The internal name of the Privacy Zone controlled by the "Privacy Mode" switch has been changed. Make sure you turn off all of your privacy mode switches before upgrading. If you do not, you will need to manually delete the old Privacy Zone from your UniFi Protect app.

* `CHANGE`: **BREAKING CHANGE** WDR `number` entity has been removed from Cameras that have HDR. This is inline with changes made to Protect as you can no longer control WDR for cameras with HDR.

* `CHANGE`: **BREAKING CHANGE** the `event_length` attribute has been removed from the motion and door binary sensors. The value was previously calculated in memory and not reliable between restarts.

* `CHANGE`: **BREAKING CHANGE** the `event_object` attribute for binary motion sensors has changed the value for no object detected from "None Identified" (string) to "None" (NoneType/null)

* `CHANGE`: **BREAKING CHANGE** The Doorbell Text select entity for Doorbells has been overhauled. The Config Flow option for Doorbell Messages has been removed. You now can use the the  `unifiprotect.add_doorbell_text` and `unifiprotect.remove_doorbell_text` services to add/remove Doorbell messages. This will persist the messages in UniFi Protect and the choices will now be the same ones that appear in the UniFi Protect iOS/Android app. **NOTE**: After running one of these services, you must restart Home Assistant for the updated options to appear.

### Other Changes in this release

* `CHANGE`: Migrates `UpvServer` to new `ProtectApiClient` from `pyunifiprotect`.
    * This should lead to a number of behind-the-scenes reliability improvements.
      * Should fix/close the following issues: #248, #255, #297, #317, #341, and #360 (TODO: Verify)

* `CHANGE`: Overhaul Config Flow
    * Adds Reauthentication support
    * Adds "Verify SSL"
    * Updates Setup / Reauth / Options flows to pre-populate forms from existing settings
    * Removes changing username/password as part of the options flow as it is redundant with Reauthentication support
    * Removes Doorbell Text option since it is handled directly by UniFi Protect now
    * Adds new config option to update all metrics (storage stat usage, uptimes, CPU usage, etc.) in realtime. **WARNING**: Enabling this option will greatly increase your CPU usage. ~2x is what we were seeing in our testing. It is recommended to leave it disabled for now as we do not have a lot of diagnostic sensors using this data yet.

* `CHANGE`: The state of the camera entities now reflects on whether the camera is actually recording. If you set your Recording Mode to "Detections", your camera will switch back and forth between "Idle" and "Recording" based on if the camera is actually recording.
  * Closes #337

* `CHANGE`: Configuration URLs for UFP devices will now take you directly to the device in the UFP Web UI.

* `CHANGE`: Default names for all entities have been updated from `entity_name device_name` to `device_name entity_name` to match how Home Assistant expects them in 2021.11+

* `CHANGE`: The Bluetooth strength sensor for the UP Sense is now disabled by default (will not effect anyone that already has the sensor).

* `NEW`: Adds `unifiprotect.set_doorbell_message` service. This is just like the `unifiprotect.set_doorbell_lcd_message`, but it is not deprecated and it requires the Doorbell Text Select entity instead of the Camera entity. Should **only** be used to set dynamic doorbell text messages (i.e. setting the current outdoor temperate on your doorbell). If you want to use static custom messages, use the Doorbell Text Select entity and the `unifiprotect.add_doorbell_text` / `unifiprotect.remove_doorbell_text` service. `unifiprotect.set_doorbell_lcd_message` is still deprecated and will still be removed in the next release.
  * Closes #396

* `NEW`: Adds "Override Connection Host" config option. This will force your RTSP(S) connection IP address to be the same as everything else. Should only be used if you need to forcibly use a different IP address.
  * For sure closes #248

* `NEW`: Added Dark Mode brand images to https://github.com/home-assistant/brands.

* `NEW`: Adds `phy_rate` and `wifi_signal` sensors so all connection states (BLE, WiFi and Wired) should have a diagnostic sensor. Disabled by default. Requires "Realtime metrics" option to update in realtime.

* `NEW`: Added Detected Object sensor for cameras with smart detections. Values are `none`, `person` or `vehicle`. Contains `event_score` and `event_thumb` attributes.
  * Closes #342

* `NEW`: Adds Paired Camera select entity for Viewports

* `NEW`: Adds "Received Data", "Transferred Data", "Oldest Recording", "Storage Used", and "Disk Write Rate" sensors for cameras. Disabled by default. Requires "Realtime metrics" option to update in realtime.

* `NEW`: (requires UniFi Protect 1.20.1) Adds "Voltage" sensor for doorbells. Disabled by default.

* `NEW`: Adds "System Sounds" switch for cameras with speakers

* `NEW`: Adds switches to toggle overlay information for video feeds on all cameras

* `NEW`: Adds switches to toggle smart detection types on cameras with smart detections

* `NEW`: Adds event thumbnail proxy view.
  * URL is `/api/ufp/thumbnail/{thumb_id}`. `thumb_id` is the ID of the thumbnail from UniFi Protect.
  * `entity_id` is a required query parameters. `entity_id` be for an sensor that has event thumbnails on it (like the Motion binary sensor)
  * `token` is a required query parameter is you are _not_ authenticated. It is an attribute on the motion sensor for the Camera
  * `w` and `h` are optional query string params for thumbnail resizing.

* `NEW`: Adds `event_thumbnail` attribute to Motion binary sensor that uses above mentioned event thumbnail proxy view.

* `NEW`: Adds NVR sensors. All of them are disabled by default. All of the sensors will only update every ~15 minutes unless the "Realtime metrics" config option is turned on. List of all sensors:
    * Disk Health (one per disk)
    * System Info: CPU Temp, CPU, Memory and Storage Utilization
    * Uptime
    * Recording Capacity (in seconds)
    * Distributions of stored video for Resolution (4K/HD/Free)
    * Distributions of stored video for Type (Continuous/Detections/Timelapse)

* More clean up and improvements for upcoming Home Assistant core merge.

* Adds various new blueprints to help users automate UniFi Protect. New [Blueprints can be found in the README](https://github.com/briis/unifiprotect#automating-services)

## 0.11.0-beta.5

* `FIX`: Fixes motion events and sensors for UP-Sense devices (#405)

* `FIX`: Fixes error on start up for G4 Domes (#408)

## 0.11.0-beta.4

* `NEW`: Adds `unifiprotect.set_doorbell_message` service. This is just like the `unifiprotect.set_doorbell_lcd_message`, but it is not deprecated and it requires the Doorbell Text Select entity instead of the Camera entity. Should **only** be used to set dynamic doorbell text messages (i.e. setting the current outdoor temperate on your doorbell). If you want to use static custom messages, use the Doorbell Text Select entity and the `unifiprotect.add_doorbell_text` / `unifiprotect.remove_doorbell_text` service. `unifiprotect.set_doorbell_lcd_message` is still deprecated and will still be removed in the next release.
  * Closes #396

* `NEW`: Adds "Override Connection Host" config option. This will force your RTSP(S) connection IP address to be the same as everything else. Should only be used if you need to forcibly use a different IP address.
  * For sure closes #248

* `FIX`: Reset event_thumbnail attribute for Motion binary sensor after motion has ended

* `FIX`: Change unit for signal strength from db to dbm. (fixes Camera Wifi Signal Strength should be dBm not dB)
  * Closes #394

* `NEW`: Added Dark Mode brand images to https://github.com/home-assistant/brands.

## 0.11.0-beta.3

* `DEPRECATION`: The Motion binary sensor will stop showing details about smart detections in the next version. Use the new separate Detected Object sensor. `event_object` attribute will be removed as well.

* `NEW`: Adds `phy_rate` and `wifi_signal` sensors so all connection states (BLE, WiFi and Wired) should have a diagnostic sensor. Disabled by default. Requires "Realtime metrics" option to update in realtime.

* `NEW`: Added Detected Object sensor for cameras with smart detections. Values are `none`, `person` or `vehicle`. Contains `event_score` and `event_thumb` attributes.
  * Closes #342

* `NEW`: Adds Paired Camera select entity for Viewports

* `NEW`: Adds "Received Data", "Transferred Data", "Oldest Recording", "Storage Used", and "Disk Write Rate" sensors for cameras. Disabled by default. Requires "Realtime metrics" option to update in realtime.

* `NEW`: (requires UniFi Protect 1.20.1) Adds "Voltage" sensor for doorbells. Disabled by default.

* `NEW`: Adds "System Sounds" switch for cameras with speakers

* `NEW`: Adds switches to toggle overlay information for video feeds on all cameras

* `NEW`: Adds switches to toggle smart detection types on cameras with smart detections

## 0.11.0-beta.2

* `CHANGE`: Allows `device_id` parameter for global service calls to be any device from a UniFi Protect instance

* `NEW`: Adds event thumbnail proxy view.
  * URL is `/api/ufp/thumbnail/{thumb_id}`. `thumb_id` is the ID of the thumbnail from UniFi Protect.
  * `entity_id` is a required query parameters. `entity_id` be for an sensor that has event thumbnails on it (like the Motion binary sensor)
  * `token` is a required query parameter is you are _not_ authenticated. It is an attribute on the motion sensor for the Camera
  * `w` and `h` are optional query string params for thumbnail resizing.

* `NEW`: Adds `event_thumbnail` attribute to Motion binary sensor that uses above mentioned event thumbnail proxy view.

* `NEW`: Adds NVR sensors. All of them are disabled by default. All of the sensors will only update every ~15 minutes unless the "Realtime metrics" config option is turned on. List of all sensors:
    * Disk Health (one per disk)
    * System Info: CPU Temp, CPU, Memory and Storage Utilization
    * Uptime
    * Recording Capacity (in seconds)
    * Distributions of stored video for Resolution (4K/HD/Free)
    * Distributions of stored video for Type (Continuous/Detections/Timelapse)

* More clean up and improvements for upcoming Home Assistant core merge.

## 0.11.0-beta.1

### Deprecations

0.11 is last major release planned before we merge the `unifiprotect` integration into core. As a result, a number of features are being removed when we merged into core.

The following services will be removed in the next version:

* `unifiprotect.set_recording_mode` -- use the select introduced in 0.10 instead
* `unifiprotect.set_ir_mode` -- use the select entity introduced in 0.10 instead
* `unifiprotect.set_status_light` -- use the switch entity on the camera device instead
* `unifiprotect.set_hdr_mode` -- use the switch entity on the camera device instead
* `unifiprotect.set_highfps_video_mode` -- use the switch entity on the camera device instead
* `unifiprotect.set_doorbell_lcd_message` -- use the select entity introduced in 0.10 instead
* `unifiprotect.set_mic_volume` -- use the number entity introduced in 0.10 instead
* `unifiprotect.set_privacy_mode` -- use the switch entity introduced in 0.10 instead
* `unifiprotect.set_zoom_position` -- use the number entity introduced in 0.10 instead
* `unifiprotect.set_wdr_value` -- use the number entity introduced in 0.10 instead
* `unifiprotect.light_settings` -- use the select entity introduced in 0.10 instead
* `unifiprotect.set_viewport_view` -- use the select entity introduced in 0.10 instead

The following events will be removed in the next version:

* `unifiprotect_doorbell` -- use a State Changed event on "Doorbell" binary sensor on the device instead
* `unifiprotect_motion` -- use a State Changed event on the "Motion" binary sensor on the device instead

The following entities will be removed in the next version:

* The "Motion Recording" sensor for cameras (in favor of the "Recording Mode" select)
* The "Light Turn On" sensor for flood lights (in favor of the "Lighting" select)

All of following attributes should be duplicated data that can be gotten from other devices/entities and as such, they will be removed in the next version.

* `device_model` will be removed from all entities -- provided in the UI as part of the "Device Info"
* `last_tripped_time` will be removed from binary sensor entities -- use the `last_changed` value provided by the [HA state instead](https://www.home-assistant.io/docs/configuration/state_object/)
* `up_since` will be removed from camera and light entities -- now has its own sensor. The sensor is disabled by default so you will need to enable it if you want to use it.
* `enabled_at` will be removed from light entities -- now has its own sensor
* `camera_id` will be removed from camera entities -- no services need the camera ID anymore so it does not need to be exposed as an attribute. You can still get device IDs for testing/debugging from the Configuration URL in the "Device Info" section
* `chime_duration`, `is_dark`, `mic_sensitivity`, `privacy_mode`, `wdr_value`, and `zoom_position`  will be removed from camera entities -- all of them have now have their own sensors


### Breaking Changes in this release

* `CHANGE`: **BREAKING CHANGE** The internal name of the Privacy Zone controlled by the "Privacy Mode" switch has been changed. Make sure you turn off all of your privacy mode switches before upgrading. If you do not, you will need to manually delete the old Privacy Zone from your UniFi Protect app.

* `CHANGE`: **BREAKING CHANGE** WDR `number` entity has been removed from Cameras that have HDR. This is inline with changes made to Protect as you can no longer control WDR for cameras with HDR.

* `CHANGE`: **BREAKING CHANGE** the `event_length` attribute has been removed from the motion and door binary sensors. The value was previously calculated in memory and not reliable between restarts.

* `CHANGE`: **BREAKING CHANGE** the `event_object` attribute for binary motion sensors has changed the value for no object detected from "None Identified" (string) to "None" (NoneType/null)

* `CHANGE`: **BREAKING CHANGE** The Doorbell Text select entity for Doorbells has been overhauled. The Config Flow option for Doorbell Messages has been removed. You now can use the the  `unifiprotect.add_doorbell_text` and `unifiprotect.remove_doorbell_text` services to add/remove Doorbell messages. This will persist the messages in UniFi Protect and the choices will now be the same ones that appear in the UniFi Protect iOS/Android app. **NOTE**: After running one of these services, you must restart Home Assistant for the updated options to appear.

### Other Changes in this release

* `CHANGE`: Migrates `UpvServer` to new `ProtectApiClient` from `pyunifiprotect`.
    * This should lead to a number of behind-the-scenes reliability improvements.
      * Should fix/close the following issues: #248, #255, #297, #317, #341, and #360 (TODO: Verify)

* `CHANGE`: Overhaul Config Flow
    * Adds Reauthentication support
    * Adds "Verify SSL"
    * Updates Setup / Reauth / Options flows to pre-populate forms from existing settings
    * Removes changing username/password as part of the options flow as it is redundant with Reauthentication support
    * Removes Doorbell Text option since it is handled directly by UniFi Protect now
    * Adds new config option to update all metrics (storage stat usage, uptimes, CPU usage, etc.) in realtime. **WARNING**: Enabling this option will greatly increase your CPU usage. ~2x is what we were seeing in our testing. It is recommended to leave it disabled for now as we do not have a lot of diagnostic sensors using this data yet.

* `CHANGE`: The state of the camera entities now reflects on whether the camera is actually recording. If you set your Recording Mode to "Detections", your camera will switch back and forth between "Idle" and "Recording" based on if the camera is actually recording.
  * Closes #337

* `CHANGE`: Configuration URLs for UFP devices will now take you directly to the device in the UFP Web UI.

* `CHANGE`: Default names for all entities have been updated from `entity_name device_name` to `device_name entity_name` to match how Home Assistant expects them in 2021.11+

* `CHANGE`: The Bluetooth strength sensor for the UP Sense is now disabled by default (will not effect anyone that already has the sensor).

* `NEW`: Adds all of the possible enabled UFP Camera channels as different camera entities; only the highest resolution secure (RTSPS) one is enabled by default. If you need RTSP camera entities, you can enable one of the given insecure camera entities.

* `NEW`: Added the following attributes to Camera entity: `width`, `height`, `fps`, `bitrate` and `channel_id`

* `NEW`: Added status light switch for Flood Light devices

* `NEW`: Added "On Motion - When Dark" option for Flood Light Lighting switch

* `NEW`: Added "Auto-Shutoff Timer" number entity for Flood Lights

* `NEW`: Added "Motion Sensitivity" number entity for Flood Lights

* `NEW`: Added "Chime Duration" number entity for Doorbells

* `NEW`: Added "Uptime" sensor entity for all UniFi Protect adoptable devices. This is disabled by default.

* `NEW`: Added `unifiprotect.set_default_doorbell_text` service to allow you to set your default Doorbell message text. **NOTE**: After running this service, you must restart Home Assistant for the default to be reflected in the options.

* `NEW`: Added "SSH Enabled" switch for all adoptable UniFi Protect devices. This switch is disabled by default.

* `NEW`: (requires 2021.12+) Added "Reboot Device" button for all adoptable UniFi Protect devices. This button is disabled by default. Use with caution as there is no confirm. "Pressing" it instantly reboots your device.

* `NEW`: Added media player entity for cameras with speaker. Speaker will accept any ffmpeg playable audio file URI (URI must be accessible from _Home Assistant_, not your Camera). TTS works great!
  * TODO: Investigate for final release. This _may_ not work as expected on G4 Doorbells. Not sure yet if it is because of the recent Doorbell issues or because Doorbells are different.
  * Implements #304


## 0.10.0

Released: 2021-11-24

> **YOU MUST BE RUNNING V1.20.0 OF UNIFI PROTECT, TO USE THIS VERSION OF THE INTEGRATION. IF YOU ARE STILL ON 1.19.x STAY ON THE 0.9.2 RELEASE.

As UniFi Protect V1.20.0 is now released, we will also ship the final release of 0.10.0. If you were not on the beta, please read these Release Notes carefully, as there are many changes for this release, and many Breaking Changes.

### Supported Versions

This release requires the following minimum Software and Firmware version:

* **Home Assistant**: `2021.09.0`
* **UniFi Protect**: `1.20.0`

### Upgrade Instructions

> If you are already running V0.10.0-beta.3 or higher of this release, there should not be any breaking changes, and you should be able to do a normal upgrade from HACS.

Due to the many changes and entities that have been removed and replaced, we recommend the following process to upgrade from an earlier Beta or from an earlier release:

* Upgrade the Integration files, either through HACS (Recommended) or by copying the files manually to your `custom_components/unifiprotect` directory.
* Restart Home Assistant
* Remove the UniFi Protect Integration by going to the Integrations page, click the 3 dots in the lower right corner of the UniFi Protect Integration and select *Delete*
* While still on this page, click the `+ ADD INTEGRATION` button in the lower right corner, search for UnFi Protect, and start the installation, supplying your credentials.

### Changes in this release

* `CHANGE`: **BREAKING CHANGE** The support for *Anonymous Snapshots* has been removed as of this release. This has always been a workaround in a time where this did not work as well as it does now. If you have this flag set, you don't have to do anything, as snapshots are automatically moved to the supported method.

* `NEW`: **BREAKING CHANGE** Also as part of Home Assistant 2021.11 a new [Entity Category](https://www.home-assistant.io/blog/2021/11/03/release-202111/#entity-categorization) is introduced. This makes it possible to classify an entity as either `config` or `diagnostic`. A `config` entity is used for entities that can change the configuration of a device and a `diagnostic` entity is used for devices that report status, but does not allow changes. These two entity categories have been applied to selected entities in this Integration. If you are not on HA 2021.11+ then this will not have any effect on your installation.

* `CHANGE`: **BREAKING CHANGE** There has been a substansial rewite of the underlying IO API Module (`pyunifiprotect`) over the last few month. The structure is now much better and makes it easier to maintain going forward. It will take too long to list all the changes, but one important change is that we have removed the support for Non UnifiOS devices. These are CloudKey+ devices with a FW lower than 2.0.24. I want to give a big thank you to @AngellusMortis and @bdraco for making this happen.

* `CHANGE`: **BREAKING CHANGE** As this release has removed the support for Non UnifiOS devices, we could also remove the Polling function for Events as this is served through Websockets. This also means that the Scan Interval is no longer present in the Configuration.

* `CHANGE`: **BREAKING CHANGE** To future proof the Select entities, we had to change the the way the Unique ID is populated. The entity names are not changing, but the Unique ID's are If you have installed a previous beta of V0.10.0 you will get a duplicate of all Select entities, and the ones that were there before, will be marked as unavailable. You can either remove them manually from the Integration page, or even easier, just delete the UniFi Protect integration, and add it again. (The later is the recommended method)

* `CHANGE`: **BREAKING CHANGE** All switches called `switch.ir_active_CAMERANAME` have been removed from the system. They are being migrated to a `Select Entity` which you can read more about below. If you have automations that turns these switches on and off, you will have to replace this with the `select.select_option` service, using the valid options described below for the `option` data.

* `CHANGE`: **BREAKING CHANGE** The Service `unifiprotect.set_ir_mode` now supports the following values for ir_mode: `"auto, autoFilterOnly, on, off"`. This is a change from the previous valid options and if you have automations that uses this service you will need to make sure that you only use these supported modes.

* `CHANGE`: **BREAKING CHANGE** The Service `unifiprotect.save_thumbnail_image` has been removed from the Integration. This service proved to be unreliable as the Thumbnail image very often was not available, when this service was called. Please use the service `camera.snapshot` instead.

* `CHANGE`: **BREAKING CHANGE** All switches called `switch.record_smart_CAMERANAME` and `switch.record_motion_CAMERANAME` have been removed from the system. They are being migrated to a `Select Entity` which you can read more about below. If you have automations that turns these switches on and off, you will have to replace this with the `select.select_option` service, using the valid options described below for the `option` data.

* `CHANGE`: **BREAKING CHANGE** All switches for the *Floodlight devices* have been removed from the system. They are being migrated to a `Select Entity` which you can read more about below. If you have automations that turns these switches on and off, you will have to replace this with the `select.select_option` service, using the valid options described below for the `option` data.

* `CHANGE`: **BREAKING CHANGE** The Service `unifiprotect.set_recording_mode` now only supports the following values for recording_mode: `"never, detections, always"`. If you have automations that uses the recording_mode `smart` or `motion` you will have to change this to `detections`.

* `CHANGE`: Config Flow has been slimmed down so it will only ask for the minimum values we need during installation. If you would like to change this after that, you can use the Configure button on the Integration page.

* `CHANGE`: It is now possible to change the UFP Device username and password without removing and reinstalling the Integration. On the Home Assistant Integration page, select CONFIGURE in the lower left corner of the UniFi Protect integration, and you will have the option to enter a new username and/or password.

* `CHANGE`: We will now use RTSPS for displaying video. This is to further enhance security, and to ensure that the system will continue running if Ubiquiti decides to remove RTSP completely. This does not require any changes from your side.

* `NEW`: For each Camera there will be a binary sensor called `binary_sensor.is_dark_CAMERANAME`. This sensor will be on if the camera is perceiving it is as so dark that the Infrared lights will turn on (If enabled).

* `CHANGE`: A significant number of 'under the hood' changes have been made by @bdraco, to bring the Integration up to Home Assistant standards and to prepare for the integration in to HA Core. Thank you to @bdraco for all his advise, coding and review.

* `CHANGE`: `pyunifiprotect` is V1.0.4 and has been completely rewritten by @AngellusMortis, with the support of @bdraco and is now a much more structured and easier to maintain module. There has also been a few interesting additions to the module, which you will see the fruit of in a coming release. This version is not utilizing the new module yet, but stay tuned for the 0.11.0 release, which most likely also will be the last release before we try the move to HA Core.

* `NEW`: Device Configuration URL's are introduced in Home Assistant 2021.11. In this release we add URL Link to allow the user to visit the device for configuration or diagnostics from the *Devices* page. If you are not on HA 2021.11+ then this will not have any effect on your installation.

* `NEW`: A switch is being created to turn on and off the Privacy Mode for each Camera. This makes it possible to set the Privacy mode for a Camera directly from the UI. This is a supplement to the already existing service `unifiprotect.set_privacy_mode`

* `NEW`: Restarted the work on implementing the UFP Sense device. We don't have physical access to this device, but @Madbeefer is kindly enough to do all the testing.
  * The following new sensors will be created for each UFP Sense device: `Battery %`, `Ambient Light`, `Humidity`, `Temperature` and `BLE Signal Strength`.
  * The following binary sensors will be created for each UFP Sense device: `Motion`, `Open/Close` and `Battery Low`. **Note** as of this release, these sensors are not working correctly, this is still work in progress.

* `NEW`: For each Camera there will now be a `Select Entity` from where you can select the Infrared mode for each Camera. Valid options are `Auto, Always Enable, Auto (Filter Only, no LED's), Always Disable`. These are the same options you can use if you set this through the UniFi Protect App.

* `NEW`: Added a new `Number` entity called `number.wide_dynamic_range_CAMERANAME`. You can now set the Wide Dynamic Range for a camera directly from the UI. This is a supplement to the already existing service `unifiprotect.set_wdr_value`.

* `NEW`: Added `select.doorbell_text_DOORBELL_NAME` to be able to change the LCD Text on the Doorbell from the UI. In the configuration menu of the Integration there is now a field where you can type a list of Custom Texts that can be displayed on the Doorbell and then these options plus the two standard texts built-in to the Doorbell can now all be selected. The format of the custom text list has to ba a comma separated list, f.ex.: RING THE BELL, WE ARE SLEEPING, GO AWAY... etc.

* `NEW`: Added a new `Number` entity called `number.microphone_level_CAMERANAME`. From here you can set the Microphone Sensitivity Level for a camera directly from the UI. This is a supplement to the already existing service `unifiprotect.set_mic_volume`.

* `NEW`: Added a new `Number` entity called `number.zoom_position_CAMERANAME`. From here you can set the optical Zoom Position for a camera directly from the UI. This entity will only be added for Cameras that support optical zoom. This is a supplement to the already existing service `unifiprotect.set_zoom_position`.

* `NEW`: For each Camera there will now be a `Select Entity` from where you can select the recording mode for each Camera. Valid options are `Always, Never, Detections`. Detections is what you use to enable motion detection. Whether they do People and Vehicle detection, depends on the Camera Type and the settings in the UniFi Protect App. We might later on implement a new Select Entity from where you can set the the Smart Detection options. Until then, this needs to be done from the UniFi Protect App. (as is the case today)

* `NEW`: For each Floodlight there will now be a `Select Entity` from where you can select when the Light Turns on. This replaces the two switches that were in the earlier releases. Valid options are `On Motion, When Dark, Manual`.

* `NEW`: Added a new event `unifiprotect_motion` that triggers on motion. You can use this instead of the Binary Sensor to watch for a motion event on any motion enabled device. The output from the event will look similar tom the below

  ```json
  {
    "event_type": "unifiprotect_motion",
    "data": {
        "entity_id": "camera.outdoor",
        "smart_detect": [
            "person"
        ],
        "motion_on": true
    },
    "origin": "LOCAL",
    "time_fired": "2021-10-18T10:55:36.134535+00:00",
    "context": {
        "id": "b3723102b4fb71a758a423d0f3a04ba6",
        "parent_id": null,
        "user_id": null
    }
  }
  ```


## 0.10.0 Beta 5 Hotfix 1

Released: November 13th, 2021

### Supported Versions

This release requires the following minimum Software and Firmware version:

* **Home Assistant**: `2021.09.0`
* **UniFi Protect**: `1.20.0-beta.7`

### Upgrade Instructions

Due to the many changes and entities that have been removed and replaced, we recommend the following process to upgrade from an earlier Beta or from an earlier release:

* Upgrade the Integration files, either through HACS (Recommended) or by copying the files manually to your `custom_components/unifiprotect` directory.
* Restart Home Assistant
* Remove the UniFi Protect Integration by going to the Integrations page, click the 3 dots in the lower right corner of the UniFi Protect Integration and select *Delete*
* While still on this page, click the `+ ADD INTEGRATION` button in the lower right corner, search for UnFi Protect, and start the installation, supplying your credentials.

### Changes in this release

* `CHANGE`: Updated `pyunifiprotect` to 1.0.2. Fixing errors that can occur when using Python 3.9 - Home Assistant uses that.

## 0.10.0 Beta 5

Released: November 13th, 2021

### Supported Versions

This release requires the following minimum Software and Firmware version:

* **Home Assistant**: `2021.09.0`
* **UniFi Protect**: `1.20.0-beta.7`

### Upgrade Instructions

Due to the many changes and entities that have been removed and replaced, we recommend the following process to upgrade from an earlier Beta or from an earlier release:

* Upgrade the Integration files, either through HACS (Recommended) or by copying the files manually to your `custom_components/unifiprotect` directory.
* Restart Home Assistant
* Remove the UniFi Protect Integration by going to the Integrations page, click the 3 dots in the lower right corner of the UniFi Protect Integration and select *Delete*
* While still on this page, click the `+ ADD INTEGRATION` button in the lower right corner, search for UnFi Protect, and start the installation, supplying your credentials.

### Changes in this release

As there were still some changes we wanted to do before releasing this, we decided to do one more Beta, before freezing.

* `CHANGE`: The support for *Anonymous Snapshots* has been removed as of this release. This had always been a workaround in a time where this did not work as well as it does now. If you have this flag set, you don't have to do anything, as snapshots are automatically moved to the supported method.
* `CHANGE`: Config Flow has been slimmed down so it will only ask for the minimum values we need during installation. If you would like to change this after that, you can use the Configure button on the Integration page.
* `CHANGE`: It is now possible to change the UFP Device username and password without removing and reinstalling the Integration. On the Home Assistant Integration page, select CONFIGURE in the lower left corner of the UniFi Protect integration, and you will have the option to enter a new username and/or password.
* `NEW`: For each Camera there will be a binary sensor called `binary_sensor.is_dark_CAMERANAME`. This sensor will be on if the camera is perceiving it is as so dark that the Infrared lights will turn on (If enabled).
* `CHANGE`: A significant number of 'under the hood' changes have been made, to bring the Integration up to Home Assistant standards and to prepare for the integration in to HA Core. Thank you to @bdraco for all his advise, coding and review.
* `CHANGE`: `pyunifiprotect` has been completely rewritten by @AngellusMortis, with the support of @bdraco and is now a much more structured and easier to maintain module. There has also been a few interesting additions to the module, which you will see the fruit of in a coming release. This version is not utilizing the new module yet, but stay tuned for the 0.11.0 release, which most likely also will be the last release before we try the move to HA Core.

## 0.10.0 Beta 4

Released: November 4th, 2021

**REMINDER** This version is only valid for **V1.20.0-beta.2** or higher of UniFi Protect. If you are not on that version, stick with V0.9.1.

### Upgrade Instructions

Due to the many changes and entities that have been removed and replaced, we recommend the following process to upgrade from an earlier Beta or from an earlier release:

* Upgrade the Integration files, either through HACS (Recommended) or by copying the files manually to your `custom_components/unifiprotect` directory.
* Restart Home Assistant
* Remove the UniFi Protect Integration by going to the Integrations page, click the 3 dots in the lower right corner of the UniFi Protect Integration and select *Delete*
* While still on this page, click the `+ ADD INTEGRATION` button in the lower right corner, search for UnFi Protect, and start the installation, supplying your credentials.

### Changes in this release

This will be the last beta with functional changes, so after this release it will only be bug fixes. The final release will come out when 1.20 of UniFi Protect is officially launched. Everything from Beta 1, 2 and 3 is included here, plus the following:

* `NEW`: Device Configuration URL's are introduced in Home Assistant 2021.11. In this release we add URL Link to allow the user to visit the device for configuration or diagnostics from the *Devices* page. If you are not on HA 2021.11+ then this will not have any effect on your installation.
* `NEW`: **BREAKING CHANGE** Also as part of Home Assistant 2021.11 a new [Entity Category](https://www.home-assistant.io/blog/2021/11/03/release-202111/#entity-categorization) is introduced. This makes it possible to classify an entity as either `config` or `diagnostic`. A `config` entity is used for entities that can change the configuration of a device and a `diagnostic` entity is used for devices that report status, but does not allow changes. These two entity categories have been applied to selected entities in this Integration. If you are not on HA 2021.11+ then this will not have any effect on your installation.<br>
We would like to have feedback from people on this choice. Have we categorized too many entities, should we not use this at all. Please come with the feedback.<br>
Entities which have the entity_category set:
  * Are not included in a service call targetting a whole device or area.
  * Are, by default, not exposed to Google Assistant or Alexa. If entities are already exposed, there will be no change.
  * Are shown on a separate card on the device configuration page.
  * Do not show up on the automatically generated Lovelace Dashboards.
* `NEW`: A switch is being created to turn on and off the Privacy Mode for each Camera. This makes it possible to set the Privacy mode for a Camera directly from the UI. This is a supplement to the already existing service `unifiprotect.set_privacy_mode`
* `NEW`: Restarted the work on implementing the UFP Sense device. We don't have physical access to this device, but @Madbeefer is kindly enough to do all the testing.
  * The following new sensors will be created for each UFP Sense device: `Battery %`, `Ambient Light`, `Humidity`, `Temperature` and `BLE Signal Strength`.
  * The following binary sensors will be created for each UFP Sense device: `Motion`, `Open/Close` and `Battery Low`. **Note** as of this beta, these sensors are not working correctly, this is still work in progress.


## 0.10.0 Beta 3

Released: October 27th, 2021

**REMINDER** This version is only valid for **V1.20.0-beta.2** or higher of UniFi Protect. If you are not on that version, stick with V0.9.1.

### Upgrade Instructions

Due to the many changes and entities that have been removed and replaced, we recommend the following process to upgrade from an earlier Beta or from an earlier release:

* Upgrade the Integration files, either through HACS (Recommended) or by copying the files manually to your `custom_components/unifiprotect` directory.
* Restart Home Assistant
* Remove the UniFi Protect Integration by going to the Integrations page, click the 3 dots in the lower right corner of the UniFi Protect Integration and select *Delete*
* While still on this page, click the `+ ADD INTEGRATION` button in the lower right corner, search for UnFi Protect, and start the installation, supplying your credentials.

### Changes in this release

Everything from Beta 1 and 2 is included here, plus the following:

* `CHANGE`: **BREAKING CHANGE** There has been a substansial rewite of the underlying IO API Module (`pyunifiprotect`) over the last few month. The structure is now much better and makes it easier to maintain going forward. It will take too long to list all the changes, but one important change is that we have removed the support for Non UnifiOS devices. These are CloudKey+ devices with a FW lower than 2.0.24. I want to give a big thank you to @AngellusMortis and @bdraco for making this happen.
* `CHANGE`: **BREAKING CHANGE** As this release has removed the support for Non UnifiOS devices, we could also remove the Polling function for Events as this is served through Websockets. This also means that the Scan Interval is no longer present in the Configuration.
* `CHANGE`: **BREAKING CHANGE** To future proof the Select entities, we had to change the the way the Unique ID is populated. The entity names are not changing, but the Unique ID's are If you have installed a previous beta of V0.10.0 you will get a duplicate of all Select entities, and the ones that were there before, will be marked as unavailable. You can either remove them manually from the Integration page, or even easier, just delete the UniFi Protect integration, and add it again. (The later is the recommended method)
* `CHANGE`: **BREAKING CHANGE** All switches called `switch.ir_active_CAMERANAME` have been removed from the system. They are being migrated to a `Select Entity` which you can read more about below. If you have automations that turns these switches on and off, you will have to replace this with the `select.select_option` service, using the valid options described below for the `option` data.
* `CHANGE`: **BREAKING CHANGE** The Service `unifiprotect.set_ir_mode` now supports the following values for ir_mode: `"auto, autoFilterOnly, on, off"`. This is a change from the previous valid options and if you have automations that uses this service you will need to make sure that you only use these supported modes.
* `CHANGE`: **BREAKING CHANGE** The Service `unifiprotect.save_thumbnail_image` has been removed from the Integration. This service proved to be unreliable as the Thumbnail image very often was not available, when this service was called. Please use the service `camera.snapshot` instead.
* `NEW`: For each Camera there will now be a `Select Entity` from where you can select the Infrared mode for each Camera. Valid options are `Auto, Always Enable, Auto (Filter Only, no LED's), Always Disable`. These are the same options you can use if you set this through the UniFi Protect App.
* `NEW`: Added a new `Number` entity called `number.wide_dynamic_range_CAMERANAME`. You can now set the Wide Dynamic Range for a camera directly from the UI. This is a supplement to the already existing service `unifiprotect.set_wdr_value`.
* `NEW`: Added `select.doorbell_text_DOORBELL_NAME` to be able to change the LCD Text on the Doorbell from the UI. In the configuration menu of the Integration there is now a field where you can type a list of Custom Texts that can be displayed on the Doorbell and then these options plus the two standard texts built-in to the Doorbell can now all be selected. The format of the custom text list has to ba a comma separated list, f.ex.: RING THE BELL, WE ARE SLEEPING, GO AWAY... etc.
* `NEW`: Added a new `Number` entity called `number.microphone_level_CAMERANAME`. From here you can set the Microphone Sensitivity Level for a camera directly from the UI. This is a supplement to the already existing service `unifiprotect.set_mic_volume`.
* `NEW`: Added a new `Number` entity called `number.zoom_position_CAMERANAME`. From here you can set the optical Zoom Position for a camera directly from the UI. This entity will only be added for Cameras that support optical zoom. This is a supplement to the already existing service `unifiprotect.set_zoom_position`.

## 0.10.0 Beta 2

Released: October 24th, 2021

Everything from Beta 1 is included here, plus the following:

`CHANGE`: Changes to the underlying `pyunifiprotect` module done by @AngellusMortis to ensure all tests are passing and adding new functionality to be used in a later release.
`NEW`: Added a new event `unifiprotect_motion` that triggers on motion. You can use this instead of the Binary Sensor to watch for a motion event on any motion enabled device. The output from the event will look similar tom the below

  ```json
  {
    "event_type": "unifiprotect_motion",
    "data": {
        "entity_id": "camera.outdoor",
        "smart_detect": [
            "person"
        ],
        "motion_on": true
    },
    "origin": "LOCAL",
    "time_fired": "2021-10-18T10:55:36.134535+00:00",
    "context": {
        "id": "b3723102b4fb71a758a423d0f3a04ba6",
        "parent_id": null,
        "user_id": null
    }
  }
  ```

## 0.10.0 Beta 1

Released: October 17th, 2021

This is the first Beta release that will support **UniFi Protect 1.20.0**. There have been a few changes to the Protect API, that requires us to change this Integration. Unfortunately it cannot be avoided that these are Breaking Changes, so please read carefully below before you do the upgrade.

When reading the Release Notes for UniFi Protect 1.20.0-beta.2 the following changes are directly affecting this Integration:

* Integrate “Smart detections” and “Motion Detections” into “Detections”.
* Generate only RTSPS links for better security. (RTSP streams are still available by removing S from RTSPS and by changing port 7441 to 7447.

#### Changes implemented in this version:
* `CHANGE`: **IMPORTANT** You MUST have at least UniFi Protect **V1.20.0-beta.1** installed for this Integration to work. There are checks on both new installations and upgraded installations to see if your UniFi Protect App is at the right version number. Please consult the HA Logfile for more information if something does not work.
If you are not running the 1.20.0 beta, DO NOT UPGRADE. If you did anyway, you can just uninstall and select the 0.9.1 release from HACS and all should be running again.
* `CHANGE`: **BREAKING CHANGE** All switches called `switch.record_smart_CAMERANAME` and `switch.record_motion_CAMERANAME` have been removed from the system. They are being migrated to a `Select Entity` which you can read more about below. If you have automations that turns these switches on and off, you will have to replace this with the `select.select_option` service, using the valid options described below for the `option` data.
* `CHANGE`: **BREAKING CHANGE** All switches for the *Floodlight devices* have been removed from the system. They are being migrated to a `Select Entity` which you can read more about below. If you have automations that turns these switches on and off, you will have to replace this with the `select.select_option` service, using the valid options described below for the `option` data.
* `CHANGE`: **BREAKING CHANGE** The Service `unifiprotect.set_recording_mode` now only supports the following values for recording_mode: `"never, detections, always"`. If you have automations that uses the recording_mode `smart` or `motion` you will have to change this to `detections`.
* `NEW`: For each Camera there will now be a `Select Entity` from where you can select the recording mode for each Camera. Valid options are `Always, Never, Detections`. Detections is what you use to enable motion detection. Whether they do People and Vehicle detection, depends on the Camera Type and the settings in the UniFi Protect App. We might later on implement a new Select Entity from where you can set the the Smart Detection options. Until then, this needs to be done from the UniFi Protect App. (as is the case today)
* `NEW`: For each Floodlight there will now be a `Select Entity` from where you can select when the Light Turns on. This replaces the two switches that were in the earlier releases. Valid options are `On Motion, When Dark, Manual`.
* `CHANGE`: We will now use RTSPS for displaying video. This is to further enhance security, and to ensure that the system will continue running if Ubiquiti decides to remove RTSP completely. This does not require any changes from your side.

## 0.9.1

Released: October 17th, 2021

This will be the final release for devices not running the UnifiOS. With the next official release, there will no longer be support for the CloudKey+ running a firmware lover than 2.0.
**NOTE** This release does not support UniFi Protect 1.20.0+. This will be supported in the next Beta release.

* `FIX`: Issue #297. Improves determining reason for bad responses.

## 0.9.0

Released: August 29th, 2021

* `NEW`: This release adds support for the UFP Viewport device. This is done by adding the `select` platform, from where the views defined in Unifi Protect can be selected. When changing the selection, the Viewport will change it's current view to the selected item. The `select` platform will only be setup if UFP Viewports are found in Unfi Protect. When you create a view in Unifi Protect, you must check the box *Shared with Others* in order to use the view in this integration.<br>
**NOTE**: This new entity requires a minimum of Home Assistant 2021.7. If you are on an older version, the Integration will still work, but you will get an error during startup.
* `NEW`: As part of the support for the UFP Viewport, there also a new service being created, called `unifiprotect.set_viewport_view`. This service requires two parameters: The `entity_id` of the Viewport and the `view_id` of the View you want to set. `view_id` is a long string, but you can find the id number when looking at the Attributes for the `select` entity.
* `FIX`: Issue #264, missing image_width variable is fixed in this release.
* `CHANGE`: PR #276, Ensure setup is retried later when device is rebooting. Thanks to @bdraco
* `CHANGE`: PR #271. Updated README, to ensure proper capitalization. Thanks to @jonbloom
* `CHANGE`: PR #278. Allow requesting a custom snapshot width and height, to support 2021.9 release. Thank to @bdraco. Fixing Issue #282

## 0.9.0 Beta 2

Released: July 17th, 2021

* `BREAKING`: If you installed Beta 1, then you will have a media_player entity that is no longer used. You can disable it, or reinstall the Integration to get completely rid of it.
* `NEW`: This release adds support for the UFP Viewport device. This is done by adding the `select` platform, from where the views defined in Unifi Protect can be selected. When changing the selection, the Viewport will change it's current view to the selected item. The `select` platform will only be setup if UFP Viewports are found in Unfi Protect. When you create a view in Unifi Protect, you must check the box *Shared with Others* in order to use the view in this integration.<br>
**NOTE**: This new entity requires a minimum of Home Assistant 2021.7

* `NEW`: As part of the support for the UFP Viewport, there also a new service being created, called `unifiprotect.set_viewport_view`. This service requires two parameters: The `entity_id` of the Viewport and the `view_id` of the View you want to set. `view_id` is a long string, but you can find the id number when looking at the Attributes for the `select` entity.
* `FIX`: Issue #264, missing image_width variable is fixed in this release.

## 0.9.0 Beta 1

Released: July 6th, 2021

* `NEW`: This release adds support for the UFP Viewport device. This is done by adding the `media_player` platform, from where the views defined in Unifi Protect can be selected as source. When selecting the source, the Viewport will change it's current view to the selected source. The `media_player` platform will only be setup if UFP Viewports are found in Unfi Protect.
* `NEW`: As part of the support for the UFP Viewport, there also a new service being created, called `unifiprotect.set_viewport_view`. This service requires two parameters: The `entity_id` of the Viewport and the `view_id` of the View you want to set. `view_id` is a long string, but you can find the id number when looking at the Attributes for the media_player.

## 0.8.9

Released: June 29th, 2021

* `FIXED`: During startup of the Integration, it would sometimes log `Error Code: 500 - Error Status: Internal Server Error`. (Issue #249) This was caused by some values not being available at startup.
* `CHANGE`: The service `unifiprotect.save_thumbnail_image` now creates the directories in the filename if they do not exist. Issue #250.
* `FIX`: We have started the integration of the new UFP-Sense devices, but these are not available in Europe yet, so the integration is not completed, and will not be, before I can get my hands on one of these devices. Some users with the devices, got a crash when running the latest version, which is now fixed. The integration is not completed, this fix, just removes the errors that were logged. Thanks to @michaeladam for finding this.
* `NEW`: When the doorbell is pressed, the integration now fires an event with the type `unifiprotect_doorbell`. You can use this in automations instead of monitoring the binary sensor. The event will look like below and only fire when the doorbell is pressed, so there will be no `false`event. If you have multiple doorbells you use the `entity_id` value in the `data` section to check which doorbell was pressed.

  ```json
  {
      "event_type": "unifiprotect_doorbell",
      "data": {
          "ring": true,
          "entity_id": "binary_sensor.doorbell_kamera_doerklokke"
      },
      "origin": "LOCAL",
      "time_fired": "2021-06-26T08:16:58.882088+00:00",
      "context": {
          "id": "6b8cbcecb61d75cbaa5035e2624a3051",
          "parent_id": null,
          "user_id": null
      }
  }
  ```

## 0.8.8

Released: May 22nd, 2021

* `NEW`: As stated a few times, there is a delay of 10-20 seconds in the Live Stream from UniFi Protect. There is not much this integration can do about it, but what we can do is, to disable the RTSP Stream, so that JPEG push is used instead. This gives an almost realtime experience, with the cost of NO AUDIO. As of this version you can disable the RTSP Stream from the Config menu.
* `FIXED`: Issue #235, where the aspect ratio of the Doorbell image was wrong when displayed in Lovelace or in Notifications. Now the aspect ratio is read from the camera, so all cameras should have a correct ratio.


## 0.8.7

Released: May 4th, 2021

* `CHANGED`: Added **iot_class** to `manifest.json` as per HA requirements
* `FIXED`: Ensure the event_object is not cleared too soon, when a smart detect event occurs. Issue #225. Thanks to @bdraco for the fix.
* `CHANGED`: Updated README.md with information on how to turn on Debug logger. Thank you @blaines


## 0.8.6

Released: April 25th, 2021

* `FIXED`: If authentication failed during setup or startup of the Integration it did not return the proper boolean, and did not close the session properly.
* `CHANGED`: Stop updates on stop event to prevent shutdown delay.
* `CHANGED`: Updated several files to ensure compatability with 2021.5+ of Home Assistant. Thanks to @bdraco for the fix.

## 0.8.5

Released: March 30th, 2021

* `ADDED`: Have you ever wanted to silence your doorbell chime when you go to bed, or you put your child to sleep? - Now this is possible. A new service to enable/disable the attached Doorbel Chime is delivered with this release. The service is called `unifiprotect.set_doorbell_chime_duration` and takes two parameters: Entity ID of the Doorbell, Duration in milliseconds which is a number between 0 and 10000. 0 equals no chime. 300 is the standard for mechanical chimes and 10000 is only used in combination with a digital chime. The function does not really exist in the API, so this is a workaround. Let me know what values are best for on with the different chimes. You might still hear a micro second of a ding, but nothing that should wake anyone up. Fixing issue #211

## 0.8.4

Released: March 18th, 2021

* `FIXED`: Issues when activating Services that required an Integer as value, and using a Template to supply that value. Services Schemas have now been converted to use `vol.Coerce(int)` instead of just `int`.
* `CHANGED`: All Services definitions have now been rewritten to use the new format introduced with the March 2021 Home Assistant release. **NOTE**: You might need to do a Hard Refresh of your browser to see the new Services UI.
* `FIXED`: When using the switches or service to change recording mode for a camera, the recording settings where reset to default values. This is now fixed, so the settings you do in the App are not modfied by activating the Service or Recording mode switches.

## 0.8.3

Released: March 3rd, 2021

* `ADDED`: New service `unifiprotect.set_wdr_value` which can set the Wide Dynamic Range of a camera to an integer between 0 and 4. Where 0 is disabled and 4 is full.
## 0.8.2

Released: February 4th, 2021

* `FIXED`: Use the UniFi Servers MAc address as unique ID to ensure that it never changes. Previously we used the name, and that can be changed by the user. This will help with stability and prevent integrations from suddenly stop working if the name of the UDMP, UNVR4 or CKP was changed.
* `FIXED`: Further enhance the fix applied in 0.8.1 to ensure the Integration loads even if the first update fails. Thanks to @bdraco for implementing this.
* `FIXED`: Sometimes we would be missing event_on or event_ring_on if the websocket connected before the integration setup the binary sensor. We now always return the full processed data, eliminating this error. Another fix by @bdraco

## 0.8.1

Released: January 28th, 2021

* `FIXED`: The service `unifiprotect.set_status_light` did not function, as it was renamed in the IO module. This has now been fixed so that both the service and the Switch work again.
* `FIXED`: Issue #181, Add a retry if the first update request fails on load of the Integration.

## 0.8.0

Released: January 8th, 2021

This release adds support for the new Ubiquiti Floodlight device. If found on your Protect Server, it will add a new entity type `light`, that will expose the Floodlight as a light entity and add support for turning on and off, plus adjustment of brightness.

There will also be support for the PIR motion sensor built-in to the Floodlight, and you will be able to adjust PIR settings and when to detect motion.

You must have UniFi Protect V1.17.0-beta.10+ installed for Floodlight Support. Below that version, you cannot add the Floodlight as a device to UniFi Protect.

THANK YOU again to @bdraco for helping with some of the code and for extensive code review. Without you, a lot of this would not have been possible.


* `ADDED`: New `light` entity for each Floodlight found. You can use the normal *light* services to turn on and off. Be aware that *brightness* in the Protect App only accepts a number from 1-6, so when you adjust brightness from Lovelace or the Service, the number here will be converted to a number between 1 and 6.
* `ADDED`: A Motion Sensor is created for each Floodlight attached. It will trigger motion despite the state of the Light. It will however not re-trigger until the time set in the *Auto Shutoff Timer* has passed.
* `ADDED`: New service `unifiprotect.light_settings`. Please see the README file for details on this Service.
* `FIXED`: Missing " in the Services description, prevented message to be displayed to the user. Thank you to @MarcJenningsUK for spotting and fixing this.
* `CHANGED`: Bumped `pyunifiprotect` to 0.28.8

**IMPORTANT**: With the official FW 2.0.24 for the CloudKey+ all UniFi Protect Servers are now migrated to UniFiOS. So as of this release, there will be no more development on the Non UniFiOS features. What is there will still be working, but new features will only be tested on UniFiOS. We only have access to very limited HW to test on, so it is not possible to maintain HW for backwards compatability testing.

#### This release is tested on:

*Tested* means that either new features work on the below versions or they don't introduce breaking changes.

* CloudKey+ G2: FW Version 2.0.24 with Unifi Protect V1.17.0-beta.13
* UDMP: FW Version 1.18.5 with Unifi Protect V1.17.0-beta.13

## Release 0.7.1

Released: January 3rd, 2021

* `ADDED`: New service `unifiprotect.set_zoom_position` to set the optical zoom level of a Camera. This only works on Cameras that support optical zoom.

  The services takes two parameters: **entity_id** of the camera, **position** which can be between 0 and 100 where 0 is no zoom and 100 is maximum zoom.

  A new attribue called `zoom_position` is added to each camera, showing the current zoom position. For cameras that does not support setting optical zoom, this will always be 0.

#### This release is tested on:

*Tested* means that either new features work on the below versions or they don't introduce breaking changes.

* CloudKey+ G2: FW Version 2.0.24 with Unifi Protect V1.16.9
* UDMP: FW Version 1.18.5 with Unifi Protect V1.17.0-beta.10
## Release 0.7.0

Released: December 20th, 2020

* `ADDED`: New service `unifiprotect.set_privacy_mode` to enable or disable a Privacy Zone, that blacks-out the camera. The effect is that you cannot view anything on screen. If recording is enabled, the camera will still record, but the only thing you will get is a black screen. You can enable/disable the microphone and set recording mode from this service, by specifying the values you see below.
If the camera already has one or more Privacy Zones set up, they will not be overwritten, and will still be there when you turn of this.
Use this instead of physically turning the camera off or on.

  The services takes four parameters: **entity_id** of the camera, **privacy_mode** which can be true or false, **mic_level** which can be between 0 and 100 and **recording_mode** which can be never, motion, always or smart.

  Also a new attribute called `privacy_mode` is added to each camera, that shows if this mode is enabled or not. (Issue #159)

* `CHANGED`: Some users are getting a warning that *verify_sll* is deprecated and should be replaced with *ssl*. We changed the pyunifiportect module to use `ssl` instead of `verify_sll` (Issue #160)

* `ADDED`: Dutch translation to Config Flow is now added. Thank you to @copperek for doing it.

* `FIXED`: KeyError: 'server_id' during startup of Unifi Protect. This error poped up occasionally during startup of Home Assistant. Thank you to @bdraco for fixing this. (Issue #147)

* `FIXED`: From V1.17.x of UniFi Protect, Non Adopted Cameras would be created as camera.none and creating all kinds of errors. Now these cameras will be ignored, until they are properly adopted by the NVR. Thank you to @bdraco for helping fixing this.

#### This release is tested on:

*Tested* means that either new features work on the below versions or they don't introduce breaking changes.

* CloudKey+ G2: FW Version 1.1.13 with Unifi Protect V1.13.37
* UDMP: FW Version 1.18.4-3 with Unifi Protect V1.17.0-beta.6

## Release 0.6.7

Released: December 15th, 2020

`ADDED`: New attribute on each camera called `is_dark`. This attribute is true if the camera sees the surroundings as dark. If infrared mode is set to *auto*, then infrared mode would be turned on when this changes to true.

`ADDED`: New Service `unifiprotect.set_mic_volume` to set the Sensitivity of the built-in Microphone on each Camera. Requires two parameters: *Camera Entity* and *level*, where level is a number between 0 and 100. If level is set to 0, the Camera will not react on Audio Events.
On each camera there is also now a new attribute called `mic_sensitivity` which displayes the current value.

See [README.md](https://github.com/briis/unifiprotect#create-input-slider-for-microphone-sensitivity) for instructions on how to setup an Input Slider in Lovelace to adjust the value.

`CHANGED`: Updated the README.md documentation and added more information and a TOC.

#### This release is tested on:

*Tested* means that either new features work on the below versions or they don't introduce breaking changes.

* CloudKey+ G2: FW Version 1.1.13 with Unifi Protect V1.13.37
* UDMP: FW Version 1.18.3 with Unifi Protect V1.17.0-beta.6
## Release 0.6.6

With the release of Unifi Protect V1.7.0-Beta 1, there is now the option of detecting Vehicles on top of the Person detection that is allready there. This is what Ubiquiti calls *Smart Detection*. Also you can now set recording mode to only look for Smart Detection events, meaning that motion is only activated if a person or a vehicle is detected on the cameras. Smart Detection requires a G4-Series camera and a UnifiOS device.

**NOTE**: If you are not running Unifi Protect V1.17.x then the new features introduced here will not apply to your system. It has been tested on older versions of Unifi Protect, and should not break any existing installations.

* **New** For all G4 Cameras, a new Switch will be created called *Record Smart*, where you can activate or de-active Smart Recording on the camera
* **New** The service `unifiprotect.set_recording_mode` now has a new option for `recording_mode` called *smart*. This will turn on Smart Recording for the selected Camera. Please note this will only work on G4-Series cameras.
* **Fix** When the G4 Doorbell disconnected or restarted, the Ring Sensor was triggered. This fix now ensures that this does not happen.

### This release is tested on:

*Tested* means that either new features work on the below versions or they don't introduce breaking changes.

* CloudKey+ G2: FW Version 1.1.13 with Unifi Protect V1.13.37
* UDMP: FW Version 1.18.3-5 with Unifi Protect V1.17.0-beta.1
* UNVR: FW Version 1.3.15 with Unifi Protect V1.15.0

## Release 0.6.5

* **Hotfix** The recording of motion score and motion length got out of sync with the motion detections on/off state. With this fix, motion score and length are now updated together with the off state of the binary motion sensors. This was only an issue for Non UnifiOS devices (*CloudKey+ users with the latest original firmware version or below*).

*This release is tested on*:
* CloudKey+ G2: FW Version 1.1.13 with Unifi Protect V1.13.37
* UDMP: FW Version 1.18.3-5 with Unifi Protect V1.16.8

## Release 0.6.4

* **Hotfix** for those who experience that motion sensors no longer work after upgrading to 0.6.3. Users affected will be those who are running a version of Unifi Protect that does not support SmartDetection.

*This release is tested on*:
* CloudKey+ G2: FW Version 1.1.13 with Unifi Protect V1.13.37
* UDMP: FW Version 1.18.3-4 with Unifi Protect V1.16.7
* UDMP FW Version 1.18.0 with Unifi Protect V1.14.11

## Release 0.6.3

@bdraco made some serious changes to the underlying IO module, that gives the following new features:

* When running UnifiOS on the Ubiquiti Device, events are now fully constructed from Websockets.
* Motion Events are now triggered regardless of the Recording Mode, meaning you can use your cameras as Motion Detectors. **Object detection** still requires that the Cameras recording mode is enabled (Motion or Always) as this information is only passed back when either of these are on.

  **BREAKING** If your Automations trigger on Motion Detection from a Camera, and you assume that Recording is enabled on a camera then you now need to make a check for that in the Condition Section of your automation.
* Bumped pyunifiprotect to 0.24.3

## Release 0.6.2

* Changed text for Config Flow, to differ between UnifiOS and NON UNifiOS devices, instead of CloudKey and UDMP. This makes more sense, now that CloudKey+ also can run UnifiOS.
* Changed the default port in Config Flow, from 7443 to 443, as this will be the most used port with the update to CloudKey+
* Added a Debug option to Config Flow, so that we can capture the actual error message when trying to Authenticate.

## Release 0.6.1
@bdraco strikes again and fixed the following problems:

* If the system is loaded, we miss events because the time has already passed.
* If the doorbell is rung at the same time as motion, we don't see the ring event because the motion event obscures it.
* If the hass clock and unifi clock are out of sync, we see the wrong events. (Still recommend to ensure that unifi and hass clocks are synchronized.)
* The Doorbell is now correctly mapped as DEVICE_CLASS_OCCUPANCY.

## Release 0.6.0
The Integration has now been rewritten to use **Websockets** for updating events, giving a lot of benefits:

* Motion and doorbell updates should now happen right away
* Reduces the amount of entity updates since we now only update cameras that change when we poll instead of them all.
* Reduce the overall load on Home Assistant.

Unfortunately, Websockets are **only available for UnifiOS** powered devices (UDMP & UNVR), so this will not apply to people running on the CloudKey. Here we will still need to do polling. Hopefully Ubiquity, will soon move the CloudKey to UnifiOS or add Websockets to this device also.

All Credits for this rewrite goes to:
* @bdraco, who did the rewrite of both the IO module and the Integration
* @adrum for the initial work on the Websocket support
* @hjdhjd for reverse engineering the Websocket API and writing up the description

This could not have been done without all your work.

### Other changes

* When setting the LCD text on the Doorbell, this is now truncated to 30 Characters, as this is the maximum supported Characters. Thanks to @hjdhjd for documenting this.
* Fixed an error were sometimes the External IP of the Server was used for the Internal Stream. Thanks to @adrum for fixing this.
* Added Switch for changing HDR mode from Lovelace (Issue #128). This switch will only be created for Cameras that support HDR mode.
* Added Switch for changing High FPS mode from Lovelace (Issue #128). This switch will only be created for Cameras that support High FPS mode.
* Improved error handling.
* Added German translation for Config Flow. Thank you @SeraphimSerapis

## Release 0.5.8
Object Detection was introduced with 1.14 of Unifi Protect for the UDMP/UNVR with the G4 series of Cameras. (I am unsure about the CloudKey+, but this release should not break on the CloudKey+ even without object detection). This release now adds a new Attribute to the Binary Motion Sensors that will display the object detected. I have currently only seen `person` being detected, but I am happy to hear if anyone finds other objects. See below on how this could be used.
This release also introduces a few new Services, as per user request. Please note that HDR and High FPS Services will require a version of Unifi Protect greater than 1.13.x. You will still be able to upgrade, but the functions might not work.

* **New feature**: Turn HDR mode on or off, asked for in Issue #119. Only selected Cameras support HDR mode, but for those cameras that support it, you can now switch this on or off by calling the service: `unifiprotect.set_hdr_mode`. Please note that when you use this Service the stream will reset, so expect a drop out in the stream for a little while.
* **New feature**: Turn High FPS video mode on or off. The G4 Cameras support High FPS video mode. With this release there is now a service to turn this on or off. Call the service `unifiprotect.set_highfps_video_mode`.
* **New feature**: Set the LCD Message on the G4 Doorbell. There is now a new service called `unifiprotect.set_doorbell_lcd_message` from where you can set a Custom Text for the LCD. Closing Issue #104
* **New attribute** `event_object` that will add the object detected when Motion occurs. It will contain the string `None Identified` if no specific object is detected. If a human is detected it will return `person` in this attribute, which you can test for in an automation. (See README.md for an example)

## Release 0.5.6
New feature: Turn the Status Light on or off, asked for in Issue #102. With this release there is now the possibility to turn the Status light on each camera On or Off. This can be done in two ways:
1. Use the service `unifiprotect.set_status_light`
2. Use the new switch that will be created for each camera.

Disabled the Websocket update, that was introduced in 0.5.5, as it is currently not being used, and caused error messages when HA was closing down, due to not being stopped.


## Release 0.5.5

The latest beta of Unifi Protect includes the start of Ubiquiti's version of AI, and introduces a concept called Smart Detect, which currently can identify People on specific Camera models. When this is enabled on a Camera, the event type changes from a *motion* event to a *smartdetect* event, and as such these cameras will no longer trigger motion events.

This release is a quick fix for the people who have upgraded to the latest Unifi Protect Beta version. I will later introduce more Integration features based on these new Unifi Protect features.

## Release 0.5.4

A more permanent fix for Issue #88, where the snapshot images did not always get the current image. The API call has now been modified, so that it forces a refresh of the image when pulling it from the camera. Thank you to @rajeevan for finding the solution.
If you installed release 0.5.3 AND enabled *Anonymous Snapshots* you can now deselect that option again, and you will not have to enable the Anonymous Snapshot on each Camera.

## Release 0.5.3

Fix for Issue #88 - The function for saving a Camera Snapshot works fine for most people, but it turns out that the image it saves is only refreshed every 10-15 seconds. There might be a way to force a new image, but as the Protect API is not documented I have not found this yet. If you need the guaranteed latest image from the Camera, there is a way around it, and that is to enable Anonymous Snapshots on each Camera, as this function always gets the latest image directly from the Camera.

This version introduces a new option where you can enable or disable anonymous snapshots in the Unifi Integration. If enabled, it will use a different function than if disabled, but it will only work if you login to each of your Cameras and enable the *Anonymous Snapshot*.

To use the Anonymous Snapshot, after this update has been installed, do the following:

1. Login to each of your Cameras by going to http://CAMERA_IP. The Username is *ubnt* and the Camera Password can be found in Unifi Protect under *Settings*.
2. If you have never logged in to the Camera before, it might take you through a Setup procedure - just make sure to keep it in *Unifi Video* mode, so that it is managed by Unifi Protect.
3. Once you are logged in, you will see an option on the Front page for enabling Anonymous Snapshots. Make sure this is checked, and then press the *Save Changes* button.
4. Repeat step 3 for each of your Cameras.
5. Now go to the Integrations page in Home Assistant. Find the Unifi Protect Widget and press options.
6. Select the checkbox *Use Anonymous Snapshots* and press *Submit*

Now the Unfi Protect Integration will use the direct Snapshot from the Camera, without going through Unfi Protect first.

## Release 0.5.2

* Added exception handling when the http connection is dropped on a persistent connection. The Integration will now throw a `ConfigEntryNotReady` instead and retry.

## Release 0.5.1

Two fixes are implemented in this release:
1. Basic data for Cameras were pulled at the same interval as the Events for Motion and Doorbell. This caused an unnecessary load on the CPU. Now the base Camera data is only pulled every 60 seconds, to minimize that load.
2. A user reported that when having more than 20 Cameras attached, the Binary Sensors stayed in an unavailable state. This was caused by the fact that a poll interval of 2 seconds for the events, was not enough to go through all cameras, so the state was never reported back to Home Assistant. With this release there is now an option on the *Integration Widget* to change the Scan Interval to a value between 2 and 30 seconds. You **ONLY** have to make this adjustment if you experience that the sensors stay unavailable - so typically if you have many Cameras attached. Default is still 2 seconds.
3. The same user mentioned above, is running Unifi Protect on the new NVR4 device, and the Integration seems to work fine on this new platform. I have not heard from anyone else on this, but at least one user has success with that.
4. Bumped pyunifiprotect to v0.16 which fixes the problem mentioned in point 1 above. Thank you to @bdraco for the fix.

## Release 0.5 - Fully Integration based

The Beta release 0.4 has been out for a while now, and I belive we are at a stage where I will release it officially, and it will be called Version 0.5.

After the conversion to use all the Async Libraries, it became obvious to also move away from *Yaml Configuration*, to the fully UI based Integration. As I wrote in the Tester Notes, I know there are some people with strong feelings about this, but I made the decision to make the move, and going forward **only** to support this way of adding Unifi Protect to Home Assistant.

### ***** BREAKING CHANGES *****
Once setup, the base functionality will be the same as before, with the addition of a few minor changes. But behind the scene there are many changes in all modules, which also makes this a lot more ready for becoming an official Integration in Home Assistant Core.

I want to send a BIG THANK YOU to @bdraco who has made a lot of code review, and helped me shape this to conform to Home Assistant standards. I learned so much from your suggestions and advice, so thank you!

Here are the Breaking changes:

1. Configuration can only be done from the *Integration* menu on the *Configuration* tab. So you will have to remove all references to *unifiprotect* from your configuration files.
2. All entities will get the `unifiprotect_` prefix removed from them, so you will have to change automations and scripts where you use these entities. This is done to make sure that entities have a Unique Id and as such can be renamed from the UI as required by Home Assistant. I will give a 99% guarantee, that we do not need to change entity names again.

### Upgrading and Installing
If you have not used Unifi Protect before, go to step 4.

If you are already runing a version of *Unifi Protect* with version 0.3.x or lower:

1. Remove the previous installation
 * If you have installed through HACS, then go to HACS and remove the Custom Component
 * If you manually copied the files to your system, go to the `custom_components` directory and delete the `unifiprotect` directory.
* Edit `configuration.yaml` and remove all references to *unifiprotect*. Some have split the setup in to multiple files, so remember to remove references to unifiprotect from these files also.
* I recommend to restart Home Assistant at this point, but in theory it should not be necessary.

4. Install the new version
 * If you use HACS, go there, and add Unifi Protect V0.5 or later.
 * If you do it manually, go to [Github](https://github.com/briis/unifiprotect/tree/master/custom_components/unifiprotect) and copy the files to `custom_components/unifiprotect`. Remember to include the `translations` directory and the files in here.
* Restart Home Assistant
* Now go to the *Integration* menu on the *Configuration* tab, and search for *Unifi Protect*. If it does not show up, try and clear your browser cache, and refresh your browser.
* From there, it should be self explanatory.

I will leave Release 0.3.4 as an option in HACS, so if you want to stick with the Yaml version, feel free to do so, but please note that I will not make any changes to this version going forward.

## Version 0.3.2

**NOTE** When upgrading Home Assistant to +0.110 you will receive warnings during startup about deprecated BinaryDevice and SwitchDevice. There has been a change to SwitchEntity and BinaryEntity in HA 0.110. For now this will not be changed, as not everybody is on 0.110 and if changing it this Component will break for users not on that version as it is not backwards compatible.

With this release the following items are new or have been fixed:

* **BREAKING** Attribute `last_motion` has been replaced with `last_tripped_time` and attribute `motion_score` has been replaced with `event_score`. So if you use any of these attributes in an automation you will need to change the automation.
* **NEW** There is now support for the Unifi Doorbell. If a Doorbell is discovered there will be an extra Binary Sensor created for each Doorbell, so a Doorbell Device will have both a Motion Binary Sensor and a Ring Binary Sensor. The later, turns True if the doorbell is pressed.<br>
**BREAKING** As part of this implementation, it is no longer possible to define which binary sensors to load - all motion and doorbell *binary sensors* found are loaded. So the `monitored_condition` parameter is removed from the configuration for `binary_sensor` and needs to be removed from your `configuration.yaml` file if present.
* **FIX** The Switch Integration was missing a Unique_ID
