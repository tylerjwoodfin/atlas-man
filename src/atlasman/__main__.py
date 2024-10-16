"""
Atlas-Man CLI - A Command Line Interface to manage Trello and Jira projects.
"""

import argparse
from typing import Tuple, List
from atlasman.config import edit_config, load_config
from atlasman.trello_commands import TrelloCommands

def add_trello_arguments(parser: argparse.ArgumentParser) -> None:
    """
    Add arguments specific to Trello commands.

    Args:
        parser (argparse.ArgumentParser):
            The argument parser to which Trello arguments will be added.
    """
    parser.add_argument(
        "--trello",
        "--t",
        help="Use Trello commands",
        action="store_true"
    )

    # Trello actions
    trello_actions = parser.add_argument_group('Trello Actions')
    trello_actions.add_argument(
        "--boards",
        action="store_true",
        help="List all Trello boards"
    )
    trello_actions.add_argument(
        "--lists",
        action="store_true",
        help="List all Trello lists"
    )
    trello_actions.add_argument(
        "--cards",
        action="store_true",
        help="List all Trello cards"
    )
    trello_actions.add_argument(
        "--add-board",
        metavar="BOARD_NAME",
        type=str,
        help="Create a new Trello board"
    )
    trello_actions.add_argument(
        "--add-list",
        metavar=("BOARD_NAME", "LIST_NAME"),
        nargs=2,
        help="Create a new Trello list in a specified board"
    )
    trello_actions.add_argument(
        "--add-card",
        metavar=("LIST_NAME", "CARD_NAME"),
        nargs=2,
        help="Create a new Trello card in a specified list"
    )
    trello_actions.add_argument(
        "--delete-board",
        metavar="BOARD_NAME",
        type=str,
        help="Delete a Trello board"
    )
    trello_actions.add_argument(
        "--delete-list",
        metavar=("BOARD_NAME", "LIST_NAME"),
        nargs=2,
        help="Delete a Trello list from a specified board"
    )
    trello_actions.add_argument(
        "--delete-card",
        metavar=("LIST_NAME", "CARD_NAME"),
        nargs=2,
        help="Delete a Trello card from a specified list"
    )


def add_jira_arguments(parser: argparse.ArgumentParser) -> None:
    """
    Add arguments specific to Jira commands.

    Args:
        parser (argparse.ArgumentParser): The argument parser to which Jira arguments will be added.
    """
    parser.add_argument(
        "--jira",
        "--j",
        help="Use Jira commands",
        action="store_true"
    )

    # Jira actions
    jira_actions = parser.add_argument_group('Jira Actions')
    jira_actions.add_argument(
        "--issues",
        action="store_true",
        help="List all Jira issues"
    )
    jira_actions.add_argument(
        "--projects",
        action="store_true",
        help="List all Jira projects"
    )
    jira_actions.add_argument(
        "--add-issue",
        metavar=("PROJECT_KEY", "ISSUE_TITLE"),
        nargs=2,
        help="Add a new Jira issue to a specified project"
    )
    jira_actions.add_argument(
        "--update-issue",
        metavar=("ISSUE_ID", "NEW_TITLE"),
        nargs=2,
        help="Update an existing Jira issue"
    )
    jira_actions.add_argument(
        "--delete-issue",
        metavar="ISSUE_ID",
        type=str,
        help="Delete a Jira issue by issue ID"
    )
    jira_actions.add_argument(
        "--add-project",
        metavar="PROJECT_NAME",
        type=str,
        help="Create a new Jira project"
    )
    jira_actions.add_argument(
        "--delete-project",
        metavar="PROJECT_KEY",
        type=str,
        help="Delete a Jira project by project key"
    )


def parse_arguments() -> argparse.Namespace:
    """
    Add command-line arguments for Atlas-Man.

    Returns:
        argparse.Namespace: Parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(description="A CLI to manage Trello and Jira projects")

    # Add Trello and Jira arguments
    add_trello_arguments(parser)
    add_jira_arguments(parser)

    return parser.parse_args()


def validate_arguments(args: argparse.Namespace,
                       remaining_args: List[str],
                       trello_commands: TrelloCommands) -> Tuple[argparse.Namespace, List[str]]:
    """
    Validate arguments based on Trello or Jira context and return parsed arguments and any unknowns.

    Args:
        args (argparse.Namespace): Parsed arguments from the initial context check.
        remaining_args (List[str]): Remaining arguments to be parsed in context.

    Returns:
        Tuple[argparse.Namespace, List[str]]:
            Parsed context-specific arguments and any unrecognized arguments.
    """
    if args.trello:
        # Parse Trello-specific commands
        trello_parser = argparse.ArgumentParser(description="Trello-specific commands")
        add_trello_arguments(trello_parser)
        trello_args, unknown = trello_parser.parse_known_args(remaining_args)

        if unknown:
            print(f"Error: Unrecognized arguments for Trello: {' '.join(unknown)}")
            trello_parser.print_help()
            return trello_args, unknown

        trello_commands.handle_trello_commands(trello_args)
        return trello_args, []

    elif args.jira:
        # Parse Jira-specific commands
        jira_parser = argparse.ArgumentParser(description="Jira-specific commands")
        add_jira_arguments(jira_parser)
        jira_args, unknown = jira_parser.parse_known_args(remaining_args)

        if unknown:
            print(f"Error: Unrecognized arguments for Jira: {' '.join(unknown)}")
            jira_parser.print_help()
            return jira_args, unknown

        handle_jira_commands(jira_args)
        return jira_args, []

    elif args.config:
        # Edit the configuration file in the default editor
        edit_config()

        return args, remaining_args

    else:
        print("Error: No valid command context provided.")
        return args, remaining_args


def handle_jira_commands(args: argparse.Namespace) -> None:
    """
    Handle Jira-specific commands based on parsed arguments.

    Args:
        args (argparse.Namespace): Parsed command-line arguments.
    """
    print("Jira")
    if args.issues:
        print("Listing all Jira issues...")
    elif args.projects:
        print("Listing all Jira projects...")
    elif args.add_issue:
        print(
            f"Adding a new issue titled '{args.add_issue[1]}' to project '{args.add_issue[0]}'...")
    elif args.update_issue:
        print(f"Updating issue '{args.update_issue[0]}' with new title '{args.update_issue[1]}'...")
    elif args.delete_issue:
        print(f"Deleting issue with ID '{args.delete_issue}'...")
    elif args.add_project:
        print(f"Creating a new Jira project named {args.add_project}...")
    elif args.delete_project:
        print(f"Deleting Jira project with key {args.delete_project}...")


def main() -> None:
    """
    The main function that serves as the entry point for the CLI.
    """
    try:
        # Initial parser to identify the command context
        parser = argparse.ArgumentParser(description="A CLI to manage Trello and Jira projects")
        parser.add_argument("--trello", "--t", help="Use Trello commands", action="store_true")
        parser.add_argument("--jira", "--j", help="Use Jira commands", action="store_true")
        parser.add_argument("--config",
                            help="Edit the configuration file in the default editor",
                            action="store_true")

        # Parse initial command context
        args, remaining_args = parser.parse_known_args()

        # Load configuration and pass necessary values to command handlers
        config = load_config()
        cli_config = config.get("cli", {})

        # Set verbosity if specified in config
        verbose = cli_config.get("verbose", False)
        if verbose:
            print("Running in verbose mode...")

        # Initialize TrelloCommands and JiraCommands
        trello_commands = TrelloCommands(config)

        # Validate arguments based on context and handle commands
        validated_args, unknown_args = validate_arguments(args, remaining_args, trello_commands)

        # If no valid command context provided and no unknown arguments, show the main help
        if not validated_args or unknown_args:
            parser.print_help()

    except KeyboardInterrupt:
        print("\nOperation cancelled by the user.")

if __name__ == "__main__":
    main()
