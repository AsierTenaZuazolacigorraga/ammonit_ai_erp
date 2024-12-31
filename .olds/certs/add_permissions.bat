@echo off

REM Change path to the current execution file
set currentdir=%~dp0
cd %currentdir%

echo Restore permissions
cd permissions
takeown /R /F *
attrib -r *.* /s
icacls * /t /q /c /reset
icacls * /inheritance:r /grant %username%:RW
cd %currentdir%
