# 🗨️ AI Services Chat

The chat functionality in Fenec allows users to interact with their codebase using natural language queries. This feature leverages the power of Large Language Models (LLMs) to provide intelligent responses based on the analyzed and summarized code structure.

## 🌟 Features

-   💬 Natural language interaction with your codebase
-   🧠 Context-aware responses using processed code summaries
-   🔀 Support for multiple AI providers (currently OpenAI, with Ollama support planned)
-   ⚙️ Customizable chat configurations

> **⚠️ Note:** The chat functionality is under active development and may not perform optimally at this time. We are working to enhance its capabilities and usability, so your feedback and contributions are highly appreciated!

## 🚀 Usage

To use the chat functionality, you first need to process your codebase using Fenec. Once processed, you can start a chat session either through the CLI or the Python API.

### CLI Usage

```bash
fenec --chat # if processed codebase is in the default location
```

This command starts a chat session about your processed codebase.

### API Usage

```python
from fenec import Fenec
from fenec.configs import OpenAIChatConfigs

# Initialize Fenec
fenec = Fenec(path="/path/to/your/codebase")

# Connect to the existing vectorstore
fenec.connect_to_vectorstore(chromadb_name="my_project")

# Start chatting
response = fenec.chat("What does the main function in app.py do?")
print(response)

# Continue the conversation
response = fenec.chat("How are errors handled in that function?")
print(response)
```

## ⚙️ Configuration

The chat functionality can be customized using configuration classes. Currently, there are two main configuration classes for the chat functionality:

1. `OpenAIChatConfigs`: For configuring OpenAI-based chat completions.
2. `OllamaChatConfigs`: For configuring Ollama-based chat completions (planned for future implementation).

### OpenAIChatConfigs

```python
from fenec.configs import OpenAIChatConfigs

chat_configs = OpenAIChatConfigs(
    system_message="You are an AI assistant specialized in Python codebases.",
    model="gpt-4o",  # defaults to "gpt-4o-2024-08-06"
    temperature=0.7
)

fenec = Fenec(
    path="/path/to/your/codebase",
    chat_configs=chat_configs
)
```

### OllamaChatConfigs (Planned)

```python
from fenec.configs import OllamaChatConfigs

chat_configs = OllamaChatConfigs(
    model="codellama:7b",
    system_message="You are an AI assistant specialized in Python codebases."
)

fenec = Fenec(
    path="/path/to/your/codebase",
    chat_configs=chat_configs
)
```

## 🚧 Under Development

Please note that the chat functionality, like the rest of Fenec, is under active development and subject to change. We encourage users to provide feedback and suggestions for improvement.

If you have ideas on better ways to implement or enhance the chat functionality, please don't hesitate to [open an issue](https://github.com/evanmschultz/fenec/issues) or submit a [pull request](https://github.com/evanmschultz/fenec/pulls). For more information on how to contribute, please refer to our [Contributing Guidelines](../../CONTRIBUTING.md).

## 🗺️ Roadmap

Our plans for enhancing the chat functionality include:

-   Tests, tests, and more tests! - Due to a rush to get Fenec out the door, we have a lot of untested code.
-   Implementing Ollama support for local LLM usage
-   Improving context and history management for more coherent multi-turn conversations
-   Enhancing the retrieval mechanism for more accurate and relevant responses
-   Agentic chat capabilities for codebase modification and refactoring (This may be beyond the scope of the Fenec library. Should it be handled by the users and other libraries, eg. [Langchain](https://www.langchain.com), thoughts?)
-   Implementing features for code generation and modification based on chat interactions

For a more detailed look at our future plans, please check out our [Roadmap](../../ROADMAP.md).

We're excited to see how the community uses and helps improve Fenec's chat capabilities!
