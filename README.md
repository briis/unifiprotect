# Unifi Protect for Home Assistant
Unifi Protect Integration for Home Assistant

This is a Home Assistant Integration for Ubiquiti's Unifi Protect Surveillance system.

This Home Assistant integration is inspired by [danielfernau's video downloader program](https://github.com/danielfernau/unifi-protect-video-downloader) and the Authorization implementation is copied from there.

Basically what this does, is integrating the Camera feeds from Unifi Protect in to Home Assistant, and furthermore there is an option to get Binary Motion Sensors and Sensors that show the current Recording Settings pr. camera.

## Prerequisites
Before you install this Integration you need to ensure that the following two settings are applied in Unifi Protect:
1. **Local User needs to be added** Open Unifi Protect in your browser. Click the USERS tab and you will get a list of users. Either select and existing user, or create a new one. The important thing is that the user is part of *Administrators* and that a local username and password is set for that user. ![User Settings](https://github.com/briis/unifiprotect/blob/master/images/user_setup.png) <!-- .element height="50%" width="50%" -->
This is the username and password you will use when setting up the Integration later.
2. **RTSP Stream** Select each camera under the CAMERAS tab, click on the camera and you will get a menu on the right side. Click the MANAGE button and there will be a menu like the picture below. (If you can't see the same picture click the + sign to the right of RTSP). Make sure that at least one of the streams is set to on. It does not matter whcich one, or if you select more than one. The integration will pick the one with the highest resolution. ![RTSP Settings](https://github.com/briis/unifiprotect/blob/master/images/rtsp_setup.png)
