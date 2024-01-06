# TODO List

## ArangoDB Docker Setup

-   docker pull arangodb/arangodb:3.11.6
-   docker run -e ARANGO_ROOT_PASSWORD=openSesame -p 8529:8529 -d arangodb/arangodb:3.11.6

## Things to do before showing

-   [ ] Create simple chat agent
-   [ ] Update docstrings
-   [ ] Add logic to construct dbs from json
-   [x] Finish `StandardUpdater`, only the `update_all` method, class to replace `main.py` for parsing, summarization, and DB insertion as an interface

    -   `update_all` wipes and updates the summaries and databases for the whole project

-   [x] Create AI tools to retrieve from ChromaDB
-   [ ] Add chatbot interface
-   [ ] Create 3-4 more simple agents to show off capabilities

    -   [ ] Starting with general 'agent', question answering

-   [ ] Add logic to reverse create models from ChromaDB
-   [ ] Complete version control updater
-   [ ] Add readme
-   [ ] Add test coverage
-   [ ] Move to new repo
-   [ ] Add issues
-   [ ] Create media to share

## Roadmap

-   [ ] Add tests and improve error handling
-   [ ] Make into pypi package
-   [ ] Update summaries and DB's based on version control
-   [ ] Add logic to track down where an import is defined and update import and dependency models
-   [x] Add logic to log summary count, eg. 'Summarizing k of n files'
-   [ ] Add tests for summarization
-   [ ] Add logic to get BottomUp and TopDown summary mapping to allow for multidirectional summary creation (if desired by user)
-   [ ] Fix parsing error, trying to update an import after it was updated
-   [ ] Add query logic for ArangoDB
-   [ ] Complete CRUD for chromadb
-   [ ] Complete CRUD logic for ArangoDB
-   [ ] Add tests for ArangoDB
-   [ ] Add load project from GitHub logic
-   [ ] Add MethodModel Class that overrides FunctionModel when function is a method
-   [ ] Class Attribute logic
