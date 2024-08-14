# 🧠 AI Services Summarizer

The summarizer functionality in Fenec is a tool designed to generate contextual and informative summaries of Python code. It leverages Large Language Models (LLMs) to analyze code structure, purpose, context, etc., providing developers and the chat LLM with in-depth insights into code snippets or entire modules.

## 🌟 Features

-   📊 Single or Multi-pass summarization for comprehensive code analysis
-   🔀 Support for multiple AI providers (OpenAI and Ollama)
-   🧩 Context-aware summaries incorporating information from dependencies, children, parents and 'connected' code blocks
-   ⚙️ Customizable configurations for fine-tuning summarization behavior
-   🔍 Integration with graph database for relationship-aware summarizations
-   🎨 Support for custom prompts to tailor summarization output

> **⚠️ Note:** The summarizer functionality is under active development and may undergo significant changes. We are working to enhance its capabilities and usability, so your feedback and contributions are highly appreciated!

## 🚀 Components

> **NOTE:** This is automatically handled by the Fenec API, so you don't need to interact with the Summarizer logic directly unless you want more granular control or to perform custom operations for testing, learning about how Fenec works, or extending Fenec's functionality.

### GraphDBSummarizationManager

The `GraphDBSummarizationManager` class orchestrates the summarization process, managing the interaction between the code models, graph database, and summarization logic.

Key methods:

-   `create_summaries_and_return_updated_models`: Performs single or multi-pass summarization on the codebase.

### SummarizationMapper

The `SummarizationMapper` class generates summarization maps for both bottom-up and top-down approaches, facilitating single or multi-pass summarization.

Key methods:

-   `create_bottom_up_summarization_map`: Creates a map for bottom-up summarization.
-   `create_top_down_summarization_map`: Creates a map for top-down summarization.

#### How the Mapper Works

The SummarizationMapper is crucial for generating the code block summaries. Multi-pass summarization works as follows:

1. **Initialization**: The mapper is initialized with module IDs to update, all available models, and an ArangoDB manager for database interactions.

    - The `--passes` argument in the CLI determines the number of summarization passes (1 or 3). The `Fenec` api class has the same parameter.

2. **Bottom-up Mapping (first pass)**:

    > **NOTE:** This is the only summarization pass that is executed in a single-pass summarization.

    - Starts from the lowest-level code elements (e.g., functions, methods, or standalone code blocks that have no children and don't depend on other code blocks defined in the project).
    - Traverses upwards through the code hierarchy, mapping dependencies and relationships.
    - This pass provides detailed summaries of individual components, including the context of the summaries of their children or code blocks they depend on.

3. **Top-down Mapping (second pass)**:

    - Begins with high-level elements (e.g., project entry points, directories, or modules).
    - Moves downwards through the hierarchy, providing context from parent elements to children, including the previous summary for the code block that was produced in the first pass.
    - This pass enhances summaries with broader context and purpose within the overall structure.

4. **Bottom-up Mapping (third pass)**:
    - Repeats first pass but with the updated summaries from the second pass as context to provide more comprehensive and project aware summaries.

The multi-pass approach ensures that each code element is summarized with a comprehensive understanding of its role within the entire codebase.

### SummarizationPromptCreator

The `SummarizationPromptCreator` class is responsible for creating prompts for the AI models, tailoring them based on the summarization context and pass number.

Key method:

-   `create_prompt`: Generates a prompt for code summarization based on various inputs.

#### Creating Custom Prompts

Fenec allows for customization of summarization prompts to tailor the output to specific needs:

1. **Modifying Existing Prompts**:

    - Locate the `summarization_prompts.py` file in the `prompts` directory.
    - Modify the `CODE_SUMMARY_PROMPT_PASS_1`, `CODE_SUMMARY_PROMPT_PASS_2`, or `CODE_SUMMARY_PROMPT_PASS_3` variables to adjust the prompts for each pass.

2. **Creating New Prompt Templates**:

    - Add new variables in `summarization_prompts.py` for your custom prompts.
    - Ensure your prompts include placeholders for dynamic content (e.g., `{code}`, `{children_summaries}`).

3. **Integrating Custom Prompts**:
    - Update the `SummarizationPromptCreator` class to include your new prompt templates.
    - Modify the `_interpolation_strategies` dictionary to use your custom prompts for specific scenarios.

Example of a custom prompt template:

```python
CUSTOM_PROMPT = """
Analyze the following Python code and provide a summary focusing on:
1. Main functionality
2. Key algorithms or patterns used
3. Potential optimizations or improvements

Code:
{code}

Additional Context:
{children_summaries}
{dependency_summaries}
{import_details}

Please provide a concise yet comprehensive summary.
"""
```

### OpenAISummarizer and OllamaSummarizer

These classes provide implementations for summarizing code using OpenAI and Ollama APIs respectively.

Key method:

-   `summarize_code`: Generates a summary for the given code snippet and context.

## 🚀 Usage

To use the summarizer functionality:

1. Initialize the summarizer with appropriate configurations:

```python
from fenec import OpenAISummarizer, OllamaSummarizer
from fenec.configs import OpenAISummarizationConfigs, OllamaSummarizationConfigs

# For OpenAI
openai_summarizer = OpenAISummarizer(OpenAISummarizationConfigs())

# For Ollama
ollama_summarizer = OllamaSummarizer(OllamaSummarizationConfigs())
```

2. Use the summarizer to generate code summaries:

```python
summary = openai_summarizer.summarize_code(
    code="def hello_world():\n    print('Hello, world!')",
    model_id="function_1",
    children_summaries="No child functions.",
    dependency_summaries="No dependencies.",
    import_details="No imports.",
    parent_summary="Module containing greeting functions.",
    pass_number=1
)

print(summary.summary if summary else "Summarization failed")
```

3. For multi-pass summarization, use the CLI with the `--passes` argument:

```bash
fenec /path/to/your/codebase --update-all --passes 3
```

This command processes the entire codebase using 3 passes for summarization (bottom-up, top-down, then bottom-up again), providing more comprehensive and context-aware summaries.

## 🚧 Under Development

Please note that the summarizer functionality, like the rest of Fenec, is under active development and subject to change. Current areas of focus include:

-   Improving multi-pass summarization logic for more cohesive summaries
-   Enhancing integration with the graph database for better context awareness
-   Optimizing prompt generation for different types of code structures
-   Expanding support for additional LLM providers

## 🤝 Contributing

We welcome contributions to improve and expand the summarizer functionality! If you have ideas or want to contribute, please check our [Contributing Guidelines](../../CONTRIBUTING.md) and consider opening an issue or submitting a pull request.

Some areas where contributions would be particularly valuable:

-   Tests, tests, and more tests! - Due to a rush to get Fenec out the door, we have a lot of untested code.
-   Implementing support for additional LLM providers
-   Enhancing the prompt generation logic for better summaries
-   Improving the efficiency of multi-pass summarization
-   Developing more sophisticated context gathering from the graph database

## 🗺️ Roadmap

The future development of the summarizer functionality will focus on:

1. Refining multi-pass summarization for more accurate and context-aware summaries
2. Implementing adaptive summarization strategies based on code complexity and structure
3. Exploring techniques to reduce token usage while maintaining summary quality
4. Asynchronous and parallel summarization for faster processing

For a more comprehensive view of our plans, please refer to our [Roadmap](../../ROADMAP.md).

We appreciate your interest in Fenec's summarizer functionality and, if you're interested, look forward to your contributions in making it even more powerful and user-friendly!
