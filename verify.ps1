$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (Test-Path -LiteralPath .\NOT_FOR_DISTRIBUTION.txt) {
    throw "This is a staging bundle and is not authorized for installation."
}
$evaluation = Test-Path -LiteralPath .\EVALUATION_ONLY.txt -PathType Leaf

$required = @(
    ".\RELEASE-MANIFEST.json",
    ".\RELEASE-MANIFEST.sig",
    ".\RELEASE-CERTIFICATE.cer",
    ".\SHA256SUMS.txt",
    ".\requirements.lock"
)
foreach ($path in $required) {
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        throw "Missing release integrity file: $path"
    }
}

$certificate = New-Object System.Security.Cryptography.X509Certificates.X509Certificate2(
    (Resolve-Path -LiteralPath .\RELEASE-CERTIFICATE.cer).Path
)
if (-not $evaluation) {
    $chain = New-Object System.Security.Cryptography.X509Certificates.X509Chain
    $chain.ChainPolicy.RevocationMode = [System.Security.Cryptography.X509Certificates.X509RevocationMode]::NoCheck
    if (-not $chain.Build($certificate)) {
        $errors = ($chain.ChainStatus | ForEach-Object { $_.StatusInformation.Trim() }) -join "; "
        throw "Release certificate is not trusted by this computer: $errors"
    }
}

$manifestPath = (Resolve-Path -LiteralPath .\RELEASE-MANIFEST.json).Path
$manifestBytes = [System.IO.File]::ReadAllBytes($manifestPath)
$signatureText = (Get-Content -LiteralPath .\RELEASE-MANIFEST.sig -Raw).Trim()
try {
    $signature = [Convert]::FromBase64String($signatureText)
} catch {
    throw "Release signature is not valid base64."
}
$rsa = [System.Security.Cryptography.X509Certificates.RSACertificateExtensions]::GetRSAPublicKey($certificate)
if ($null -eq $rsa) {
    throw "Release certificate does not contain an RSA public key."
}
$signatureOk = $rsa.VerifyData(
    $manifestBytes,
    $signature,
    [System.Security.Cryptography.HashAlgorithmName]::SHA256,
    [System.Security.Cryptography.RSASignaturePadding]::Pkcs1
)
if (-not $signatureOk) {
    throw "Release manifest signature verification failed."
}

$manifest = Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
if ($manifest.schema -ne 1) {
    throw "Release manifest is not a schema-1 bundle."
}
if ($evaluation) {
    if ($manifest.evaluation -ne $true -or $manifest.production -ne $false) {
        throw "Evaluation marker and signed manifest disagree."
    }
    Write-Warning "INTERNAL EVALUATION BUILD: production release and HIL gates are incomplete."
} else {
    if ($manifest.production -ne $true -or $manifest.evaluation -eq $true) {
        throw "Release manifest is not a production bundle."
    }
    if ($manifest.release.release_state -ne "released" -or $manifest.release.hil_status -ne "PASS") {
        throw "Release manifest does not contain completed release gates."
    }
}
if ($manifest.target.name -ne "windows-x64" -or $manifest.target.os -ne "windows" -or $manifest.target.architecture -ne "amd64") {
    throw "Release manifest is not a Windows x64 bundle."
}
if ([System.Environment]::OSVersion.Platform -ne [System.PlatformID]::Win32NT) {
    throw "Windows bundle can only be installed on Windows."
}
if (([string]$env:PROCESSOR_ARCHITECTURE).ToUpperInvariant() -ne "AMD64") {
    throw "Windows x64 bundle requires an AMD64 host process architecture."
}

$bundleRoot = [System.IO.Path]::GetFullPath($PSScriptRoot)
$bundlePrefix = $bundleRoot.TrimEnd([System.IO.Path]::DirectorySeparatorChar) + [System.IO.Path]::DirectorySeparatorChar
foreach ($entry in $manifest.files) {
    $relative = [string]$entry.path
    if ([System.IO.Path]::IsPathRooted($relative) -or $relative.Contains("..") -or $relative.Contains("\")) {
        throw "Unsafe release manifest path: $relative"
    }
    $localRelative = $relative.Replace("/", [System.IO.Path]::DirectorySeparatorChar)
    $target = [System.IO.Path]::GetFullPath((Join-Path $bundleRoot $localRelative))
    if (-not $target.StartsWith($bundlePrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Release manifest path escapes the bundle: $relative"
    }
    if (-not (Test-Path -LiteralPath $target -PathType Leaf)) {
        throw "Missing signed release file: $relative"
    }
    $item = Get-Item -LiteralPath $target
    if ($item.Length -ne [long]$entry.bytes) {
        throw "Release file size mismatch: $relative"
    }
    $actualHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $target).Hash
    if ($actualHash -ne ([string]$entry.sha256).ToUpperInvariant()) {
        throw "Release file hash mismatch: $relative"
    }
}

$sumsHash = (Get-FileHash -Algorithm SHA256 -LiteralPath .\SHA256SUMS.txt).Hash
if ($sumsHash -ne ([string]$manifest.sha256sums_sha256).ToUpperInvariant()) {
    throw "SHA256SUMS.txt does not match the signed release manifest."
}

Write-Host "PyMotion Lite release signature and all file hashes are valid."
