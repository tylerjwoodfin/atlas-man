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

    def list_lists(self, board_name_or_alias: str) -> None:
        """
        Lists all non-archived lists in a specified Trello board.
        Can use board name or alias from the configuration.

        Args:
            board_name_or_alias (str): The name of the Trello board or an alias.
        """
        # Check if alias exists in config
        alias_info = self.config["trello"].get("alias_ids", {}).get(board_name_or_alias)

        if alias_info:
            board_id = alias_info.get("board_id")
            if not board_id:
                print(f"Error: Alias '{board_name_or_alias}' does not contain a board ID.")
                return
            board = self.client.get_board(board_id)
        else:
            # Fallback to treating it as a board name
            board = next(
                (b for b in self.client.list_boards() if b.name == board_name_or_alias),
                None
            )

        if not board:
            print(f"No board found with the name or alias '{board_name_or_alias}'.")
            return

        # Filter out archived lists (closed == True)
        for list_obj in board.list_lists():
            if not list_obj.closed:
                print(f"List Name: {list_obj.name} - List ID: {list_obj.id}")

    def list_cards(self, list_name_or_alias: str) -> None:
        """
        Lists all cards in a specified list.
        Can use list name or alias from the configuration.

        Args:
            list_name_or_alias (str): The ID of the list or an alias from the configuration.
        """
        # Check if alias exists in config
        alias_info = self.config["trello"].get("alias_ids", {}).get(list_name_or_alias)

        if alias_info:
            list_id = alias_info.get("list_id")
            if not list_id:
                print(f"Error: Alias '{list_name_or_alias}' does not contain a list ID.")
                return
            list_obj = self.client.get_list(list_id)
        else:
            # Fallback to treating it as a list ID
            try:
                list_obj = self.client.get_list(list_name_or_alias)
            except TokenError as e:
                print(f"Error fetching list with ID '{list_name_or_alias}': {e}")
                return

        if not list_obj:
            print(f"No list found with the ID or alias '{list_name_or_alias}'.")
            return

        cards = list_obj.list_cards()
        for card in cards:
            print(f"Card Name: {card.name} - Card ID: {card.id}")

    def add_card(self, list_name_or_alias: str, card_name: str, description: str = "") -> None:
        """
        Adds a new card to a specified list.
        Can use list name or alias from the configuration.

        Args:
            list_name_or_alias (str): The name of the list or an alias.
            card_name (str): The name of the card to create.
            description (str): The description for the card.
        """
        # Check if alias exists in config
        alias_info = self.config["trello"].get("alias_ids", {}).get(list_name_or_alias)

        if alias_info:
            list_id = alias_info.get("list_id")
            if not list_id:
                print(f"Error: Alias '{list_name_or_alias}' does not contain a list ID.")
                return
            list_obj = self.client.get_list(list_id)
        else:
            # Fallback to treating it as a list name or ID
            try:
                list_obj = self.client.get_list(list_name_or_alias)
            except TokenError as e:
                print(f"Token error fetching list with ID or name '{list_name_or_alias}': {e}")
            except ValueError as e:
                print(f"Value error fetching list with ID or name '{list_name_or_alias}': {e}")
            except Exception as e: # pylint: disable=broad-except
                print(f"Unexpected error fetching list with ID or name '{list_name_or_alias}': {e}")
                return

        if not list_obj:
            print(f"No list found with the ID or alias '{list_name_or_alias}'.")
            return

        # Add the card to the specified list
        try:
            list_obj.add_card(card_name, desc=description)
            print(f"Card '{card_name}' added to list '{list_obj.name}'.")
        except TokenError as e:
            print(f"Token error adding card '{card_name}' to list: {e}")
        except ValueError as e:
            print(f"Value error adding card '{card_name}' to list: {e}")
        except Exception as e: # pylint: disable=broad-except
            print(f"Unexpected error adding card '{card_name}' to list: {e}")

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
        elif args.cards:
            self.list_cards(args.cards)
        elif args.add_card:
            self.add_card(args.add_card[0], args.add_card[1])
        elif args.delete_card:
            print("Unimplemented: Delete card")
        elif args.delete_list:
            print("Unimplemented: Delete list")
        elif args.delete_board:
            print("Unimplemented: Delete board")
