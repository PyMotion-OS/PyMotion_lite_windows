param(
    [Parameter(Mandatory = $true)]
    [string]$SdkPython,

    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$PythonArguments
)

$ErrorActionPreference = "Stop"
trap {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path -LiteralPath $SdkPython -PathType Leaf)) {
    throw "The PyMotion Lite SDK Python executable was not found: $SdkPython"
}

& $SdkPython -u @PythonArguments
exit $LASTEXITCODE
