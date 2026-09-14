@echo off
setlocal

set "SDK_ENV="
for %%T in (cp314 cp313 cp312 cp311 cp310) do if not defined SDK_ENV if exist "%LOCALAPPDATA%\PyMotion\LiteSDK\venv-%%T\Scripts\activate.bat" set "SDK_ENV=%LOCALAPPDATA%\PyMotion\LiteSDK\venv-%%T"
if not defined SDK_ENV if exist "%LOCALAPPDATA%\PyMotion\LiteSDK\venv\Scripts\activate.bat" set "SDK_ENV=%LOCALAPPDATA%\PyMotion\LiteSDK\venv"

if not defined SDK_ENV (
    echo ERROR: PyMotion Lite SDK environment was not found.
    echo Run install.bat first.
    pause
    exit /b 2
)

call "%SDK_ENV%\Scripts\activate.bat"
title PyMotion Lite SDK
echo PyMotion Lite SDK environment activated.
echo Python: %SDK_ENV%\Scripts\python.exe
echo Examples: %~dp0examples
if defined PYMOTION_TERMINAL_NO_SHELL exit /b 0
cmd.exe /k
