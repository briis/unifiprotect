# Changelog

## Version 0.4.0

**BREAKING** From this version on the only way to configure Unifi Protect is from the Integration Page in the Settings Menu. All Yaml configuration has been removed. I am aware that this is not what everybody wants, but it is the way Home Assistant is moving, and I don't want to maintain two different ways of Configuration.<br>
So before you install this version, please remove all `unifiprotect` entries from your configurations files, and restart Home Assistant. Then you can upgrade via HACS and go to the Integration Page and install Unifi Protect.


## Version 0.3.2

**NOTE** When upgrading Home Assistant to +0.110 you will receive warnings during startup about deprecated BinaryDevice and SwitchDevice. There has been a change to SwitchEntity and BinaryEntity in HA 0.110. For now this will not be changed, as not everybody is on 0.110 and if changing it this Component will break for users not on that version as it is not backwards compatible.

With this release the following items are new or have been fixed:

* **BREAKING** Attribute `last_motion` has been replaced with `last_tripped_time` and attribute `motion_score` has been replaced with `event_score`. So if you use any of these attributes in an automation you will need to change the automation.
* **NEW** There is now support for the Unifi Doorbell. If a Doorbell is discovered there will be an extra Binary Sensor created for each Doorbell, so a Doorbell Device will have both a Motion Binary Sensor and a Ring Binary Sensor. The later, turns True if the doorbell is pressed.<br>
**BREAKING** As part of this implementation, it is no longer possible to define which binary sensors to load - all motion and doorbell *binary sensors* found are loaded. So the `monitored_condition` parameter is removed from the configuration for `binary_sensor` and needs to be removed from your `configuration.yaml` file if present.
* **FIX** The Switch Integration was missing a Unique_ID
