# // Changelog

## 0.9.1 Beta 1

Released: NOT RELEASED YET

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
