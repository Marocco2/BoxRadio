#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
; #Warn  ; Enable warnings to assist with detecting common errors.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.

FileRead, CurrVer, version.txt
UrlDownloadToFile, https://raw.githubusercontent.com/Marocco2/PitConfig-Marocco2-version/master/apps/python/PitConfig/version.txt, version.txt
FileRead, NewVer, version.txt
IniRead, EnableOTA, PitConfig.ini, AUTOUPDATE, Enable, 1
if (CurrVer != NewVer and EnableOTA == 1) {
	UrlDownloadToFile, https://raw.githubusercontent.com/Marocco2/PitConfig-Marocco2-plugin/%NewVer%/apps/python/PitConfig/Hotkey.exe, Hotkey.exe
	UrlDownloadToFile, https://raw.githubusercontent.com/Marocco2/PitConfig-Marocco2-plugin/%NewVer%/apps/python/PitConfig/PitConfig.py, PitConfig.py
	UrlDownloadToFile, https://raw.githubusercontent.com/Marocco2/PitConfig-Marocco2-plugin/%NewVer%/apps/python/PitConfig/CheckNewVersion.exe, CheckNewVersion.exe
	}
Exit