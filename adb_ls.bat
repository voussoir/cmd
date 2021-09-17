@echo off

echo ENABLED
echo =======
adb shell pm list packages -e | sorted !i

echo.

echo DISABLED
echo ========
adb shell pm list packages -d | sorted !i
