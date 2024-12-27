# Core Automation Installer

This installer will generate a windows executeable for Core Automation core.exe and a setup program called coresetup.exe

## Description

When you run the probram "runner-windows.p1" the script will execute build-installer.ps1 passing the appropriate parameters.

The parametrers are:

* InnoSetupPath \
  Default: C:\Program Files (x86)\Inno Setup 6\iscc.exe
* SetupScriptPath \
  Default: .\coresetup.iss
* PyInstallerPath \
  Default: pyinstaller
* PyInstallerSpecFile \
  Default: core.spec
* NexusRepoPath \
  Default: repository/files/core-automation
* AppVersion \
  Default: none

It will call pyinstaller to generate a windows exeutable called core.exe which will be in the dist\core folder inside the
project folder.

The python project is a peotry project using poetry-dynamic-versioning.  As such a version number is automatically derrived
from the git repository TAGS.  The tag must begin with a 'v'.  Example v1.0.4, v1.2.3.

The version number must comply with PEP 440 style guide.

Once the windows executable is generated, the script will use Inno Seetup 6 (please see the instructions at https://jrsoftware.org/isdl.php)

The coresetup program is naamed with the version number. For example, coresetup-1.0.4.exe.

The seetuup program is zipped up and uploaded to nexus.

In order for the upload to nexus to work, you must supply the environment variables:

NEXUS_SEVER = http://myserver
NEXUS_USERNAME = my username
NEXUS_PASSWORD = my password

The default repository is '/files'.  If you wish to change the repository, update the runner-windows.ps1 with the approprite path.

Once complete you will be able to download the installer from Nexus repository.

## Runner

Execute: runner-windows.ps1
```powershell
pwsh -WorkingDirectory "$(Get-Location)" `
   -File ".\build-installer.ps1" `
   -InnoSetupPath "C:\Program Files (x86)\Inno Setup 6\iscc.exe" `
   -NexusServer "${env:NEXUS_SERVER}"
```

## Installing

#### Step 1
Download the core automation coresetup.exe program from nexus:

```text
PS C:\> curl -sSL -u "${env:NEXUS_USERNAME}:${env:NEXUS_PASSWORD}" -o coresetup-1.0.4.zip `
   https://${env:NEXUS_SERVER}/repository/files/core-automation/coresetup-1.0.4.zip
```

#### Step 2
Unzip the file

```text
PS C:\> 7z x .\coresetup-1.0.4.zip
```

#### Step 3
Run the setup/intallerr

```text
PS C:\> .\coresetup-1.0.4.exe
```

There will be two updates to your environment variables.  A new variable called CORE_HOME will be set
and the PATH will be updated so you can run "core.exe" right from your command line.

```text
PS C:\> core -h
Usage: core [<tasks>] [<options>]

Core Autmation Module v1.0.4

Default tasks: package upload compile deploy
  <tasks>                  Available tasks:
                             package         Package application files (platform/package.sh)
                             upload          Upload the package to the S3 bucket for deployment
                             compile         Compile the application and generate Actions
                             deploy          Execute the application Actions
                             release         Release the deployed application
                             teardown        Teardown the deployed application
                             configure       Configure client vars

Available options:
  -h, --help               show this help message and exit
  -c , --client            Client name, used for resource prefixes
  -s , --scope             Scope name
  -p , --portfolio         Portfolio name
  -a , --app               App name
  -b , --branch            Branch name
  -n , --build             Build name
  --aws-profile            AWS profile name
  --bucket-name            S3 bucket name
  --bucket-region          S3 bucket region, default "ap-southeast-1"
  --automation-type        Automation type [deployspec, pipeline], default is pipeline
  --extra-facts-json       Supply extra facts to the compiler. Must be a valid json string.
  --invoker-name           Invoker Lambda name
  --invoker-branch         Invoker Lambda branch. Takes precedence over the --invoker-name option.
  --invoker-region         Invoker Lambda region, default "ap-southeast-1"
  --automation-account     Automaton AWS Account ID
  --organization_account   Master/Payer Organization Account
  --organization_id        AWS Organization ID
  --master-region          AWS region for the master Automation account
  --force                  Set to 'true' to force through an action if it has protection checks on it -- see teardown.
  --show                   For configure task, show the current configuration file

Options can also be set via environment variables:
    TASKS
    PORTFOLIO, APP, BRANCH, BUILD
    SCOPE
    AUTOMATION_TYPE
    BUCKET_NAME, BUCKET_REGION
    INVOKER_LAMBDA_NAME, INVOKER_LAMBDA_REGION

Copyright (c) 2024 Core Developer. All rights reserved.
```

#### Step 4 (optional)

Every invocation of the 'core.exe' application will require that you supply tbe '-c, --client' option.

We recommend that you open your Environment Variables control panel and set this variable so you
no longer need to add it.  Note, that in core.exe, this is used to set AWS_PROFILE if AWS_PROFILE is
not already set.

```pwershell
$env:CLIENT = "simple"
```

#### Step 5

Configure the core platform by running the "core configure" command.  Find your 'client_vars.yaml' file which
will have the values you need.  If you do this step, then you don't need to have the 'simple-config' git repository
checked out on your drive and these values will be written to $HOME/.core/config.

*NOTE: If you specified the environment variable CLIENT=simple, then you don't need the --client opton.*

```text
PS C:\> core configure --client simple
Core Automation Configuration

Enter configuration values for client: simple

Enter a dash (-) to remove the value
Default master region []: ap-southeast-1
Default client region []: ap-southeast-1
Automation account []: 4xxxxxxxxxxx
Automation bucket region []: ap-southeast-1
Organization account []: 6xxxxxxxxxxx
Organization id []: org-xxxxxxxx
IAM Account []: 2xxxxxxxxxxx
Scope prefix []:
```

## Contributions

You may contact James Barwick <james.barwick@simple.com> for details on how to enhance the installer
