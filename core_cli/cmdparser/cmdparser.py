import os
import argparse
import gettext

from core_framework.constants import (
    ENV_TASKS,
    ENV_UNITS,
    ENV_AWS_PROFILE,
    ENV_AUTOMATION_TYPE,
    ENV_CLIENT_NAME,
    ENV_CLIENT,
    ENV_SCOPE,
    ENV_PORTFOLIO,
    ENV_APP,
    ENV_BRANCH,
    ENV_BUILD,
    ENV_BUCKET_NAME,
    ENV_BUCKET_REGION,
    ENV_INVOKER_LAMBDA_NAME,
    ENV_INVOKER_LAMBDA_REGION,
)

from .._version import __version__

locale_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "locale")
gettext.bindtextdomain("sck_core", locale_path)
gettext.textdomain("sck_core")
_ = gettext.gettext


def get_epilog():
    """
    Return the footer for the help text
    """
    return f"""\n
Environment Variables:
    {ENV_TASKS} = {os.getenv(ENV_TASKS, '')}
    {ENV_UNITS} = {os.getenv(ENV_UNITS, '')}
    {ENV_AWS_PROFILE} = {os.getenv(ENV_AWS_PROFILE, '')}
    {ENV_AUTOMATION_TYPE} = {os.getenv(ENV_AUTOMATION_TYPE, '')}
    {ENV_CLIENT_NAME} = {os.getenv(ENV_CLIENT_NAME, '')}
    {ENV_CLIENT} = {os.getenv(ENV_CLIENT, '')}
    {ENV_SCOPE} = {os.getenv(ENV_SCOPE, '')}
    {ENV_PORTFOLIO} = {os.getenv(ENV_PORTFOLIO, '')}
    {ENV_APP} = {os.getenv(ENV_APP, '')}
    {ENV_BRANCH} = {os.getenv(ENV_BRANCH, '')}
    {ENV_BUILD} = {os.getenv(ENV_BUILD, '')}
    {ENV_BUCKET_NAME} = {os.getenv(ENV_BUCKET_NAME, '')}
    {ENV_BUCKET_REGION} = {os.getenv(ENV_BUCKET_REGION, '')}
    {ENV_INVOKER_LAMBDA_NAME} = {os.getenv(ENV_INVOKER_LAMBDA_NAME, '')}
    {ENV_INVOKER_LAMBDA_REGION} = {os.getenv(ENV_INVOKER_LAMBDA_REGION, '')}

Copyright (c) 2024 Core Developer. All rights reserved.
 \n
"""


def get_prolog():
    """The prolog comes before the description"""
    return f"Core Autmation Module v{__version__}"


class CoreHelpTextFormatter(argparse.RawTextHelpFormatter):
    """
    Create our own text formatter class so we can make the options column wider
    """

    def __init__(self, *args, **kwargs):
        # Set max_help_position to a larger value to increase the width of the options name column
        self.choices = kwargs.pop("choices", None)
        kwargs["max_help_position"] = 50
        super().__init__(*args, **kwargs)

    def add_arguments(self, actions):
        # Custom logic to make the command name column wider
        actions = sorted(
            actions, key=lambda x: x.dest
        )  # Sort actions to ensure consistent ordering
        if len(actions) == 0:
            max_help_position = 30
        else:
            max_help_position = max(
                len(self._format_action_invocation(action)) for action in actions
            )
        self._action_max_length = max(
            max_help_position, 30
        )  # Set a minimum width of 24 characters
        super().add_arguments(actions)

    def _format_action_invocation(self, action):
        if not action.option_strings:
            return super()._format_action_invocation(action)

        parts = []

        # Get the option strings (e.g., ['-h', '--help'])
        parts.extend(action.option_strings)

        # Join the option strings with commas if there's more than one
        return ", ".join(parts)

    def _format_action(self, action):
        # Check if the action has choices
        if len(action.option_strings) == 0 and self.choices and action.choices:
            keys = list(action.choices)
            # Use a list comprehension to build the formatted choices string
            formatted_choices = "\n".join(
                f"  {key:29} {self._get_description(self.choices.get(key, ('unknown', None)))}"
                for key in keys
            )
            # Combine the action help and formatted choices
            return (
                f"{action.help}\n{formatted_choices}"
                if action.help
                else formatted_choices
            )
        return super()._format_action(action)

    def _get_description(self, choice):
        # Ensure the result is a list and get the first element, otherwise convert to string
        return choice[0] if isinstance(choice, (list, tuple)) else str(choice)


class CoreArgumentParser(argparse.ArgumentParser):
    """
    We create our own object because we want to tweak how the help text is formatted.
    """

    def __init__(self, *args, **kwargs):
        command_title = kwargs.pop("commands_title", "Available Commands")
        options_title = kwargs.pop("options_title", "Available Options")
        epilog = kwargs.get("epilog", "")
        description = kwargs.get("description", "")
        if len(description) > 0:
            description = f"\n{description}"
        self.choices = kwargs.pop("choices", None)
        kwargs["description"] = f"{get_prolog()}{description}"
        kwargs["epilog"] = f"{epilog}{get_epilog()}"

        super().__init__(*args, **kwargs)

        self.set_group_title(0, command_title)
        self.set_group_title(1, options_title)

    def set_group_title(self, index, title):
        """set the title of the group"""
        if title:
            self._action_groups[index].title = title

    def get_action_groups(self) -> list:
        """return all action groups"""
        return self._action_groups

    def get_action_group(self, index) -> list:
        """return a specific action group by number"""
        return self._action_groups[index]

    def format_help(self) -> str:
        """I don't like usage being lowercase"""
        msg1 = super().format_help()
        msg = msg1.replace("usage:", "Usage:")
        return msg

    def add_custom_subparsers(self, **kwargs):
        """make subparsers use this parser class"""
        subparsers = self.add_subparsers(**kwargs)
        subparsers._parser_class = CoreArgumentParser  # pylint: disable=W0212
        return subparsers

    def _get_formatter(self):
        return CoreHelpTextFormatter(prog=self.prog, choices=self.choices)
