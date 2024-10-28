"""
This module provides functions to interact with the Jira API.
"""

import argparse
import traceback
from typing import Any, Dict
from jira import Issue, JIRA, JIRAError

# Decorator to handle common Jira-related exceptions
def handle_jira_exceptions(func):
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


class JiraCommands:
    """
    The JiraCommands class provides functions to interact with the Jira API.
    """

    def __init__(self, config_data: Dict[str, Any]) -> None:
        """
        Initializes the JiraCommands class with the given configuration.

        Args:
            config_data (Dict[str, Any]):
                The configuration dictionary containing Jira API credentials.
        """

        self.config: Dict[str, Any] = config_data
        self.client: JIRA = self.initialize_jira_client()

    def initialize_jira_client(self) -> JIRA:
        """
        Initializes and returns a Jira client using credentials from the config.
        
        Returns:
            JIRA: An instance of the JIRA client configured with API credentials.
        """

        config_jira = self.config.get("jira", {})

        base_url = config_jira.get("base_url")
        username = config_jira.get("username")
        api_token = config_jira.get("api_token")

        # Validate presence of necessary credentials
        if not base_url or not username or not api_token:
            raise ValueError("Missing required Jira credentials ",
                             "(base_url, username, or api_token) in the configuration file.")

        # Initialize JIRA client with API token for basic auth
        return JIRA(server=base_url, basic_auth=(username, api_token))

    @handle_jira_exceptions
    def list_issues(self, project_key: str) -> None:
        """
        Lists all issues for a specified project.

        Args:
            project_key (str): The key of the project to list issues from.
        """

        print(f"Issues for {project_key}:")
        issues = self.client.search_issues(f'project="{project_key}"')

        # Check if the response is a ResultList of Issue objects
        if isinstance(issues, list) or hasattr(issues, 'total'):
            for issue in issues:
                if isinstance(issue, Issue):
                    print(f"Issue Key: {issue.key} - Issue Summary: {issue.fields.summary}")
                else:
                    print(f"Unexpected item type in issues list: {type(issue)}")
        elif isinstance(issues, dict):
            print("Received response as dictionary. Inspecting keys for more details.")
            for key, value in issues.items():
                print(f"{key}: {value}")
        else:
            print("Unexpected issue format received from Jira API.")

    @handle_jira_exceptions
    def list_projects(self) -> None:
        """
        Lists all projects available in Jira.
        """
        projects = self.client.projects()
        for project in projects:
            print(f"Project Name: {project.name} - Project Key: {project.key}")

    @handle_jira_exceptions
    def add_issue(self, project_key: str, issue_title: str) -> None:
        """
        Adds a new issue to the specified project.

        Args:
            project_key (str): The key of the project where the issue will be added.
            issue_title (str): The title of the issue.
        """
        new_issue = self.client.create_issue(project=project_key,
                                             summary=issue_title, issuetype={'name': 'Task'})
        print(f"Issue '{new_issue.key}' created successfully in project '{project_key}'.")

    @handle_jira_exceptions
    def update_issue(self, issue_id: str, new_title: str) -> None:
        """
        Updates the title of an existing issue.

        Args:
            issue_id (str): The ID of the issue to update.
            new_title (str): The new title for the issue.
        """
        issue = self.client.issue(issue_id)
        issue.update(fields={"summary": new_title})
        print(f"Issue '{issue_id}' updated successfully.")

    @handle_jira_exceptions
    def delete_issue(self, issue_id: str) -> None:
        """
        Deletes an issue by its ID.

        Args:
            issue_id (str): The ID of the issue to delete.
        """
        issue = self.client.issue(issue_id)
        issue.delete()
        print(f"Issue '{issue_id}' deleted successfully.")

    @handle_jira_exceptions
    def add_project(self, project_name: str, project_key: str) -> None:
        """
        Creates a new project with the specified name and key.
        
        Args:
            project_name (str): The name of the project to create.
            project_key (str): The key for the project to create.
        """
        try:
            new_project = self.client.create_project(
                key=project_key,
                name=project_name,
            )
            print(f"Project '{project_name}' created successfully with Key: {new_project.key}")
        except JIRAError as e:
            if e.status_code == 403:
                print("Error: You do not have the required admin privileges to create projects.")
            else:
                raise  # Reraise other errors for the decorator to handle

    @handle_jira_exceptions
    def delete_project(self, project_key: str) -> None:
        """
        Deletes a project by its key.

        Args:
            project_key (str): The key of the project to delete.
        """
        try:
            project = self.client.project(project_key)
            project.delete()
            print(f"Project '{project_key}' deleted successfully.")
        except JIRAError as e:
            if e.status_code == 403:
                print("Error: You do not have the required admin privileges to delete projects.")
            elif e.status_code == 404:
                print(f"Error: Project '{project_key}' not found.")
            else:
                raise  # Reraise other errors for the decorator to handle

    def handle_jira_commands(self, args: argparse.Namespace) -> None:
        """
        Handle Jira commands based on the provided arguments.

        Args:
            args (argparse.Namespace): The parsed command-line arguments.
        """

        if args.issues:
            # Use the default project if no specific project key is provided
            if args.issues == "default":
                project_key = self.config["jira"].get("default_project_key")
            else:
                project_key = args.issues
            if project_key:
                self.list_issues(project_key)
            else:
                print("Error: No project key provided, ",
                      "and no default project set in configuration.")
        elif args.projects:
            self.list_projects()
        elif args.add_issue:
            self.add_issue(args.add_issue[0], args.add_issue[1])
        elif args.update_issue:
            self.update_issue(args.update_issue[0], args.update_issue[1])
        elif args.delete_issue:
            self.delete_issue(args.delete_issue)
        elif args.add_project:
            self.add_project(args.add_project[0], args.add_project[1])
        elif args.delete_project:
            self.delete_project(args.delete_project)
