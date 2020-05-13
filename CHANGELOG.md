# Changelog

## Version 0.3.2

With this release the following items are new or have been fixed:

* **NEW** There is now support for the Unifi Doorbell. If a Doorbell is discovered there will be an extra Binary Sensor created for each Doorbell, that monitors if the doorbell button is pressed. As part of this implementation, it is no longer possible to define which binary sensors to load - all motion and doorbell *binary sensors* are loaded. So the `monitored_condition` parameter is removed from the configuration.
* **FIX** The Switch Integration was missing a Unique_ID
