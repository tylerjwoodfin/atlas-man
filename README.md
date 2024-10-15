# atlas-man
A CLI to manage Trello and Jira projects.

## Overview
`atlas-man` is a command-line interface (CLI) tool for managing tasks and projects in Trello and Jira. It allows you to interact with both platforms directly from your terminal, enabling streamlined project management without needing to open a web browser.

## Features
- List, add, and delete boards, lists, and cards on Trello.
- List, add, update, and delete issues and projects on Jira.
- Separate commands for Trello and Jira, so you can work with only the commands you need.
- Context-aware argument validation, ensuring commands are accurately targeted to Trello or Jira.

## Installation
Clone the repository and navigate to the project directory:
```bash
git clone https://github.com/tylerjwoodfin/atlas-man.git
cd atlas-man
```

### Setting up the Environment
It’s recommended to use a virtual environment:
```bash
python3 -m venv env
source env/bin/activate
```

### Installing Dependencies
`atlas-man` requires some Python dependencies. Install them with:
```bash
pip install -r requirements.md
```

## Usage
Run the CLI by executing the `main` script with the appropriate commands for Trello or Jira. You can access detailed help with the `--help` flag.

```bash
python atlas-man.py --help
```

### Trello Commands
#### Listing Commands
- **List all Trello boards**:
  ```bash
  python atlas-man.py --trello --boards
  ```
- **List all Trello lists**:
  ```bash
  python atlas-man.py --trello --lists
  ```
- **List all Trello cards**:
  ```bash
  python atlas-man.py --trello --cards
  ```

#### Add Commands
- **Add a new Trello board**:
  ```bash
  python atlas-man.py --trello --add-board "Board Name"
  ```
- **Add a new Trello list to an existing board**:
  ```bash
  python atlas-man.py --trello --add-list "Board Name" "List Name"
  ```
- **Add a new Trello card to an existing list**:
  ```bash
  python atlas-man.py --trello --add-card "List Name" "Card Name"
  ```

#### Delete Commands
- **Delete a Trello board**:
  ```bash
  python atlas-man.py --trello --delete-board "Board Name"
  ```
- **Delete a Trello list from a board**:
  ```bash
  python atlas-man.py --trello --delete-list "Board Name" "List Name"
  ```
- **Delete a Trello card from a list**:
  ```bash
  python atlas-man.py --trello --delete-card "List Name" "Card Name"
  ```

### Jira Commands
#### Listing Commands
- **List all Jira issues**:
  ```bash
  python atlas-man.py --jira --issues
  ```
- **List all Jira projects**:
  ```bash
  python atlas-man.py --jira --projects
  ```

#### Add Commands
- **Add a new Jira issue to a project**:
  ```bash
  python atlas-man.py --jira --add-issue "Project Key" "Issue Title"
  ```
- **Add a new Jira project**:
  ```bash
  python atlas-man.py --jira --add-project "Project Name"
  ```

#### Update Commands
- **Update an existing Jira issue's title**:
  ```bash
  python atlas-man.py --jira --update-issue "Issue ID" "New Title"
  ```

#### Delete Commands
- **Delete a Jira issue**:
  ```bash
  python atlas-man.py --jira --delete-issue "Issue ID"
  ```
- **Delete a Jira project**:
  ```bash
  python atlas-man.py --jira --delete-project "Project Key"
  ```

## Example Usages
Here are a few example commands you can try:

```bash
# List all Trello boards
python atlas-man.py --trello --boards

# Add a new list to the "Development" board
python atlas-man.py --trello --add-list "Development" "Backlog"

# List all issues in Jira
python atlas-man.py --jira --issues

# Add a new issue to the "WEB" project in Jira
python atlas-man.py --jira --add-issue "WEB" "Fix homepage bug"
```

## Contributing
We welcome contributions! Please fork the repository, make your changes, and submit a pull request. Before contributing, review the following guidelines:
1. Ensure code is clear, concise, and well-documented.
2. Include comments for any complex logic.
3. Test thoroughly before submitting your pull request.

## License
This project is licensed under the MIT License. See the `LICENSE` file for more details.

## Contact
For any inquiries or issues, please open an issue on [GitHub](https://github.com/tylerjwoodfin/atlas-man/issues).

Happy tasking!
```