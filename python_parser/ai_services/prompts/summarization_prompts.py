SUMMARIZER_DEFAULT_INSTRUCTIONS = """You are a code summarizer. Your task is to analyze the code provided and create a concise summary of the
given code based on the prompt provided. Your summary should be technical yet understandable, providing a clear picture of the code's purpose, main
features, and key components.
"""

SUMMARIZER_DEFAULT_DESCRIPTION = """Summarizes Python code."""

# TODO: Customize based on code block type.
COD_SUMMARIZATION_PROMPT_WITH_EVERYTHING = """Prompt: "Summarize the code provided."

NOTE: Below the code are summaries, `CHILDREN_SUMMARIES` and `LOCAL_IMPORT_AND_DEPENDENCY_SUMMARIES`. The `CHILDREN_SUMMARIES of summaries of all 
of the code blocks defined in the `CODE`. The `LOCAL_IMPORT_AND_DEPENDENCY_SUMMARIES` are summaries of all the code blocks defined locally in the 
overarching project that the `CODE` depends on or uses to accomplish its intended task. Use these summaries to help you write your summary of the 
`CODE`, directly referencing the immediate children and the imports the `CODE` depends on. 

If the code is for a function, or class, specifically reference the function or class name, and any names defined inside of it, in your summary.

Chain of Density Steps:

1. INITIAL SUMMARY: Start by generating a high-level summary of the code. This summary should briefly describe the main functionality 
and purpose of the code. For example, "This code implements a basic sorting algorithm to return a list of integers sorted in ascending order."

2. IDENTIFY MISSING KEY COMPONENTS: After creating the initial summary, identify 1-3 key components that are missing from the summary. These 
components could be specific functions, algorithms, data structures, classes, local and third-party library imports and variables, etc.

3. INCORPORATE MISSING COMPONENTS: Rewrite the summary to include the identified components, making it more detailed and informative and explains the
functionality and purpose of the code even better. Ensure that the length of the summary does not increase. For example, "This code implements a 
quicksort algorithm using a pivot selection function and partitioning logic to return a list of integers in ascending order."

4. REPEAT THE PROCESS: Continue this process, identifying missing components and integrating them into the summary in each iteration. After 
each iteration, the summary should become more detailed, covering more aspects of the code and getting better detail on its purpose without becoming 
longer.

5. FINAL SUMMARY: After 5 iterations, the final summary should be dense with technical details and accurately reflect the key functionalities, 
algorithms, and structures used in the code, and include detailed information on the code's purpose. It should provide a clear and concise overview of 
the code's content and purpose.

Guidelines:
- Ensure that each iteration of the summary accurately reflects the code's functionality and purpose.
- The summary should be technical yet understandable, providing a clear picture of the code's purpose, main features, and key components.
- Avoid technical jargon unless it is directly relevant to the code's main functionality.
- The final summary should be comprehensive yet concise, capturing the essence of the code, and written below the phrase "FINAL SUMMARY:".

CODE:
```Python
{code}
```

CHILDREN_SUMMARIES:
{children_summaries}

LOCAL_IMPORT_AND_DEPENDENCY_SUMMARIES:
{dependency_summaries}

STANDARD_LIBRARY_AND_THIRD_PARTY_LIBRARY_IMPORTS:
{import_details}

Make sure to write your final summary below the phrase "FINAL SUMMARY:". Take a deep breath and do some great work!
"""

COD_SUMMARIZATION_PROMPT_NO_CHILDREN = """Prompt: "Summarize the code provided."

NOTE: Below the code are summaries, `LOCAL_IMPORT_AND_DEPENDENCY_SUMMARIES`. The `LOCAL_IMPORT_AND_DEPENDENCY_SUMMARIES` are summaries of all the 
code blocks defined locally in the overarching project that the `CODE` depends on or uses to accomplish its intended task. Use these summaries to help 
write your summary of the `CODE`, directly referencing the imports the `CODE` depends on. If summaries are missing for the dependencies,
do not infer or make assumptions about their content, beyond what the code directly implies their purpose is. Instead, write your summary based on 
the code and summaries provided.

If the code is for a function, or class, specifically reference the function or class name, and any names defined inside of it, in your summary.

Chain of Density Steps:

1. INITIAL SUMMARY: Start by generating a high-level summary of the code. This summary should briefly describe the main functionality 
and purpose of the code. For example, "This code implements a basic sorting algorithm to return a list of integers sorted in ascending order."

2. IDENTIFY MISSING KEY COMPONENTS: After creating the initial summary, identify 1-3 key components that are missing from the summary. These 
components could be specific functions, algorithms, data structures, classes, local and third-party library imports and variables, etc.

3. INCORPORATE MISSING COMPONENTS: Rewrite the summary to include the identified components, making it more detailed and informative and explains the
functionality and purpose of the code even better. Ensure that the length of the summary does not increase. For example, "This code implements a 
quicksort algorithm using a pivot selection function and partitioning logic to return a list of integers in ascending order."

4. REPEAT THE PROCESS: Continue this process, identifying missing components and integrating them into the summary in each iteration. After 
each iteration, the summary should become more detailed, covering more aspects of the code and getting better detail on its purpose without becoming 
longer.

5. FINAL SUMMARY: After 5 iterations, the final summary should be dense with technical details and accurately reflect the key functionalities, 
algorithms, and structures used in the code, and include detailed information on the code's purpose. It should provide a clear and concise overview of 
the code's content and purpose.

Guidelines:
- Ensure that each iteration of the summary accurately reflects the code's functionality and purpose.
- The summary should be technical yet understandable, providing a clear picture of the code's purpose, main features, and key components.
- Avoid technical jargon unless it is directly relevant to the code's main functionality.
- The final summary should be comprehensive yet concise, capturing the essence of the code, and written below the phrase "FINAL SUMMARY:".

CODE:
```Python
{code}
```

LOCAL_IMPORT_AND_DEPENDENCY_SUMMARIES:
{dependency_summaries}

STANDARD_LIBRARY_AND_THIRD_PARTY_LIBRARY_IMPORTS:
{import_details}

Make sure to write your final summary below the phrase "FINAL SUMMARY:". Take a deep breath and do some great work!
"""

COD_SUMMARIZATION_PROMPT_NO_DEPENDENCIES = """Prompt: "Summarize the code provided."

NOTE: Below the code are summaries, `CHILDREN_SUMMARIES`. The `CHILDREN_SUMMARIES of summaries of all 
of the code blocks defined in the `CODE`. Use these summaries to help you write your summary of the 
`CODE`, directly referencing the immediate children and the imports the `CODE` depends on. 

If the code is for a function, or class, specifically reference the function or class name, and any names defined inside of it, in your summary.

Chain of Density Steps:

1. INITIAL SUMMARY: Start by generating a high-level summary of the code. This summary should briefly describe the main functionality 
and purpose of the code. For example, "This code implements a basic sorting algorithm to return a list of integers sorted in ascending order."

2. IDENTIFY MISSING KEY COMPONENTS: After creating the initial summary, identify 1-3 key components that are missing from the summary. These 
components could be specific functions, algorithms, data structures, classes, local and third-party library imports and variables, etc.

3. INCORPORATE MISSING COMPONENTS: Rewrite the summary to include the identified components, making it more detailed and informative and explains the
functionality and purpose of the code even better. Ensure that the length of the summary does not increase. For example, "This code implements a 
quicksort algorithm using a pivot selection function and partitioning logic to return a list of integers in ascending order."

4. REPEAT THE PROCESS: Continue this process, identifying missing components and integrating them into the summary in each iteration. After 
each iteration, the summary should become more detailed, covering more aspects of the code and getting better detail on its purpose without becoming 
longer.

5. FINAL SUMMARY: After 5 iterations, the final summary should be dense with technical details and accurately reflect the key functionalities, 
algorithms, and structures used in the code, and include detailed information on the code's purpose. It should provide a clear and concise overview of 
the code's content and purpose.

Guidelines:
- Ensure that each iteration of the summary accurately reflects the code's functionality and purpose.
- The summary should be technical yet understandable, providing a clear picture of the code's purpose, main features, and key components.
- Avoid technical jargon unless it is directly relevant to the code's main functionality.
- The final summary should be comprehensive yet concise, capturing the essence of the code, and written below the phrase "FINAL SUMMARY:".

CODE:
```Python
{code}
```

CHILDREN_SUMMARIES:
{children_summaries}

STANDARD_LIBRARY_AND_THIRD_PARTY_LIBRARY_IMPORTS:
{import_details}

Make sure to write your final summary below the phrase "FINAL SUMMARY:". Take a deep breath and do some great work!
"""

COD_SUMMARIZATION_PROMPT_NO_IMPORTS = """Prompt: "Summarize the code provided."

NOTE: Below the code are summaries, `CHILDREN_SUMMARIES` and `LOCAL_IMPORT_AND_DEPENDENCY_SUMMARIES`. The `CHILDREN_SUMMARIES of summaries of all 
of the code blocks defined in the `CODE`. The `LOCAL_IMPORT_AND_DEPENDENCY_SUMMARIES` are summaries of all the code blocks defined locally in the 
overarching project that the `CODE` depends on or uses to accomplish its intended task. Use these summaries to help you write your summary of the 
`CODE`, directly referencing the immediate children and the imports the `CODE` depends on. 

If the code is for a function, or class, specifically reference the function or class name, and any names defined inside of it, in your summary.

Chain of Density Steps:

1. INITIAL SUMMARY: Start by generating a high-level summary of the code. This summary should briefly describe the main functionality 
and purpose of the code. For example, "This code implements a basic sorting algorithm to return a list of integers sorted in ascending order."

2. IDENTIFY MISSING KEY COMPONENTS: After creating the initial summary, identify 1-3 key components that are missing from the summary. These 
components could be specific functions, algorithms, data structures, classes, etc.

3. INCORPORATE MISSING COMPONENTS: Rewrite the summary to include the identified components, making it more detailed and informative and explains the
functionality and purpose of the code even better. Ensure that the length of the summary does not increase. For example, "This code implements a 
quicksort algorithm using a pivot selection function and partitioning logic to return a list of integers in ascending order."

4. REPEAT THE PROCESS: Continue this process, identifying missing components and integrating them into the summary in each iteration. After 
each iteration, the summary should become more detailed, covering more aspects of the code and getting better detail on its purpose without becoming 
longer.

5. FINAL SUMMARY: After 5 iterations, the final summary should be dense with technical details and accurately reflect the key functionalities, 
algorithms, and structures used in the code, and include detailed information on the code's purpose. It should provide a clear and concise overview of 
the code's content and purpose.

Guidelines:
- Ensure that each iteration of the summary accurately reflects the code's functionality and purpose.
- The summary should be technical yet understandable, providing a clear picture of the code's purpose, main features, and key components.
- Avoid technical jargon unless it is directly relevant to the code's main functionality.
- The final summary should be comprehensive yet concise, capturing the essence of the code, and written below the phrase "FINAL SUMMARY:".

CODE:
```Python
{code}
```

CHILDREN_SUMMARIES:
{children_summaries}

LOCAL_IMPORT_AND_DEPENDENCY_SUMMARIES:
{dependency_summaries}

Make sure to write your final summary below the phrase "FINAL SUMMARY:". Take a deep breath and do some great work!
"""

COD_SUMMARIZATION_PROMPT_NO_CHILDREN_NO_IMPORTS = """Prompt: "Summarize the code provided."

NOTE: Below the code are summaries, `LOCAL_IMPORT_AND_DEPENDENCY_SUMMARIES`. The `LOCAL_IMPORT_AND_DEPENDENCY_SUMMARIES` are summaries of all the 
code blocks defined locally in the overarching project that the `CODE` depends on or uses to accomplish its intended task. Use these summaries to help 
write your summary of the `CODE`, directly referencing the imports the `CODE` depends on. If summaries are missing for the dependencies,
do not infer or make assumptions about their content, beyond what the code directly implies their purpose is. Instead, write your summary based on 
the code and summaries provided.

If the code is for a function, or class, specifically reference the function or class name, and any names defined inside of it, in your summary.

Chain of Density Steps:

1. INITIAL SUMMARY: Start by generating a high-level summary of the code. This summary should briefly describe the main functionality 
and purpose of the code. For example, "This code implements a basic sorting algorithm to return a list of integers sorted in ascending order."

2. IDENTIFY MISSING KEY COMPONENTS: After creating the initial summary, identify 1-3 key components that are missing from the summary. These 
components could be specific functions, algorithms, data structures, classes, local and third-party library imports and variables, etc.

3. INCORPORATE MISSING COMPONENTS: Rewrite the summary to include the identified components, making it more detailed and informative and explains the
functionality and purpose of the code even better. Ensure that the length of the summary does not increase. For example, "This code implements a 
quicksort algorithm using a pivot selection function and partitioning logic to return a list of integers in ascending order."

4. REPEAT THE PROCESS: Continue this process, identifying missing components and integrating them into the summary in each iteration. After 
each iteration, the summary should become more detailed, covering more aspects of the code and getting better detail on its purpose without becoming 
longer.

5. FINAL SUMMARY: After 5 iterations, the final summary should be dense with technical details and accurately reflect the key functionalities, 
algorithms, and structures used in the code, and include detailed information on the code's purpose. It should provide a clear and concise overview of 
the code's content and purpose.

Guidelines:
- Ensure that each iteration of the summary accurately reflects the code's functionality and purpose.
- The summary should be technical yet understandable, providing a clear picture of the code's purpose, main features, and key components.
- Avoid technical jargon unless it is directly relevant to the code's main functionality.
- The final summary should be comprehensive yet concise, capturing the essence of the code, and written below the phrase "FINAL SUMMARY:".

CODE:
```Python
{code}
```

LOCAL_IMPORT_AND_DEPENDENCY_SUMMARIES:
{dependency_summaries}

Make sure to write your final summary below the phrase "FINAL SUMMARY:". Take a deep breath and do some great work!
"""

COD_SUMMARIZATION_PROMPT_NO_DEPENDENCIES_NO_IMPORTS = """Prompt: "Summarize the code provided."

NOTE: Below the code are summaries, `CHILDREN_SUMMARIES`. The `CHILDREN_SUMMARIES of summaries of all 
of the code blocks defined in the `CODE`. Use these summaries to help you write your summary of the 
`CODE`, directly referencing the immediate children and the imports the `CODE` depends on. 

If the code is for a function, or class, specifically reference the function or class name, and any names defined inside of it, in your summary.

Chain of Density Steps:

1. INITIAL SUMMARY: Start by generating a high-level summary of the code. This summary should briefly describe the main functionality 
and purpose of the code. For example, "This code implements a basic sorting algorithm to return a list of integers sorted in ascending order."

2. IDENTIFY MISSING KEY COMPONENTS: After creating the initial summary, identify 1-3 key components that are missing from the summary. These 
components could be specific functions, algorithms, data structures, classes, etc.

3. INCORPORATE MISSING COMPONENTS: Rewrite the summary to include the identified components, making it more detailed and informative and explains the
functionality and purpose of the code even better. Ensure that the length of the summary does not increase. For example, "This code implements a 
quicksort algorithm using a pivot selection function and partitioning logic to return a list of integers in ascending order."

4. REPEAT THE PROCESS: Continue this process, identifying missing components and integrating them into the summary in each iteration. After 
each iteration, the summary should become more detailed, covering more aspects of the code and getting better detail on its purpose without becoming 
longer.

5. FINAL SUMMARY: After 5 iterations, the final summary should be dense with technical details and accurately reflect the key functionalities, 
algorithms, and structures used in the code, and include detailed information on the code's purpose. It should provide a clear and concise overview of 
the code's content and purpose.

Guidelines:
- Ensure that each iteration of the summary accurately reflects the code's functionality and purpose.
- The summary should be technical yet understandable, providing a clear picture of the code's purpose, main features, and key components.
- Avoid technical jargon unless it is directly relevant to the code's main functionality.
- The final summary should be comprehensive yet concise, capturing the essence of the code, and written below the phrase "FINAL SUMMARY:".

CODE:
```Python
{code}
```

CHILDREN_SUMMARIES:
{children_summaries}

Make sure to write your final summary below the phrase "FINAL SUMMARY:". Take a deep breath and do some great work!
"""

COD_SUMMARIZATION_PROMPT_NO_DEPENDENCIES_NO_CHILDREN = """Prompt: "Summarize the code provided."

If the code is for a function, or class, specifically reference the function or class name, and any names defined inside of it, in your summary.

Chain of Density Steps:

1. INITIAL SUMMARY: Start by generating a high-level summary of the code. This summary should briefly describe the main functionality 
and purpose of the code. For example, "This code implements a basic sorting algorithm to return a list of integers sorted in ascending order."

2. IDENTIFY MISSING KEY COMPONENTS: After creating the initial summary, identify 1-3 key components that are missing from the summary. These 
components could be specific functions, algorithms, data structures, classes, local and third-party library imports and variables, etc.

3. INCORPORATE MISSING COMPONENTS: Rewrite the summary to include the identified components, making it more detailed and informative and explains the
functionality and purpose of the code even better. Ensure that the length of the summary does not increase. For example, "This code implements a 
quicksort algorithm using a pivot selection function and partitioning logic to return a list of integers in ascending order."

4. REPEAT THE PROCESS: Continue this process, identifying missing components and integrating them into the summary in each iteration. After 
each iteration, the summary should become more detailed, covering more aspects of the code and getting better detail on its purpose without becoming 
longer.

5. FINAL SUMMARY: After 5 iterations, the final summary should be dense with technical details and accurately reflect the key functionalities, 
algorithms, and structures used in the code, and include detailed information on the code's purpose. It should provide a clear and concise overview of 
the code's content and purpose.

Guidelines:
- Ensure that each iteration of the summary accurately reflects the code's functionality and purpose.
- The summary should be technical yet understandable, providing a clear picture of the code's purpose, main features, and key components.
- Avoid technical jargon unless it is directly relevant to the code's main functionality.
- The final summary should be comprehensive yet concise, capturing the essence of the code, and written below the phrase "FINAL SUMMARY:".

CODE:
```Python
{code}
```

STANDARD_LIBRARY_AND_THIRD_PARTY_LIBRARY_IMPORTS:
{import_details}

Make sure to write your final summary below the phrase "FINAL SUMMARY:". Take a deep breath and do some great work!
"""

COD_SUMMARIZATION_PROMPT_WITHOUT_ANYTHING = """Prompt: "Summarize the code provided."

If the code is for a function, or class, specifically reference the function or class name, and any names defined inside of it, in your summary.

Chain of Density Steps:

1. INITIAL SUMMARY: Start by generating a high-level summary of the code. This summary should briefly describe the main functionality 
and purpose of the code. For example, "This code implements a basic sorting algorithm to return a list of integers sorted in ascending order."

2. IDENTIFY MISSING KEY COMPONENTS: After creating the initial summary, identify 1-3 key components that are missing from the summary. These 
components could be specific functions, algorithms, data structures, classes, etc.

3. INCORPORATE MISSING COMPONENTS: Rewrite the summary to include the identified components, making it more detailed and informative and explains the
functionality and purpose of the code even better. Ensure that the length of the summary does not increase. For example, "This code implements a 
quicksort algorithm using a pivot selection function and partitioning logic to return a list of integers in ascending order."

4. REPEAT THE PROCESS: Continue this process, identifying missing components and integrating them into the summary in each iteration. After 
each iteration, the summary should become more detailed, covering more aspects of the code and getting better detail on its purpose without becoming 
longer.

5. FINAL SUMMARY: After 5 iterations, the final summary should be dense with technical details and accurately reflect the key functionalities, 
algorithms, and structures used in the code, and include detailed information on the code's purpose. It should provide a clear and concise overview of 
the code's content and purpose.

Guidelines:
- Ensure that each iteration of the summary accurately reflects the code's functionality and purpose.
- The summary should be technical yet understandable, providing a clear picture of the code's purpose, main features, and key components.
- Avoid technical jargon unless it is directly relevant to the code's main functionality.
- The final summary should be comprehensive yet concise, capturing the essence of the code, and written below the phrase "FINAL SUMMARY:".

CODE:
```Python
{code}
```

Make sure to write your final summary below the phrase "FINAL SUMMARY:". Take a deep breath and do some great work!
"""


COD_SUMMARIZATION_PROMPT_OLD = """Prompt: "Summarize the code provided."

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

Below the code are summaries from the code block's the `CODE` depends on. Use these summaries to help you write your summary.

CODE:
```Python
{code}
```

Make sure to write your final summary below the phrase "FINAL_SUMMARY:". Take a deep breath and do some great work!
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
    COD_SUMMARIZATION_PROMPT_WITH_EVERYTHING,
    COD_SUMMARIZATION_PROMPT_WITHOUT_ANYTHING,
    COD_SUMMARIZATION_PROMPT_NO_CHILDREN,
    COD_SUMMARIZATION_PROMPT_NO_DEPENDENCIES,
    COD_SUMMARIZATION_PROMPT_NO_IMPORTS,
    COD_SUMMARIZATION_PROMPT_NO_CHILDREN_NO_IMPORTS,
    COD_SUMMARIZATION_PROMPT_NO_DEPENDENCIES_NO_IMPORTS,
    COD_SUMMARIZATION_PROMPT_NO_DEPENDENCIES_NO_CHILDREN,
    ROLE_ASSIGNMENT_PROMPT,
    ITERATIVE_REFINEMENT_AND_COMBINING_OUTPUTS_PROMPT,
    GENERAL_PURPOSE_SUMMARIZATION_PROMPT,
]
