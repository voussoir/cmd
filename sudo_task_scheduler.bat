rem Run as administrator!
rem https://docs.microsoft.com/en-us/sysinternals/downloads/psexec
PsExec -i -s %windir%\system32\mmc.exe /s taskschd.msc
