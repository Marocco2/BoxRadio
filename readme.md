# BoxRadio V0.1

Based on the Pit Menu (by NAGP MadMac) and [PitConfig](http://www.assettocorsa.net/forum/index.php?threads/pitconfig.28683/), this modified version has the following characteristics:

- The app is used to configure the work to be performed on the pit prior to stopping the car on the pit stop.
- Works on any screen resolution.
- Does not require any external executable. All code is in the python module.
- **It's self-updating** `(WORK IN PROGRESS)`
- Identifies the tyres available for original AC cars and mod cars.
- Works also on servers that limit the allowable tyres.
- Does not require any button to start the pit work. You just need to stop on the pit spot and the pit stop starts automatically.
- Option on PitConfig.ini to configure the fueling method. Set to "1" (Default) to ADD the fuel to the amount already in the tank or set to "0" to fill the tank up to the amount selected on the app.
- "Fill" button available to complete the tank.
- Preset system for different strategies. Presets are saved on exit and are available the next time AC is initiated if the car is not changed.
- Compact scalable UI. You can increase the UI size changing the "sizemultiplier" option of PitConfig.ini. For instance, set "UI / sizemultiplier" to "1.2" in order to increase UI size in 20% (min: 1.0, max: 3.0).
- Hotkey system to change presets _on the fly_
- Speech recognition to:  `(WORK IN PROGRESS)`
    - request pit stop without moving the mouse
    - ask information about the standings


Just install and activate as any other AC app.
