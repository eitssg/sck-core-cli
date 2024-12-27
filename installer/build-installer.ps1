param (
    [string]$InnoSetupPath = "C:\Program Files (x86)\Inno Setup 6\iscc.exe",
    [string]$SetupScriptPath = ".\coresetup.iss",
    [string]$PyInstallerPath = "pyinstaller",
    [string]$PyInstallerSpecFile = "core.spec",
    [string]$NexusRepoPath = "repository/files/core-automation",
    [string]$SourceDir = "D:\Development\core-automation\sck-mod-core",
    [string]$AppVersion
)

# Function to invoke a command and check for success
function Invoke-CommandWithArgs {
    param (
        [string]$Command,
        [string[]]$Arguments
    )

    & $Command $Arguments
    if ($LASTEXITCODE -ne 0) {
        Write-Error "$Command failed with exit code $LASTEXITCODE"
        exit $LASTEXITCODE
    }
}

# Fetch the version from Poetry if AppVersion is not provided
if (-not $AppVersion) {
    try {
        $AppVersion = $(poetry version -s)
        if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($AppVersion)) {
            Write-Error "Failed to get version from Poetry"
            exit 1
        }
    } catch {
        Write-Error "Failed to get version from Poetry"
        exit 1
    }
}

# Save the current directory
$CurrentDirectory = Get-Location

# Get the parent directory of the current directory
$ParentDirectory = Split-Path -Parent $CurrentDirectory

# Change to the parent directory to run PyInstaller
Set-Location $ParentDirectory

# Run Poetry update
Write-Output "Running Poetry update..."
Invoke-CommandWithArgs "poetry" @("update")

Write-Output "Poetry update completed successfully."

# Run Poetry build
Write-Output "Running Poetry build..."
Invoke-CommandWithArgs "poetry" @("build")

Write-Output "Poetry build completed successfully."

# Remove 'dist\core' folder if it exists
$DistCorePath = Join-Path $ParentDirectory "dist\core"
if (Test-Path $DistCorePath) {
    Remove-Item -Recurse -Force $DistCorePath
    Write-Output "The folder 'dist\core' has been removed."
}
Write-Output "Distribution will be saved to 'dist\core'"

# Run PyInstaller
Write-Output "Running PyInstaller..."
Invoke-CommandWithArgs $PyInstallerPath @($PyInstallerSpecFile)

Write-Output "PyInstaller build completed successfully."

# Change back to the original directory
Set-Location $CurrentDirectory

# Remove all *.exe and *.zip files from the current directory
Write-Output "Removing all *.exe and *.zip files from the current directory..."
Get-ChildItem -Path $CurrentDirectory -Filter *.exe -Recurse | Remove-Item -Force
Get-ChildItem -Path $CurrentDirectory -Filter *.zip -Recurse | Remove-Item -Force
Write-Output "All *.exe and *.zip files have been removed."

# Check if Inno Setup compiler exists
if (-Not (Test-Path $InnoSetupPath)) {
    Write-Error "Inno Setup compiler not found at path: $InnoSetupPath"
    exit 1
}

# Check if the setup script exists
if (-Not (Test-Path $SetupScriptPath)) {
    Write-Error "Setup script not found at path: $SetupScriptPath"
    exit 1
}

# Run the Inno Setup compiler with the setup script and version parameter
Write-Output "Running Inno Setup Compiler..."
Invoke-CommandWithArgs $InnoSetupPath @("-dMyAppVersion=$AppVersion", "-dMySourceDir=$SourceDir", $SetupScriptPath)

Write-Output "Inno Setup compilation completed successfully."

# Construct the dynamic output filename
$OutputFileName = "coresetup-$AppVersion.exe"
$OutputFilePath = Join-Path $CurrentDirectory $OutputFileName

# Check if the output file exists
if (-Not (Test-Path $OutputFilePath)) {
    Write-Error "Output file not found: $OutputFilePath"
    exit 1
}

# Zip the output file
$ZipFileName = "coresetup-$AppVersion.zip"
$ZipFilePath = Join-Path $CurrentDirectory $ZipFileName

# Delete the zip file if it already exists
if (Test-Path $ZipFilePath) {
    Remove-Item -Force $ZipFilePath
    Write-Output "The existing zip file '$ZipFilePath' has been removed."
}

Write-Output "Zipping the output file..."
Add-Type -AssemblyName 'System.IO.Compression.FileSystem'

# Create a new zip archive and add the output file
$zip = [System.IO.Compression.ZipFile]::Open($ZipFilePath, [System.IO.Compression.ZipArchiveMode]::Create)
try {
    [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile($zip, $OutputFilePath, [System.IO.Path]::GetFileName($OutputFilePath), [System.IO.Compression.CompressionLevel]::Optimal)
} finally {
    $zip.Dispose()
}

# Check if the zip file was created
if (-Not (Test-Path $ZipFilePath)) {
    Write-Error "Zip file not found: $ZipFilePath"
    exit 1
}

# Nexus repository URL
$NexusUrl = "https://${env:NEXUS_SERVER}/$NexusRepoPath/$ZipFileName"

# Upload the zip file to Nexus repository using Invoke-WebRequest
Write-Output "Uploading $ZipFileName to Nexus repository..."
Write-Output "Be patient, this may take a while..."

$Headers = @{
    Authorization = "Basic " + [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("${env:NEXUS_USERNAME}:${env:NEXUS_PASSWORD}"))
}

Invoke-WebRequest -Uri $NexusUrl -Method Put -InFile $ZipFilePath -Headers $Headers

Write-Output "File uploaded to Nexus repository successfully."
Write-Output ""
Write-Output "You may download the installer from the following URL: ${NexusUrl}"
Write-Output ""
Write-Output "Installer build process completed successfully."
exit 0
