@echo off
setlocal
cd /d "%~dp0"

set "POWERSHELL_EXE=%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe"
if not exist "%POWERSHELL_EXE%" (
    echo ERROR: Windows PowerShell is unavailable.
    set "INSTALL_EXIT_CODE=2"
    goto :finished
)

if exist "%~dp0RELEASE-MANIFEST.json" goto :customer_install

set "SOURCE_ROOT="
set "DEV_SETUP="
if exist "%~dp0pyproject.toml" if exist "%~dp0src\pymotion_lite" if exist "%~dp0tools\setup_windows_dev.ps1" set "SOURCE_ROOT=%~dp0"
if not defined SOURCE_ROOT if exist "%~dp0..\pyproject.toml" if exist "%~dp0..\src\pymotion_lite" if exist "%~dp0..\tools\setup_windows_dev.ps1" set "SOURCE_ROOT=%~dp0..\"
if not defined SOURCE_ROOT if exist "%~dp0..\..\pyproject.toml" if exist "%~dp0..\..\src\pymotion_lite" if exist "%~dp0..\..\tools\setup_windows_dev.ps1" set "SOURCE_ROOT=%~dp0..\..\"
if not defined SOURCE_ROOT if exist "%~dp0..\..\..\pyproject.toml" if exist "%~dp0..\..\..\src\pymotion_lite" if exist "%~dp0..\..\..\tools\setup_windows_dev.ps1" set "SOURCE_ROOT=%~dp0..\..\..\"
if defined SOURCE_ROOT set "DEV_SETUP=%SOURCE_ROOT%tools\setup_windows_dev.ps1"
if defined DEV_SETUP goto :developer_install

echo ERROR: This directory is neither a signed customer bundle nor a complete source checkout.
echo Installer directory: %~dp0
echo.
echo Customer installation requires RELEASE-MANIFEST.json and the complete signed bundle
echo beside install.bat. Developer setup requires pyproject.toml, src\pymotion_lite,
echo and tools\setup_windows_dev.ps1 in the source checkout.
echo Do not copy install.bat by itself.
set "INSTALL_EXIT_CODE=2"
goto :finished

:customer_install
set "INSTALL_MODE=customer"
echo Installing from a signed PyMotion Lite customer bundle...
"%POWERSHELL_EXE%" -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0install.ps1" %*
set "INSTALL_EXIT_CODE=%ERRORLEVEL%"
goto :finished

:developer_install
set "INSTALL_MODE=developer"
echo Source checkout detected; preparing an isolated developer environment...
echo Source root: %SOURCE_ROOT%
"%POWERSHELL_EXE%" -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%DEV_SETUP%" %*
set "INSTALL_EXIT_CODE=%ERRORLEVEL%"

:finished
if not defined INSTALL_EXIT_CODE set "INSTALL_EXIT_CODE=1"
if "%INSTALL_EXIT_CODE%"=="0" (
    echo.
    echo Installation completed.
    if "%INSTALL_MODE%"=="customer" (
        if exist "%~dp0open-sdk-vscode.bat" echo Run open-sdk-vscode.bat to open the examples in VS Code with the correct Python.
        echo Run open-sdk-terminal.bat to use the SDK from a terminal.
    ) else (
        echo Use the developer environment activation command printed above.
    )
    if not defined PYMOTION_INSTALL_NO_PAUSE pause
) else (
    echo.
    echo Installation failed with exit code %INSTALL_EXIT_CODE%.
    echo Review the error above. PyMotion Lite requires 64-bit CPython 3.10 through 3.14.
    if not defined PYMOTION_INSTALL_NO_PAUSE pause
)
exit /b %INSTALL_EXIT_CODE%
