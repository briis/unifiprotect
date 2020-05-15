# NEED TESTERS for next release of Unifi Protect for Home Assistant

Home Assistant is moving away from *Custom Components* and towards *Integrations* and has been doing so for a while. The main purpose of that is most likely to ready the whole eco system for V1.0 of Home Assistant. One main goal to be reached for V1.0 is that you should not need to edit *Yaml* files to get your system up and running.

So to achieve this, I have now converted the *unifiprotect* Custom Component to an *Integration* This means that everything is now setup using a Form from the Integrations page in Home Assistant. And as I don't want to maintain more complexity than necessary, I have decided to remove the Yaml configuration completely.  
I know some people have strong feelings about 'to Yaml or not to Yaml' but looking at the number of Configuration Options we need for this Integration, it makes perfectly sense to me, to remove the Yaml option.

**Disclaimer** Even though the core of the system has not changed for this version, and as such should be *production ready*, I strongly advise that that this test version is installed on a non-critical HA Instance. During the test, basic things may change, and then you will need to de-install and install again, loosing your current setup.

## Whats new

There are not that many new things in here, but the ones there are will make the old setup **break**.
* The setup is changed from adding things to `configuration.yaml` and other yaml files, to using the *Integration Page* from the *Settings Menu*. It should be clear enough what you need to enter, but that is part of the testing.
* Previously there was a module called `unifi_protect_server.py` distributed with the Custom Component. This has now been moved to *PyPi.org* as a separate module called [pyunifiprotect](https://github.com/briis/pyunifiprotect). So if anyone wants to change or develop on the core API logic, you need to Fork that module now.
