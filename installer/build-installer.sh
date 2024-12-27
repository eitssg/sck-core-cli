#!/bin/bash

# Set Defaults
PyInstallerSpecFile=${PyInstallerSpecFile:-core.spec}
PyInstallerPath=${PyInstallerPath:-pyinstaller}
NexusRepoPath=${NexusRepoPath:-repository/files/core-automation}
SourceDir=${SourceDir:-./core-automation/sck-mod-core}
AppVersion=${AppVersion}

# Fetch the version from Poetry if AppVersion is not provided
if [ -z $AppVersion ]; then
  AppVersion=$(poetry version -s)
  if [ $? -ne 0 ]; then
      echo "Failed to get version from Poetry"
      exit 1
  fi
fi

# Save the current directory
CurrentDirectory=$(pwd)

# Get the parent directory of the current directory
ParentDirectory=$(dirname $CurrentDirectory)

# Change to the parent directory to run PyInstaller
cd $ParentDirectory

# Run Poetry update
echo "Running Poetry update..."
poetry update
if [ $? -ne 0 ]; then
  echo "Failed to update dependencies"
  exit 1
fi

echo "Poetry update completed successfully."

# Run Poetry build
echo "Running Poetry build..."
poetry build
if [ $? -ne 0 ]; then
  echo "Failed to build."
  exit 1
fi

echo "Poetry build completed successfully."

# Remove 'dist\core' folder if it exists
DistCorePath="$ParentDirectory/dist/core"
rm -rf "$DistCorePath"
echo "The folder 'dist\core' has been removed."
echo "Distribution will be saved to 'dist/core'"

# Run PyInstaller
echo "Running PyInstaller..."
$PyInstallerPath $PyInstallerSpecFile
if [ $? -ne 0 ]; then
  echo "Failed to successfully build executable."
  exit 1
fi

echo "PyInstaller build completed successfully."

# Change back to the original directory
cd $CurrentDirectory

# Remove all tar.gz files from the current directory
echo "Removing all previous archives the current directory..."
rm -f *.tar.gz
echo "All *.tar.gz files have been removed."

# Run the Inno Setup compiler with the setup script and version parameter
echo "Creating tar archive..."

# Check if the script is running on macOS
if [[ "$(uname)" == "Darwin" ]]; then
    echo "Running on macOS"
    TarFileName="core-$AppVersion-darwin.tar.gz"
else
    echo "Not running on macOS"
    TarFileName="core-$AppVersion.tar.gz"
fi

cd "$ParentDirectory/dist"
tar -czf "$CurrentDirectory/$TarFileName" core

# Change back to the original directory
cd $CurrentDirectory

if [ ! -f $TarFileName ]; then
   echo "Output file not found: $TarFileName"
   exit 1
fi

# Check if NEXUS_SERVER starts with "https://"
if [[ $NEXUS_SERVER != https://* ]]; then
    NEXUS_SERVER="https://$NEXUS_SERVER"
fi
# Nexus repository URL
NexusUrl="${NEXUS_SERVER}/$NexusRepoPath/$TarFileName"

# Upload the zip file to Nexus repository using Invoke-WebRequest
echo "Uploading $ZipFileName to Nexus repository..."
echo "Be patient, this may take a while..."

# Perform the curl request and capture the HTTP status code
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -u "$NEXUS_USERNAME:$NEXUS_PASSWORD" -T "$TarFileName" -X PUT "$NexusUrl")

# Check if the status code is 404
if [ "$HTTP_STATUS" -ne 200 ]; then
    echo "Failed to upload to Nexus: Received ${HTTP_STATUS} when uploading"
    echo "URL: $NexusUrl"
    echo "The repository \"${NexusRepoPath}\" is probably invalid or you don't have permission."
    exit 1
fi

echo "File uploaded to Nexus repository successfully."
echo ""
echo "You may download the installer from the following URL: ${NexusUrl}"
echo ""
echo "Installer build process completed successfully."

exit 0
