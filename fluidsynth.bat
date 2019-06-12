@echo off
set filename=%1
set filename=%filename:.mid=.wav%

D:\software\fluidsynth\fluidsynth.exe --gain 1 -F %filename% D:\software\fluidsynth\Scc1t2.sf2 %1%