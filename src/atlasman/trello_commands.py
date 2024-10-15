"""
This module provides functions to interact with the Trello API.
"""

import argparse
from trello import TrelloClient
from config import load_config

def initialize_trello_client() -> TrelloClient:
    """
    Initializes and returns a Trello client using credentials from the config.
    
    Returns:
        TrelloClient: An instance of the TrelloClient configured with API credentials.
    """
    config = load_config()
    trello_config = config.get("trello", {})
    api_key = trello_config.get("api_key")
    api_token = trello_config.get("api_token")

    if not api_key or not api_token:
        raise ValueError("Missing Trello API credentials in the configuration file.")

    return TrelloClient(api_key=api_key, api_secret=api_token)

def list_boards() -> None:
    """
    Lists all Trello boards for the authenticated user.
    """
    client = initialize_trello_client()
    boards = client.list_boards()
    for board in boards:
        print(f"Board Name: {board.name} - Board ID: {board.id}")

def list_lists(board_name: str) -> None:
    """
    Lists all lists in a specified Trello board.

    Args:
        board_name (str): The name of the Trello board.
    """
    client = initialize_trello_client()
    board = next((b for b in client.list_boards() if b.name == board_name), None)

    if not board:
        print(f"No board found with the name '{board_name}'.")
        return

    for list_obj in board.list_lists():
        print(f"List Name: {list_obj.name} - List ID: {list_obj.id}")

def add_card(list_name: str, card_name: str, description: str = "") -> None:
    """
    Adds a new card to a specified list in the default board.

    Args:
        list_name (str): The name of the list to add the card to.
        card_name (str): The name of the card to create.
        description (str): The description for the card.
    """
    client = initialize_trello_client()
    config = load_config()
    default_board_name = config["trello"].get("default_board")

    if not default_board_name:
        print("Error: No default board specified in the configuration file.")
        return

    boards = client.list_boards() or []
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

def handle_trello_commands(args: argparse.Namespace) -> None:
    """
    Handle Trello commands based on the provided arguments.

    Args:
        args (argparse.Namespace): The parsed command-line arguments.
    """
    if args.boards:
        list_boards()
    elif args.lists:
        list_lists(args.lists)
    elif args.add_card:
        add_card(args.add_card[0], args.add_card[1])
    else:
        print("No valid Trello command provided.")