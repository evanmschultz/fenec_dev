# TODO List

## Things to do before showing

-   [ ] Finish `StandardUpdater`, only the `update_all` method, class to replace `main.py` for parsing, summarization, and DB insertion as an interface

    -   `update_all` wipes and updates the summaries and databases for the whole project

-   [ ] Create AI tools to retrieve from ChromaDB
-   [ ] Add chatbot interface
-   [ ] Create 3-4 simple agents to show off capabilities

    -   [ ] Starting with general 'agent', question answering

-   [ ] Add and, or correct docstrings
-   [ ] Add readme
-   [ ] Add test coverage
-   [ ] Move to new repo
-   [ ] Add issues
-   [ ] Create media to share

## Roadmap for future

-   [ ] Add tests and improve error handling
-   [ ] Make into pypi package
-   [ ] Update summaries and DB's based on version control
-   [ ] Add logic to track down where an import is defined and update import and dependency models
-   [x] Remove output json from version control
-   [ ] Add logic to log summary count, eg. 'Summarizing k of n files'
-   [ ] Finish summarization MVP
-   [ ] Add tests for summarization
-   [x] Add chromadb
-   [ ] Add initial chat logic
-   [ ] Add logic to get BottomUp and TopDown summary mapping to allow for multidirectional summary creation
-   [ ] Add ability to create summaries from top down and then back up after initial summary creation (will cost three times more, but will be much better contextually)
-   [ ] Fix parsing error, trying to update an import after it was updated
-   [ ] Add query logic for ArangoDB
-   [ ] Complete CRUD for chromadb
-   [ ] Complete CRUD logic for ArangoDB
-   [ ] Add tests for ArangoDB
-   [ ] Add load project from GitHub logic
-   [ ] Add MethodModel Class that overrides FunctionModel when function is a method
-   [ ] Class Attribute logic
