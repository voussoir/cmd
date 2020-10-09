@echo off
REM 1. Go to or create "HKCU\Software\Microsoft\Command Processor"
REM 2. Create string value "Autorun"
REM 3. Set its value to "call <path_to_this_file>"
REM And now all of these commands will be invisibly executed in every new cmd window.
REM I use it to set doskeys which are as close as Windows gets to unix aliases.

doskey .=cd.
doskey ..=cd..
doskey ...=start.
doskey \=cd\
doskey gc=gitcheckup $*
