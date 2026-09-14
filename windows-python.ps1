function Resolve-PyMotionPython {
    [CmdletBinding()]
    param(
        [string]$Python,
        [string[]]$PythonTags = @("cp310", "cp311", "cp312", "cp313", "cp314")
    )

    $allowedMinors = @()
    foreach ($tag in $PythonTags) {
        if ($tag -notmatch '^cp3(10|11|12|13|14)$') {
            throw "Unsupported Python tag in the signed bundle: $tag"
        }
        $allowedMinors += [int]$Matches[1]
    }
    $allowedMinors = @($allowedMinors | Sort-Object -Unique -Descending)
    if ($allowedMinors.Count -eq 0) {
        throw "The signed bundle does not declare any supported CPython wheel tags."
    }

    $probe = "import json, platform, struct, sys; print(json.dumps({'executable': sys.executable, 'implementation': platform.python_implementation(), 'major': sys.version_info[0], 'minor': sys.version_info[1], 'micro': sys.version_info[2], 'bits': struct.calcsize('P') * 8}))"
    $candidates = @()
    if (-not [string]::IsNullOrWhiteSpace($Python)) {
        $candidates += [PSCustomObject]@{ Command = $Python; Arguments = @(); Label = $Python }
    } else {
        $launcher = Get-Command py.exe -ErrorAction SilentlyContinue
        if ($null -ne $launcher) {
            foreach ($minor in $allowedMinors) {
                $candidates += [PSCustomObject]@{
                    Command = $launcher.Source
                    Arguments = @("-3.$minor")
                    Label = "CPython 3.$minor via py.exe"
                }
            }
        }
        foreach ($commandName in "python.exe", "python3.exe") {
            $command = Get-Command $commandName -ErrorAction SilentlyContinue
            if ($null -ne $command) {
                $candidates += [PSCustomObject]@{
                    Command = $command.Source
                    Arguments = @()
                    Label = $command.Source
                }
            }
        }
    }

    if ($candidates.Count -eq 0) {
        throw "No Python interpreter was found. Install 64-bit CPython 3.10 through 3.14, then run this installer again."
    }

    $rejected = New-Object System.Collections.Generic.List[string]
    foreach ($candidate in $candidates) {
        $output = $null
        try {
            $output = & $candidate.Command @($candidate.Arguments) -c $probe 2>$null
            $probeExitCode = $LASTEXITCODE
        } catch {
            continue
        }
        if ($probeExitCode -ne 0 -or $null -eq $output) {
            continue
        }
        try {
            $info = @($output)[-1] | ConvertFrom-Json
        } catch {
            continue
        }
        $version = "$($info.major).$($info.minor).$($info.micro)"
        if (
            $info.implementation -eq "CPython" -and
            [int]$info.major -eq 3 -and
            [int]$info.minor -in $allowedMinors -and
            [int]$info.bits -eq 64
        ) {
            return [PSCustomObject]@{
                Executable = [string]$info.executable
                Version = $version
                PythonTag = "cp$($info.major)$($info.minor)"
            }
        }
        $rejected.Add("$($candidate.Label): $($info.implementation) $version, $($info.bits)-bit")
    }

    $detail = if ($rejected.Count -gt 0) { " Found " + ($rejected -join "; ") + "." } else { "" }
    $requiredVersions = ($allowedMinors | ForEach-Object { "3.$_" }) -join ", "
    throw "This PyMotion Lite bundle requires 64-bit CPython $requiredVersions.$detail Use -Python C:\path\to\python.exe to select an interpreter explicitly."
}
