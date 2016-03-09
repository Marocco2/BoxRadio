#PitConfig Marocco2 version (M2V) V1

Based on the Pit Menu (by NAGP MadMac) and [PitConfig](http://www.assettocorsa.net/forum/index.php?threads/pitconfig.28683/), this modified version has the following characteristics:

- The app is used to configure the work to be performed on the pit prior to stopping the car on the pit spot. Note: Pit Stops are available only in Multiplayer at the moment.
- Works on any screen resolution (may not work in window mode).
- ~~Does not require any external executable. All code is in the python module.~~
- **It's self-updating**
- Identifies the tyres available for original AC cars and mod cars.
- Works also on servers that limit the allowable tyres.
- Does not require any button to start the pit work. You just need to stop on the pit spot and the pit stop starts automatically.
- Option on PitConfig.ini to configure the fueling method. Set to "1" (Default) to ADD the fuel to the amount already in the tank or set to "0" to fill the tank up to the amount selected on the app.
- "Fill" button available to complete the tank.
- Preset system for different strategies. Presets are saved on exit and are available the next time AC is initiated if the car is not changed.
- Compact scalable UI. You can increase the UI size changing the "sizemultiplier" option of PitConfig.ini. For instance, set "UI / sizemultiplier" to "1.2" in order to increase UI size in 20% (min: 1.0, max: 3.0).

Just install and activate as any other AC app.

###M2V V1.2
- Fixed hotkey not working
- Bug: Cannot select preset with mouse, only hotkey
- Redone update logic

###M2V V1.1
- Now PitConfig will update itself.

###M2V V1
- Adds an hotkey (keyboard or joystick input) to switch preset on-the-fly

###V1.4
- Support for Mod Car Tyres and for servers limiting tyre compounds. App now reads the tyres from AC log.txt. This way it can identify also mod car tyres and also checks if the server has limited the allowable tyres. If AC log.txt is not found, the previous method is used, reading the tyres from server manager ks_tyres.ini.

###V1.3
- UI now uses default AC pitstop icons instead of ugly checkboxes. Much cleaner look in my opinion. 
- Due to the change on the UI, the Full Size UI is discontinued, however you can increase the UI size changing the "sizemultiplier" option of PitConfig.ini. For instance, set "UI / sizemultiplier" to "1.2" in order to increase UI size in 20% (min: 1.0, max: 3.0).
- Fix for a bug on the preset system that could cause the app to crash on startup.

###V1.2
- New preset system for different strategies. Presets are saved on exit and are available the next time AC is initiated if the car is not changed.
- Compact UI. Old UI is still available selecting "0" on the "compact" option of PitConfig.ini.

###V1.1
- Added option on PitConfig.ini to configure the fueling method. Set to "1" (Default) to ADD the fuel to the amount already in the tank or set to "0" to fill the tank up to the amount selected on the app.

###V1.0
- First Release




