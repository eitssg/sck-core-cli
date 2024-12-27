# Get the directory where the script is located
$D = Split-Path -Parent -Path $MyInvocation.MyCommand.Definition

# Build the path to the core.py script
$pythonScript = Join-Path -Path $D -ChildPath "core.py"

# Execute the Python script with arguments
python $pythonScript $args
