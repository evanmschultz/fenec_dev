# Postcode

This project is designed to parse a Python codebase and generate summaries for each code block and its dependencies. The goal is to enhance an AI's capability to engage in meaningful conversations with the codebase. The goal is to create a python package that others can use with their own projects.

## Installation

Ensure you have Poetry installed. If not, install it by following the instructions in the [Poetry Documentation](https://python-poetry.org/docs/).

Clone the repository and install the dependencies:

```bash
git clone https://github.com/evanmschultz/postcode.git
cd postcode
poetry install
```

## Usage

To simple chat with the Postcode Project as is, run the following command:

```bash
python main.py
```

-   This will create a simple CLI app to chat with an AI using the ChromaDB database saved in version control.

The project allows for use of a Graph Database and currently requires ArangoDB. To use the database, you must have ArangoDB installed and running. You can install ArangoDB in a docker container by following the instructions in the [ArangoDB Documentation](https://hub.docker.com/_/arangodb/) or by following the commands below:

```bash
docker pull arangodb/arangodb:3.11.6
docker run -e ARANGO_ROOT_PASSWORD=openSesame -p 8529:8529 -d arangodb/arangodb:3.11.6
```

## Configuration

Add configuration logic and update readme.

## Contributing

If you find issues or have suggestions for improvement, feel free to open an issue or submit a pull request. Contributions are greatly welcome!

<!-- ## License

This project is licensed under the [MIT License](LICENSE). -->
