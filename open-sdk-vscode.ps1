param(
    [switch]$NoLaunch
)

$ErrorActionPreference = "Stop"
trap {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
Set-Location $PSScriptRoot

$manifestPath = Join-Path $PSScriptRoot "RELEASE-MANIFEST.json"
if (-not (Test-Path -LiteralPath $manifestPath -PathType Leaf)) {
    throw "Signed release manifest is missing. Use this launcher from a complete customer bundle."
}
$manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
$installationId = ([string]$manifest.sha256sums_sha256).Substring(0, 12)
$pythonTags = @($manifest.target.python_tags | ForEach-Object { [string]$_ })

$localAppData = [Environment]::GetEnvironmentVariable("LOCALAPPDATA")
if ([string]::IsNullOrWhiteSpace($localAppData)) {
    $localAppData = [Environment]::GetFolderPath([Environment+SpecialFolder]::LocalApplicationData)
}
if ([string]::IsNullOrWhiteSpace($localAppData)) {
    throw "Cannot determine the current user's local application data directory."
}

$pythonCandidates = [System.Collections.Generic.List[string]]::new()
$installationStatePath = Join-Path $localAppData "PyMotion\LiteSDK\installations\$installationId.json"
if (Test-Path -LiteralPath $installationStatePath -PathType Leaf) {
    $installationState = Get-Content -LiteralPath $installationStatePath -Raw | ConvertFrom-Json
    if (-not [string]::IsNullOrWhiteSpace([string]$installationState.venv_path)) {
        $pythonCandidates.Add((Join-Path ([string]$installationState.venv_path) "Scripts\python.exe"))
    }
}
foreach ($pythonTag in $pythonTags) {
    $pythonCandidates.Add((Join-Path $localAppData "PyMotion\LiteSDK\venv-$pythonTag\Scripts\python.exe"))
}
$pythonCandidates.Add((Join-Path $localAppData "PyMotion\LiteSDK\venv\Scripts\python.exe"))

$sdkPython = $null
foreach ($candidate in ($pythonCandidates | Select-Object -Unique)) {
    if (Test-Path -LiteralPath $candidate -PathType Leaf) {
        & $candidate -c "import pymotion as pm; assert pm.lite.__version__ == '1.0.1'"
        if ($LASTEXITCODE -eq 0) {
            $sdkPython = [System.IO.Path]::GetFullPath($candidate)
            break
        }
    }
}
if ([string]::IsNullOrWhiteSpace($sdkPython)) {
    throw "The installed PyMotion Lite SDK environment was not found or failed its import check. Run install.bat first."
}

$workspaceDirectory = Join-Path $localAppData "PyMotion\LiteSDK\workspaces\pymotion-lite-$installationId"
$projectDirectory = Join-Path $workspaceDirectory "project"
New-Item -ItemType Directory -Path $projectDirectory -Force | Out-Null
$editableExamples = Join-Path $projectDirectory "examples"
if (-not (Test-Path -LiteralPath $editableExamples -PathType Container)) {
    Copy-Item -LiteralPath (Join-Path $PSScriptRoot "examples") -Destination $editableExamples -Recurse
}
if (-not (Test-Path -LiteralPath (Join-Path $projectDirectory "README.md") -PathType Leaf)) {
    Copy-Item -LiteralPath (Join-Path $PSScriptRoot "docs\README.md") -Destination (Join-Path $projectDirectory "README.md")
}
if (-not (Test-Path -LiteralPath (Join-Path $projectDirectory "SDK_USER_MANUAL.md") -PathType Leaf)) {
    Copy-Item -LiteralPath (Join-Path $PSScriptRoot "docs\SDK_USER_MANUAL.md") -Destination (Join-Path $projectDirectory "SDK_USER_MANUAL.md")
}
$workspacePath = Join-Path $workspaceDirectory "pymotion-lite.code-workspace"
$pythonRunner = Join-Path $PSScriptRoot "run-sdk-python.ps1"
if (-not (Test-Path -LiteralPath $pythonRunner -PathType Leaf)) {
    throw "The signed PyMotion Lite Python runner is missing."
}
# Code Runner submits this command to the user's current terminal shell.  Start
# with an unquoted executable name, then let the signed wrapper invoke the
# possibly space-containing SDK Python path with PowerShell's call operator.
$pythonExecutor = 'powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "' + $pythonRunner + '" -SdkPython "' + $sdkPython + '"'
$workspace = [ordered]@{
    folders = @(
        [ordered]@{
            name = "PyMotion Lite SDK"
            path = $projectDirectory
        }
    )
    settings = [ordered]@{
        "python.defaultInterpreterPath" = $sdkPython
        "python.terminal.activateEnvironment" = $true
        "code-runner.executorMap" = [ordered]@{
            python = $pythonExecutor
        }
        "code-runner.runInTerminal" = $true
        "code-runner.ignoreSelection" = $true
    }
}
$workspace | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $workspacePath -Encoding UTF8

Write-Host "PyMotion Lite VS Code workspace is ready."
Write-Host "Python: $sdkPython"
Write-Host "Editable examples: $editableExamples"
Write-Host "Workspace: $workspacePath"
if ($NoLaunch) {
    exit 0
}

$vsCodeCandidates = [System.Collections.Generic.List[string]]::new()
$codeCommand = Get-Command code.cmd -ErrorAction SilentlyContinue | Select-Object -First 1
if ($null -ne $codeCommand) {
    $vsCodeCandidates.Add($codeCommand.Source)
}
$codeCommand = Get-Command code.exe -ErrorAction SilentlyContinue | Select-Object -First 1
if ($null -ne $codeCommand) {
    $vsCodeCandidates.Add($codeCommand.Source)
}
if (-not [string]::IsNullOrWhiteSpace($env:LOCALAPPDATA)) {
    $vsCodeCandidates.Add((Join-Path $env:LOCALAPPDATA "Programs\Microsoft VS Code\Code.exe"))
}
if (-not [string]::IsNullOrWhiteSpace($env:ProgramFiles)) {
    $vsCodeCandidates.Add((Join-Path $env:ProgramFiles "Microsoft VS Code\Code.exe"))
}
if (-not [string]::IsNullOrWhiteSpace(${env:ProgramFiles(x86)})) {
    $vsCodeCandidates.Add((Join-Path ${env:ProgramFiles(x86)} "Microsoft VS Code\Code.exe"))
}
$vsCode = $vsCodeCandidates | Where-Object { Test-Path -LiteralPath $_ -PathType Leaf } | Select-Object -First 1
if ([string]::IsNullOrWhiteSpace($vsCode)) {
    throw "Visual Studio Code was not found. Install VS Code, then run open-sdk-vscode.bat again."
}

& $vsCode --new-window $workspacePath
if ($LASTEXITCODE -ne 0) {
    throw "Visual Studio Code exited with code $LASTEXITCODE."
}
