# // Changelog

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
