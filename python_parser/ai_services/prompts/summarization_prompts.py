SUMMARIZER_DEFAULT_INSTRUCTIONS = """You are a code summarizer. Your task is to analyze the code provided and create a concise summary of the
given code based on the prompt provided. Your summary should be technical yet understandable, providing a clear picture of the code's purpose, main
features, and key components.
"""

SUMMARIZER_DEFAULT_DESCRIPTION = """Summarizes Python code."""

COD_SUMMARIZATION_PROMPT = """Prompt: "Summarize the code provided."

Chain of Density Steps:

1. **Initial Summary**: Start by generating a high-level summary of the code. This summary should briefly describe the main functionality 
or purpose of the code. For example, "This code implements a basic sorting algorithm."

2. **Identify Missing Key Components**: After creating the initial summary, identify 1-3 key components that are missing from the summary. These 
components could be specific functions, algorithms, data structures, or important variables used in the code.

3. **Incorporate Missing Components**: Rewrite the summary to include the identified components, making it more detailed and informative. Ensure 
that the length of the summary does not increase. For example, "This code implements a quicksort algorithm using a pivot selection function and 
partitioning logic."

4. **Repeat the Process**: Continue this process, identifying missing components and integrating them into the summary in each iteration. After 
each iteration, the summary should become more detailed, covering more aspects of the code without becoming longer.

5. **Final Summary**: After 5 iterations, the final summary should be dense with technical details and accurately reflect the key functionalities, 
algorithms, and structures used in the code. It should provide a clear and concise overview of the code's content.

Guidelines:
- Ensure that each iteration of the summary accurately reflects the code's functionality.
- The summary should be technical yet understandable, providing a clear picture of the code's purpose, main features, and key components.
- Avoid technical jargon that is not directly relevant to the code's main functionality.
- The final summary should be comprehensive yet concise, capturing the essence of the code.

CODE:
```Python
{code}
```
"""

ROLE_ASSIGNMENT_PROMPT = """Act as a Code Summarizer. Analyze this code and create a concise summary of its main functionalities, key algorithms, 
and important variables. Explain how the code is intended to be used and its primary purpose. Your summary should cover the essence of the code, its 
general architecture, and how each part contributes to the overall functionality. The summary should be technical yet understandable, providing a clear 
picture of the code's purpose, main features, and key components. Combine the last two summaries together and write them below the phrase "FINAL_SUMMARY:"

CODE:
```Python
{code}
```
"""

ITERATIVE_REFINEMENT_AND_COMBINING_OUTPUTS_PROMPT = """Provide a high-level overview of this code, outlining its general purpose, structure, and intended 
use. Then, in a separate summary, focus on the key functions, classes, methods, or code blocks, their roles within the code, and how they support the 
code's main purpose. Lastly, summarize the unique aspects or complex parts of the code, such as specific algorithms or data structures used, and explain 
how these contribute to the functionality and intended use of the code.

CODE:
```Python
{code}
```
"""

GENERAL_PURPOSE_SUMMARIZATION_PROMPT = """Summarize the following code, focusing on its primary purpose and main functions. Describe the algorithms it 
implements and the intended use of the code. Include a brief description of significant classes and methods, their roles, and how they interconnect to 
achieve the code's objectives. Highlight any unique coding techniques used and explain how they contribute to the code's overall functionality.

CODE:
```Python
{code}
```
"""

summary_prompt_list: list[str] = [
    COD_SUMMARIZATION_PROMPT,
    ROLE_ASSIGNMENT_PROMPT,
    ITERATIVE_REFINEMENT_AND_COMBINING_OUTPUTS_PROMPT,
    GENERAL_PURPOSE_SUMMARIZATION_PROMPT,
]
