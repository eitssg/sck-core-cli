"""
Commandline interface to interact with the core module "execute" package.

This can run either in local mode or in lambda mode.  Very helpful
to test your actions and see how they work in AWS lambda!  Or, how they run
locally on your machine.
"""
from .simulate import get_execute_command

__all__ = ["get_execute_command"]
