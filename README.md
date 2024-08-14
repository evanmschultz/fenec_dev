# Fenec 🦊

The anti-devin, no fancy reveal, this sucks, and will suck for awhile. It however could be something. Who knows!?

Fenec is an experimental Python library aimed at enhancing code comprehension and interaction through the use of Large Language Models (LLMs). It's like having a tiny, overeducated, incompetent, know-it-all fox rummaging through your codebase, occasionally giving you insights, either through its greater understanding or lack there of, or because it broke and you learned that you need to deal with your tech debt!

Fenec is an experimental Python library aimed at enhancing code comprehension and interaction through the use of Large Language Models (LLMs). Currently in early development, Fenec explores innovative approaches to parsing, summarizing, and querying Python projects.

> **⚠️ Note:** Fenec is in its early stages and is not yet ready for production use. Features and capabilities are actively evolving. Contributions and feedback to help shape the project's direction and functionality are more than welcome.

🎯 Project Vision
Fenec aspires to:

Parse Python codebases into structured, analyzable formats (because

## 🎯 Project Vision

Fenec aspires to:

-   Parse Python codebases into structured, analyzable formats
-   Generate concise, context-aware summaries of code elements
-   Facilitate natural language interactions with codebases
-   Integrate with AI services to provide intelligent code insights

## 🌟 Current Features

-   📊 Python project parsing and Concrete Syntax Tree (CST) construction:
    -   Constructs a hierarchical representation of the codebase
    -   Builds a graph database to enable network-style navigation of code elements
    -   Lays the foundation for interactive visualization of project structure and dependencies
    -   Supports context-rich summarization by leveraging code relationships
-   🧠 Code summarization using LLMs (OpenAI or Ollama):
    -   Generates summaries that incorporate contextual information from related code blocks
    -   Provides a more holistic understanding of each code element's role in the project
-   🕸️ Preliminary integration with ArangoDB for storing code structure and relationships
-   🔍 Initial implementation of vector storage (ChromaDB) for efficient retrieval of code summaries
-   🖥️ Command-line interface for basic interactions and codebase exploration
-   🐍 Initial simple Python API for programmatic use and integration into development workflows
    -   Greater integration with existing and future project functionalities are planned to allow for more control and customization

Contributions from people that are interested in exploring new methods of using AI in development. Please see the [Contributing Guidelines](CONTRIBUTING.md) for more details.

##

[Features](#-features) | [Installation](#️️-installation) | [CLI - Quick Start](#️️-cli---quick-start) | [API - Quick Start](#️️-api---quick-start) | [Contributing](#-contributing) | [License](#-license) | [Acknowledgments](#-acknowledgments) | [Example Output](#example-output)

## 🌟 Features

-   📊 Parse entire Python projects
-   🧠 Summarize code blocks using LLMs (OpenAI or Ollama)
-   🕸️ Store code structure in a graph database (ArangoDB)
-   🔍 Store summaries in a vector database (ChromaDB) for efficient retrieval
-   🖥️ CLI interface for easy interaction
-   🐍 Python API for integration into your projects

## 🛠️ Installation

### Prerequisites

-   Python 3.11+
-   [Poetry](https://python-poetry.org/docs/#installation)
-   [Docker](https://www.docker.com/) (for ArangoDB)
-   [Ollama](https://github.com/jmorganca/ollama) (optional, for local LLM usage)

### Steps

1. Clone the repository:

    ```bash
    git clone https://github.com/yourusername/fenec.git
    cd fenec
    ```

2. Install dependencies:

    ```bash
    poetry install
    ```

3. Set up ArangoDB using Docker:

    ```bash
    docker pull arangodb/arangodb:3.11.6
    docker run -e ARANGO_ROOT_PASSWORD=openSesame -p 8529:8529 -d arangodb/arangodb:3.11.6
    ```

4. Set up OpenAI API key (if using OpenAI):

    - Create an account on [OpenAI](https://platform.openai.com/signup)
    - Create an API key and set it as an environment variable in your terminal:
        ```bash
        export OPENAI_API_KEY="your-api-key"
        ```

5. Install Ollama (if using Ollama for a local LLM):
    - On macOS (using Homebrew):
        ```bash
        brew install ollama
        ```
    - For other platforms, follow the [official Ollama installation guide](https://github.com/jmorganca/ollama#installation).

## 🚀 CLI - Quick Start

After installing Fenec using Poetry, you can immediately start chatting with the Fenec project itself in the CLI:

```bash
fenec
```

This will connect to the existing vectorstore and start a chat session about the Fenec project.

To process and interact with your own codebase:

1. Process your codebase:

    ```bash
    fenec /path/to/your/codebase --update-all --passes 3
    ```

    This command processes the entire codebase at the specified path, using 3 passes for summarization (bottom-up, top-down, then bottom-up again).

2. Update changed files:

    ```bash
    fenec /path/to/your/codebase --update --passes 1
    ```

    This updates the summaries and databases with code that has changed since the last git commit, using a single bottom-up pass.

3. Start a chat session:

    ```bash
    fenec /path/to/your/codebase --chat
    ```

    This connects to the existing vectorstore and starts a chat session about your processed codebase.

4. Process and chat in one command:
    ```bash
    fenec /path/to/your/codebase --update-all --passes 3 --chat
    ```
    This processes the entire codebase and then starts a chat session.

CLI Options:

-   `--update`: Update summaries for changed files since last commit
-   `--update-all`: Process and update the entire codebase
-   `--chat`: Start a chat session after processing (default: True)
-   `--passes`: Number of summarization passes (1 or 3, default: 1)

    > **NOTE:** The `--passes` arg sets the number of passes the summarizer will take (1 or 3). The summarizer will first summarize the code blocks that are at the lowest level (the ones that have no children, eg. a method of a function often doesn't have any child code blocks), or doesn't have any code blocks defined in the project that it depends on. Then, it will summarize the code blocks that depend on the previously summarized code blocks, and so on.
    >
    > if the `--passes` arg is set to 3, the second pass will run from the top level of the project, eg. the entry points and directories, and summarize the code blocks that depend on the code blocks that were summarized in the first pass, using the existing summaries and the summaries of the parent code blocks to make the summaries of each code block include further information and how the code block fits into the project, eg. its purpose. The third run like the first pass but with greater context.

    > **NOTE:** The first time you run Fenec, it will take some time to process the codebase and build the databases. Subsequent runs should be faster and cheaper as it will use version control to only process the changed files and the summaries for the code blocks that depend on them.

## 🚀 API - Quick Start

You can also use Fenec programmatically in your Python projects. Here's how to get started:

1. Import and initialize Fenec:

```python
from pathlib import Path
from fenec import Fenec
from fenec.configs import OpenAISummarizationConfigs, OpenAIChatConfigs

# Initialize Fenec with default configurations
fenec = Fenec(path=Path("/path/to/your/codebase"))

# Or, customize configurations, note their are configs for ollama as well
summarization_configs = OpenAISummarizationConfigs(
    system_message="Summarize the following code concisely.",
    model="gpt-4o", # defaults to "gpt-4o-2024-08-06"
    temperature=0.2
)
chat_configs = OpenAIChatConfigs(
    system_message="You are an AI assistant specialized in Python codebases.",
    model="gpt-4o", # defaults to "gpt-4o-2024-08-06"
    temperature=0.7
)
fenec = Fenec(
    path=Path("/path/to/your/codebase"),
    summarization_configs=summarization_configs,
    chat_configs=chat_configs
)
```

2. Process the codebase:

```python
# Process the entire codebase
fenec.process_codebase(num_of_passes=3, process_all=True)

# Or, update only changed files
fenec.process_codebase(num_of_passes=1, process_all=False)
```

3. Connect to an existing vectorstore (if you've already processed the codebase):

```python
fenec.connect_to_vectorstore(chromadb_name="my_project")
```

4. Chat with the AI about your codebase:

```python
response = fenec.chat("What does the main function in app.py do?")
print(response)

# You can ask multiple questions in a row
response = fenec.chat("How are errors handled in the database module?")
print(response)
```

This API allows you to integrate Fenec's capabilities into your own Python scripts or applications, giving you programmatic control over codebase processing and AI interactions.

> **NOTE:** Fenec is built to be extensible and thus access to the chromadb, vectorstore, and chroma_librarian could be relatively easily added to the API. If you wish for this please open an issue or a pull request.

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for more details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

-   [OpenAI](https://openai.com/) for their powerful language models
-   [Ollama](https://github.com/jmorganca/ollama) for providing local LLM capabilities
-   [LibCST](https://libcst.readthedocs.io/en/latest/) for providing the library for Python code parsing
-   [ArangoDB](https://www.arangodb.com/) for the graph database
-   [ChromaDB](https://www.trychroma.com/) for the vector database

## Example Output:

The following is the output Fenec gave with the prompt: "Update this README intro to be more comprehensive and detailed: Fenec is a Python library for parsing, summarizing, and interacting with entire Python projects using Large Language Models (LLMs)."

> **NOTE:** This project is in early development and is NOT near ready for production. So, please ignore the grandiose claims in the AI's response below.

    Fenec is a comprehensive and robust Python library designed to revolutionize the way developers parse, summarize, and interact with entire Python projects. By leveraging the capabilities of Large Language Models (LLMs), Fenec provides an advanced framework that facilitates deep analysis and understanding of complex codebases. This library is not just a tool for parsing code; it is an integrated system that transforms raw code into structured, semantically rich models, enabling sophisticated interactions and insights.

    At its core, Fenec utilizes the LibCST library to parse Python code into concrete syntax trees, ensuring high fidelity and syntactic accuracy. This parsing capability is complemented by a suite of tools that convert code elements, such as import statements and class definitions, into structured data models. These models are essential for static analysis, refactoring, and documentation generation, providing a detailed representation of the code's structure and semantics.

    Fenec's summarization features are powered by LLMs, which generate detailed and contextually aware summaries of code snippets. This functionality is crucial for enhancing code retrieval and understanding, particularly in large and complex projects. By producing semantically rich summaries, Fenec enables developers to quickly grasp the functionality and purpose of code segments, facilitating efficient navigation and comprehension of the codebase.

    The library also offers a unique interaction model through a chat interface, allowing users to query the codebase using natural language. This feature bridges the gap between raw code data and user interaction, making it possible to explore and understand code functionalities dynamically. By integrating with AI services, Fenec provides a conversational interface that enhances accessibility and user engagement, transforming the way developers interact with their code.

    In the context of a larger system, Fenec serves as a foundational component for tools that require a structured and interactive representation of Python code. It supports a wide range of applications, from improving code quality and maintainability to facilitating complex refactoring tasks. By providing a reliable and extensible framework, Fenec empowers developers to perform complex analyses and transformations efficiently, making it an indispensable tool for modern software development environments.
