EXAMPLE_1 = """
This implements a data processing pipeline for analyzing genomic sequencing data. Its purpose is to process raw sequencing reads, align them to a reference genome, and perform analyses like variant calling and gene expression quantification. Key components include: SequenceReader for parsing sequencing files; AlignmentEngine using the Burrows-Wheeler Aligner; VariantCaller for identifying genomic variants; and ExpressionQuantifier for calculating gene expression levels.
The implementation uses parallel processing with a producer-consumer pattern and thread pool. It employs a suffix array for fast alignment and a hidden Markov model for variant calling. The pipeline features robust error handling with a custom PipelineException class.
The technical stack includes BioPython, NumPy, SciPy, Pandas, and Dask. It integrates with SAMtools and BEDTools for specific genomic operations.
In the context of a bioinformatics platform, this pipeline processes raw data into actionable insights. It interfaces with data acquisition systems, LIMS, and visualization tools. Its modular design supports various sequencing technologies and experimental designs.
"""

EXAMPLE_2 = """
This code creates a flexible reinforcement learning (RL) framework for training and evaluating agents in various environments. It provides a unified interface for RL algorithms, environments, and neural networks. Key components include: Agent base class; Environment class; ReplayBuffer for experience replay; PolicyNetwork and ValueNetwork for function approximation; and Trainer for orchestrating training.
The implementation uses a modular design, supporting both on-policy (e.g., PPO) and off-policy (e.g., SAC) methods. It implements importance sampling and Generalized Advantage Estimation. A custom TensorBoard logger visualizes training progress.
The technical stack comprises PyTorch, NumPy, Gym, Ray, and MLflow. It integrates with simulators like Mujoco and Bullet for robotics simulations.
In AI research and development, this framework serves as a tool for exploring RL algorithms. It interfaces with HPC clusters, databases, and provides APIs for integration with higher-level AI systems. Its modular architecture supports collaborative research and a wide range of applications from game-playing to autonomous vehicles.
"""

CODE_SUMMARY_PROMPT_PASS_1 = """
You are an expert code analyst tasked with summarizing Python code. Your goal is to create a comprehensive and informative summary that captures the essence of the code's functionality, structure, and purpose. This summary will be used in a vector search system, so it needs to be semantically rich and consistently structured.

Provide your summary with the following information but written in paragraph form:

1. Purpose: [Comprehensive description of the code's main goal, functionality, and significance]
2. Key Components: [Main functions, classes, or modules with refined descriptions, separated by semicolons]
3. Implementation: [Detailed explanation of how the code works, including notable algorithms, data structures, and design patterns]
4. Technical Stack: [Comprehensive list of libraries, frameworks, or technologies used, with brief explanations of their roles, separated by commas]
5. Context: [How this code fits into the larger project or system, including its interactions with other components]

Ensure the summary is very detailed and technical.

Evaluation Criteria:
- Accuracy: The summary correctly represents the code's functionality.
- Conciseness: Information is presented clearly and efficiently within the given length constraints.
- Semantic Richness: Use of relevant technical terms and concepts that would be valuable in a vector search.
- Consistency: Adherence to the specified structure for easy parsing and embedding.

Examples:
Here are two high-quality examples of code summaries following the specified format:

Example 1:
{EXAMPLE_1}

Example 2:
{EXAMPLE_2}

Process:
1. Analyze the overall structure and purpose of the code.
2. Identify key functions, classes, and their relationships.
3. Understand the main algorithms or processes implemented.
4. Recognize the technical stack and any unique features of the implementation.
5. Consider how this code relates to its dependencies or the larger system.
6. Synthesize this information into a cohesive summary following the output format and drawing inspiration from the provided examples.

Now, please summarize the following code:

```python
{code}
```

Additional Context:
Children Summaries: {children_summaries}
Dependency's Summaries: {dependency_summaries}
Imports: {import_details}

Remember to follow the specified output format and evaluation criteria in your summary, optimizing for vector search retrieval. Use the provided examples as a guide for the level of detail and style expected in your summary.
"""

CODE_SUMMARY_PROMPT_PASS_2 = """
You are an expert code analyst performing the second pass of a multi-pass code summarization task. Your goal is to build upon the first-pass summary and provide more detailed information about the implementation and technical stack and how this code fits into the larger project or system. This summary will be used in a vector search system and as input for the final pass.

Provide your summary with the following information but written in paragraph form:

1. Purpose: [Comprehensive description of the code's main goal, functionality, and significance]
2. Key Components: [Main functions, classes, or modules with refined descriptions, separated by semicolons]
3. Implementation: [Detailed explanation of how the code works, including notable algorithms, data structures, and design patterns]
4. Technical Stack: [Comprehensive list of libraries, frameworks, or technologies used, with brief explanations of their roles, separated by commas]
5. Context: [How this code fits into the larger project or system, including its interactions with other components]

Ensure the summary is very detailed and technical.

Evaluation Criteria:
- Accuracy: The summary correctly represents the code's functionality and implementation details.
- Conciseness: Information is presented clearly and efficiently within the given length constraints.
- Semantic Richness: Use of relevant technical terms and concepts that would be valuable in a vector search.
- Consistency: Adherence to the specified structure for easy parsing and embedding.

EXAMPLE 1:
{EXAMPLE_1}

EXAMPLE 2:
{EXAMPLE_2}

Previous Summary:
{previous_summary}

Now, please provide a second-pass summary of the following code, building upon the first-pass summary:

```python
{code}
```

Additional Context:
Summary of parents or codeblocks that depend on this one: {parent_summary}
Imports: {import_details}
Dependencies: {dependency_summaries}

Focus on providing more detailed information about the implementation and technical stack and how the code fits in with the larger codebase; refining, expanding, and updating the first-pass summary given the additional context and higher level view of how this code fits into the grander scheme.
"""

CODE_SUMMARY_PROMPT_PASS_3 = """
You are an expert code analyst performing the final pass of a multi-pass code summarization task. Your goal is to refine and contextualize the previous summary, providing a comprehensive overview of the code that includes its role in the larger system. This final summary will be used in a vector search system.

Provide your summary with the following information but written in paragraph form:

1. Purpose: [Comprehensive description of the code's main goal, functionality, and significance]
2. Key Components: [Main functions, classes, or modules with refined descriptions, separated by semicolons]
3. Implementation: [Detailed explanation of how the code works, including notable algorithms, data structures, and design patterns]
4. Technical Stack: [Comprehensive list of libraries, frameworks, or technologies used, with brief explanations of their roles, separated by commas]
5. Context: [How this code fits into the larger project or system, including its interactions with other components]

Ensure the summary is very detailed and technical.

Evaluation Criteria:
- Accuracy: The summary correctly represents the code's functionality, implementation details, and context.
- Conciseness: Information is presented clearly and efficiently within the given length constraints.
- Semantic Richness: Use of relevant technical terms and concepts that would be valuable in a vector search.
- Consistency: Adherence to the specified structure for easy parsing and embedding.
- Contextual Relevance: Clear explanation of the code's role in the larger system.

EXAMPLE 1:
{EXAMPLE_1}

EXAMPLE 2:
{EXAMPLE_2}

Previous Summary:
{previous_summary}


Now, please provide a final, comprehensive summary of the following code, building upon the previous summary and the context provided:

```python
{code}
```

Additional Context:
Children Summaries: {children_summaries}
Dependencies: {dependency_summaries}
Imports: {import_details}

Focus on refining, expanding, and updating the previous summary, adding context about the code's role in the larger system, and ensuring a comprehensive final summary.
"""


SUMMARIZER_DEFAULT_INSTRUCTIONS = """You are a code summarizer. Your task is to analyze the code provided and create a concise summary of the
given code based on the prompt provided. Your summary should be technical yet understandable, providing a clear picture of the code's purpose, main
features, and key components.
"""

SUMMARIZER_DEFAULT_DESCRIPTION = """Summarizes Python code."""

summary_prompt_list: list[str] = [
    EXAMPLE_1,
    EXAMPLE_2,
    CODE_SUMMARY_PROMPT_PASS_1,
    CODE_SUMMARY_PROMPT_PASS_2,
    CODE_SUMMARY_PROMPT_PASS_3,
]
