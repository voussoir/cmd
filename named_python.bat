@echo off

rem Because Python is interpreted, when you look at the task manager process
rem list you'll see that every running python instance has the same name,
rem python.exe. This scripts helps you name the executables so they stand out.
rem For the time being this script doesn't automatically call your new exe,
rem you have to write a second command to actually run it. Batch doesn't have a
rem good way to pass "all arguments after %1" to the new program.

set real=C:\Python\__latest\python.exe
set named=C:\Python\__latest\python-%1.exe
if not exist %named% (mklink /h %named% %real%) else (echo %named%)
