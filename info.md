# // Unifi Protect for Home Assistant

![GitHub release (latest by date including pre-releases)](https://img.shields.io/github/v/release/briis/unifiprotect?include_prereleases&style=flat-square) [![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg?style=flat-square)](https://github.com/custom-components/hacs)

The Unifi Protect Integration adds support for retrieving Camera feeds and Sensor data from a Unifi Protect installation on either a Ubiquiti CloudKey+ or Ubiquiti Unifi Dream Machine Pro.

There is support for the following device types within Home Assistant:
* Camera
* Sensor
* Binary Sensor
* Switch

It supports both regular Ubiquiti Cameras and the Unifi Doorbell. Camera feeds, Motion Sensors, Doorbell Sensors, Motion Setting Sensors and Switches will be created automativally for each Camera found, once the Integration has been configured.

{% if prerelease %}
### NB!: This is a Beta version!

Version 0.4 is a total rewrite of the Unifi Protect Integration, and no longer supports configuration through Yaml. So if you upgrade to this version from a 0.3.x release, then you need to do the following:

1. You must remove all references to *unifiprotect* from your configuration files, and restart HA to clear it.
2. Go back to HACS, and install this pre-release. After the installation, you will have the option of entering the Integrations page to configure *Unifi Protect*.
3. Go to *Settings* and then *Integration* and search for Unifi Protect
4. Select the Integration, fill out the form and press Save. Once this is done, you should now have all Entities of Unifi Protect present in Home Assistance.

Go to [Github](https://github.com/briis/unifiprotect/tree/v0.4.0) for Pre-requisites and Setup Instructions.

{% else %}

Go to [Github](https://github.com/briis/unifiprotect) for Pre-requisites and Setup Instructions.

{% endif %}

