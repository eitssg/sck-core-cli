"""
Core Automation application entry points
"""
import sys
from dotenv import load_dotenv
load_dotenv(override=True)

from core_cli import register_module, parse_args, execute, __version__  # noqa: E402


def core_module(args):
    """
    This is the main entry point for the 'core' command when not run within
    the SCK.  This function duplicates what the SCK will do.  If you are using core.exe executable,
    this will run.  If you have installed the sck-mod-core package in your python SCK environment,
    then the SCK will call the three functions in the sck_mod_core module.

    Args:
        args (list): command-line arguments
    """
    try:
        registration_data = {
            "name": "SCK",
            "description": "SCK Autmation Engine",
            "version": __version__,
        }

        name, description, version = register_module(**registration_data)

        data = parse_args(args)

        data["module"] = {"name": name, "description": description, "version": version}
        data["sck"] = registration_data

        execute(**data)
    except KeyboardInterrupt:
        print("Aborted by user.")
        sys.exit(1)
    except Exception as e:  # pylint: disable=broad-except
        print(f"Error: {e}")
        sys.exit(1)


def main():
    """
    This is the main entry point for the script within the python
    enviroment.  Used during pip install to create the commend 'core'
    """
    core_module(sys.argv[1:])


if __name__ == "__main__":
    main()
