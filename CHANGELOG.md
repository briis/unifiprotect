# Changelog

## Version 0.0.6
* `binary_sensor_`:
  * Changed default SCAN_INTERVAL to 3 seconds to optimize Motion Detection
* `camera`:
  * Added new service `camera.unifiprotect_save_thumbnail`. When calling this services the Thumbnail of the last recorded motion will be saved to disk, and could then be used in an automation, to send to a phone via the `notify` platform. Requires `entity_id` and `filename` as attributes.
* `sensor`:
  * Added new attribute `camera_type` to the sensor. Showing what type of Unfi Camera is attached to this sensor
* `Core Module`
  * changed size of the thumbnail image when being created.
  * fixed error when no *Last Motion* record exist
  * cleaned up the code, removing obsolete parts.