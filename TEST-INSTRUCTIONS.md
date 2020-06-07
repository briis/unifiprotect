# NEED TESTERS for next release of Unifi Protect for Home Assistant

Home Assistant is moving away from *Custom Components* and towards *Integrations* and has been doing so for a while. The main purpose of that is most likely to ready the whole eco system for V1.0 of Home Assistant. One main goal to be reached for V1.0 is that you should not need to edit *Yaml* files to get your system up and running.

So to achieve this, I have now converted the *unifiprotect* Custom Component to an *Integration* This means that everything is now setup using a Form from the Integrations page in Home Assistant. And as I don't want to maintain more complexity than necessary, I have decided to remove the Yaml configuration completely.  
I know some people have strong feelings about 'to Yaml or not to Yaml' but looking at the number of Configuration Options we need for this Integration, it makes perfectly sense to me, to remove the Yaml option.

**Disclaimer** Even though the core of the system has not changed from V0.3.3 for this version, and as such should be *production ready*, I strongly advise that that this test version is installed on a non-critical HA Instance. During the test, basic things may change, and then you will need to de-install and install again, loosing your current setup.

## Whats new?

There are not that many new things in here, but the ones that are will make the old setup **break**.
* The setup is changed from adding settings to `configuration.yaml` and other yaml files, to using the *Integration Page* from the *Settings Menu*. It should be clear enough what you need to enter, but that is part of the testing.
* Previously there was a module called `unifi_protect_server.py` distributed with the Custom Component. This has now been moved to *PyPi.org* as a separate module called [pyunifiprotect](https://github.com/briis/pyunifiprotect). So if anyone wants to change or develop on the core API logic, you need to Fork that module now.
* It should now be possible to add more than one instance of this Integration to Home Assistant. So if you have more that one UDMP or CloudKey+ you should be able to add them all. I have only one CloudKey+, so I have not been able to test this.
* Due to the support of more Instances, the naming of the Cameras, Sensors, Binary Sensors and Switches have changed. So if you would install this on an existing system, you would have to change automations etc.

## What needs to be tested?
For everyone that wants to try this out, I would like you test one or more of the following:
* General stability of the system
* The setup process using the Form - Is it logical, anything you miss to be able to specify?
* Does it support more than ONE instance? So hopefully, someone with more HW than me, could test this.
* If anyone wants to translate the form text to something else than English and Danish, you can go to the `translation` directory and copy the `en.json` file to your own language code, and submit the file to Github.

Please don't use the Home Assistant Forum for feedback, but instead use the [Issue Page](https://github.com/briis/unifiprotect/issues) on Github for feedback and bug reporting.

## Setup Instructions

I have not made this available in HACS, so it will require a manual installation while testing. 

The source of this new version (Called 0.4.0) can be found [here](https://github.com/briis/unifiprotect/tree/v0.4.0/custom_components/unifiprotect)

1. If you already have an earlier version of unifiprotect installed, you must remove that from your configuration files, delete the files in the `custom_components/unifiprotect` directory (or deinstall via HACS) and restart HA.
2. Copy all the files from the directory given about to `custom_components/unifiprotect` in your Home Assistant installation and restart HA.
3. Go to *Settings* and then *Integration* and search for Unifi Protect
4. Select the Integration, fill out the form and press Save. Once this is done, you should now have all Entities of Unifi Protect present in Home Assistance.

Have fun.
/B
