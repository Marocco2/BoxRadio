#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
; #Warn  ; Enable warnings to assist with detecting common errors.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.

UrlDownloadToFile, https://raw.githubusercontent.com/Marocco2/PitConfig-Marocco2-version/master/apps/python/PitConfig/Hotkey.exe, Hotkey.exe
UrlDownloadToFile, https://raw.githubusercontent.com/Marocco2/PitConfig-Marocco2-version/master/apps/python/PitConfig/PitConfig.py, PitConfig.py
Exit