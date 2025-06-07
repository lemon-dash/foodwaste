@echo off
Setlocal Enabledelayedexpansion
set "str= "
for /f "delims=" %%i in ('dir /b *.*') do (
set "var=%%i" & ren "%%i" "!var:%str%=!")
@Echo Off&SetLocal ENABLEDELAYEDEXPANSION
FOR %%a in (*) do (
set "name=%%a"
set "name=!name:(=!"
set "name=!name:)=!"
ren "%%a" "!name!"
)
exit
