# TODO list for UniFi Protect Integration

The following are items that are on my ToDo List.

* **Convert to Integration** - To make this in to a V1.0 product, it needs to conform with the way Home Assistant is driving new development. This means that we need to get away from the Yaml configuration and make it in to a real Integration that can be configured from the Integration Page. In order to do that, I will have to do the following:
  * A good first step has already been taken as the whole component is now converted to Async, to adhere to the standards of Home Assistant.
  * Next step will be to separate the I/O logic (`unifi_protect_server.py`) in to a *PyPi* component, so that it is separated from the HA modules. I have already reserved *pyunifiprotect* as a module name, and converting the current logic to this, is not that difficult.
  * With that done, all the modules that depend on `unifi_protect_server.py` need to call the new I/O logic module
  * Then I need to write the whole Config Flow module. I have practiced a bit on a few other Integrations, and I am positive I can produce a working Flow, maybe still with some flaws. This btw, also requires that Logos are uploaded to the new Brands repository, which I have done already.
  * When Config Flow is implemented, all modules need to be updated to use that, instead of the Yaml configuration. I have decided to abandon Yaml completely, as this Integration does not need a lot of tweaking that can't be handled from the Config Flow.
  * That is more or less it. This will give a few Breaking Changes once released, but I belive it is worth it.
