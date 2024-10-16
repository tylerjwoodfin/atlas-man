"""
This module provides functions to interact with the Trello API.
"""

import os
import argparse
from typing import Any, Dict
from trello import TrelloClient
from trello import TokenError

class TrelloCommands:
    """
    The TrelloCommands class provides functions to interact with the Trello API.
    """

    def __init__(self, config_data: Dict[str, Any]) -> None:
        """
        Initializes the TrelloCommands class with the given configuration.

        Args:
            config_data (Dict[str, Any]):
                The configuration dictionary containing Trello API credentials.
        """

        self.config: Dict[str, Any] = config_data
        self.client: TrelloClient = self.initialize_trello_client()

    def initialize_trello_client(self) -> TrelloClient:
        """
        Initializes and returns a Trello client using credentials from the config.
        
        Returns:
            TrelloClient: An instance of the TrelloClient configured with API credentials.
        """

        config_trello = self.config.get("trello", {})

        api_key = config_trello.get("api_key")
        api_secret = config_trello.get("api_secret")
        oauth_token = config_trello.get("oauth_token")
        oauth_token_secret = config_trello.get("oauth_token_secret")

        # Validate presence of necessary credentials
        if not api_key:
            raise ValueError("Missing Trello API key in the configuration file.")

        # Set environment variables for the Trello client to use
        os.environ["TRELLO_API_KEY"] = api_key
        os.environ["TRELLO_API_SECRET"] = api_secret

        # Initialize Trello client with available credentials
        return TrelloClient(api_key=api_key,
                            api_secret=api_secret,
                            token=oauth_token,
                            token_secret=oauth_token_secret)

    def list_boards(self) -> None:
        """
        Lists all Trello boards for the authenticated user.
        """

        try:
            boards = self.client.list_boards()
            for board in boards:
                print(f"Board Name: {board.name} - Board ID: {board.id}")
        except TokenError as e:
            print(f"Error listing boards: {e}")

    def list_lists(self, board_name: str) -> None:
        """
        Lists all lists in a specified Trello board.

        Args:
            board_name (str): The name of the Trello board.
        """

        board = next((b for b in self.client.list_boards() if b.name == board_name), None)

        if not board:
            print(f"No board found with the name '{board_name}'.")
            return

        for list_obj in board.list_lists():
            print(f"List Name: {list_obj.name} - List ID: {list_obj.id}")

    def add_card(self, list_name: str, card_name: str, description: str = "") -> None:
        """
        Adds a new card to a specified list in the default board.

        Args:
            list_name (str): The name of the list to add the card to.
            card_name (str): The name of the card to create.
            description (str): The description for the card.
        """

        default_board_name = self.config["trello"].get("default_board")

        if not default_board_name:
            print("Error: No default board specified in the configuration file.")
            return

        boards = self.client.list_boards() or []
        board = next((b for b in boards if b.name == default_board_name), None)
        if not board:
            print(f"No board found with the name '{default_board_name}'.")
            return

        trello_list = next((l for l in board.list_lists() if l.name == list_name), None)
        if not trello_list:
            print(f"No list found with the name '{list_name}' in board '{default_board_name}'.")
            return

        trello_list.add_card(card_name, desc=description)
        print(f"Card '{card_name}' added to list '{list_name}' in board '{default_board_name}'.")

    def handle_trello_commands(self, args: argparse.Namespace) -> None:
        """
        Handle Trello commands based on the provided arguments.

        Args:
            args (argparse.Namespace): The parsed command-line arguments.
        """

        if args.boards:
            self.list_boards()
        elif args.lists:
            self.list_lists(args.lists)
        elif args.add_card:
            self.add_card(args.add_card[0], args.add_card[1])
        else:
            print("No valid Trello command provided.")
