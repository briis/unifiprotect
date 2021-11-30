# // UniFi Protect for Home Assistant

![GitHub release (latest by date including pre-releases)](https://img.shields.io/github/v/release/briis/unifiprotect?include_prereleases&style=flat-square) [![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg?style=flat-square)](https://github.com/custom-components/hacs)

> **NOTE** If you are NOT running UniFi Protect V1.20.0 or higher, you must use the **V0.9.1** of this Integration.
> Please the [CHANGELOG](https://github.com/briis/unifiprotect/blob/master/CHANGELOG.md) very carefully before you upgrade as there are many breaking changes going from V0.9.1 to 0.10.0
>
> You will also need Home Assistant **2021.11+** to upgrade to V0.10.0 as well.

The UniFi Protect Integration adds support for retrieving Camera feeds and Sensor data from a UniFi Protect installation on either a Ubiquiti CloudKey+,  Ubiquiti UniFi Dream Machine Pro (UDMP) or UniFi Protect Network Video Recorder (UNVR).

There is support for the following entity types within Home Assistant:
* Camera
* Sensor
* Binary Sensor
* Switch
* Select
* Number

It supports both regular Ubiquiti Cameras and the UniFi Doorbell. Camera feeds, Motion Sensors, Doorbell Sensors, Motion Setting Sensors and Switches will be created automatically for each Camera found, once the Integration has been configured.

Go to [Github](https://github.com/briis/unifiprotect) for Pre-requisites and Setup Instructions.
