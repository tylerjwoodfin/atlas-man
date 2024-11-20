"""
This module provides functions to interact with 
Confluence using the Jira API.
"""

import os
import argparse
import subprocess
import tempfile
import traceback
from typing import Any, Dict
from jira import JIRAError
import requests

# Decorator to handle common Jira-related exceptions
def handle_confluence_exceptions(func):
    """
    A decorator to handle common Jira-related exceptions.
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except JIRAError as e:
            print(f"JIRA error: {e}")
        except ValueError as e:
            print(f"Value error: {e}")
        except Exception as e:  # pylint: disable=broad-except
            print(f"Unexpected error in {func.__qualname__}: {e}")
            traceback.print_exc()
    return wrapper

class ConfluenceCommands:
    """
    Handles Confluence-specific commands.
    """

    def __init__(self, config_data: Dict[str, Any]) -> None:
        """
        Initializes the ConfluenceCommands class with the given configuration.

        Args:
            config_data (Dict[str, Any]):
                The configuration dictionary containing Confluence API credentials.
        """

        self.config: Dict[str, Any] = config_data
        self.username: str = config_data["jira"]["username"]
        self.api_token: str = config_data["jira"]["api_token"]
        self.base_url: str = config_data["jira"]["base_url"].rstrip("/")
        self.default_space_key: str = config_data["confluence"]["default_space_key"]

    @handle_confluence_exceptions
    def request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Makes a request to the Confluence REST API.

        Args:
            method (str): The HTTP method to use (GET, POST, PUT, DELETE).
            endpoint (str): The API endpoint relative to the base URL.

        Returns:
            Dict[str, Any]: The JSON response from the API.
        """
        url = f"{self.base_url}/wiki/rest/api/{endpoint}"
        auth = (self.username, self.api_token)
        headers = {"Content-Type": "application/json"}

        response = requests.request(method,
                                    url,
                                    auth=auth,
                                    headers=headers,
                                    **kwargs,
                                    timeout=30)
        response.raise_for_status()
        return response.json()

    @handle_confluence_exceptions
    def list_pages(self, space_key: str | None = None) -> None:
        """
        Lists all pages in a specified space.

        Args:
            space_key (str): The key of the Confluence space.
        """

        if not space_key:
            space_key = self.default_space_key

        pages = self.request("GET", f"content?spaceKey={space_key}&type=page")
        for page in pages.get("results", []):
            print(f"Page Title: {page['title']} - Page ID: {page['id']}")

    @handle_confluence_exceptions
    def get_page(self, page_id: str) -> Dict[str, Any]:
        """
        Retrieves a Confluence page by its ID.

        Args:
            page_id (str): The ID of the page to retrieve.

        Returns:
            Dict[str, Any]: The page content and metadata.
        """
        return self.request("GET", f"content/{page_id}?expand=body.storage,version")

    @handle_confluence_exceptions
    def edit_page(self, page_id: str) -> None:
        """
        Opens a Confluence page in Vim for editing.

        Args:
            page_id (str): The ID of the page to edit.
        """
        page_data = self.get_page(page_id)
        page_title = page_data["title"]
        page_body = page_data["body"]["storage"]["value"]
        version_number = page_data["version"]["number"]

        # Create a temporary file to edit the page content
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as tmpfile:
            tmpfile.write(page_body.encode("utf-8"))
            tmpfile_path = tmpfile.name

        # Open Vim to edit the content
        subprocess.run(["vim", tmpfile_path], check=True)

        # Read the updated content
        with open(tmpfile_path, "r", encoding="utf-8") as tmpfile:
            updated_body = tmpfile.read()

        os.remove(tmpfile_path)

        # Update the page in Confluence
        payload = {
            "version": {"number": version_number + 1},
            "title": page_title,
            "type": "page",
            "body": {
                "storage": {
                    "value": updated_body,
                    "representation": "storage"
                }
            }
        }

        self.request("PUT", f"content/{page_id}", json=payload)
        print(f"Page '{page_title}' updated successfully.")

    @handle_confluence_exceptions
    def create_page(self, space_key: str, title: str, content: str) -> None:
        """
        Creates a new page in a specified space.

        Args:
            space_key (str): The key of the space to create the page in.
            title (str): The title of the page.
            content (str): The content of the page in Confluence storage format (XHTML).
        """

        if not space_key:
            space_key = self.default_space_key

        payload = {
            "title": title,
            "type": "page",
            "space": {"key": space_key},
            "body": {
                "storage": {
                    "value": content,
                    "representation": "storage"
                }
            }
        }

        page = self.request("POST", "content", json=payload)
        print(f"Page '{title}' created successfully with ID: {page['id']}")

    @handle_confluence_exceptions
    def delete_page(self, page_id: str) -> None:
        """
        Deletes a Confluence page by its ID.

        Args:
            page_id (str): The ID of the page to delete.
        """
        self.request("DELETE", f"content/{page_id}")
        print(f"Page with ID '{page_id}' deleted successfully.")

    @handle_confluence_exceptions
    def handle_confluence_commands(self, args: argparse.Namespace) -> None:
        """
        Handle Confluence commands based on the provided arguments.

        Args:
            args (argparse.Namespace): The parsed command-line arguments.
        """

        if args.pages:
            # Use the default space key if none is provided
            default_space_key = args.pages
            if args.pages == "default":
                default_space_key = self.config["confluence"].get("default_space_key")
            self.list_pages(default_space_key)
        elif args.page:
            if args.page:
                self.get_page(args.page)
            else:
                print("Error: Missing argument for retrieving a page. Requires a page ID.")
        elif args.edit_page:
            if args.edit_page:
                self.edit_page(args.edit_page)
            else:
                print("Error: Missing argument for editing a page. Requires a page ID.")
        elif args.add_page:
            if len(args.add_page) >= 3:
                space_key = args.add_page[0]
                title = args.add_page[1]
                content = args.add_page[2]
                self.create_page(space_key, title, content)
            else:
                print("Error: Missing arguments for creating a page. ",
                      "Requires space key, title, and content.")
        elif args.delete_page:
            if args.delete_page:
                self.delete_page(args.delete_page)
            else:
                print("Error: Missing argument for deleting a page. Requires a page ID.")
