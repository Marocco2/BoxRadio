#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
; #Warn  ; Enable warnings to assist with detecting common errors.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.

IniRead, key, PitConfig.ini, HOTKEY, key
Hotkey, %key%, Prs
return

Prs:
IniRead, preset, PitConfig.ini, PRESET, num, 1
preset := ++preset
if preset = 5
	preset = 1
IniWrite, %preset%, PitConfig.ini, PRESET, num
return