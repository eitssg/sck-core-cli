
pwsh -WorkingDirectory "$(Get-Location)" `
   -File ".\build-installer.ps1" `
   -InnoSetupPath "C:\Program Files (x86)\Inno Setup 6\iscc.exe" `
   -SourceDir "D:\Development\core-automation-python\sck-mod-core" `
   -NexusServer "${env:NEXUS_SERVER}"
