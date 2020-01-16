set autorun_val=call %~dp0cmd_autoexec.bat
reg add "HKEY_CURRENT_USER\Software\Microsoft\Command Processor" /v "Autorun" /t REG_SZ /d "%autorun_val%"
