from fenec.ai_services.summarizer.ollama_summarizer import OllamaSummarizer
from fenec.ai_services.summarizer.openai_summarizer import OpenAISummarizer
from fenec.ai_services.summarizer.summarizer_protocol import Summarizer
from fenec.utilities.configs.configs import (
    OpenAISummarizationConfigs,
    OllamaSummarizationConfigs,
)


def create_summarizer(
    configs: OpenAISummarizationConfigs | OllamaSummarizationConfigs,
) -> Summarizer:
    """
    Create a summarizer based on the provided configs.

    Args:
        - `configs` (OpenAISummarizationConfigs | OllamaSummarizationConfigs): The summarization configs.

    Returns:
        Summarizer: The summarizer instance.
    """
    if isinstance(configs, OpenAISummarizationConfigs):
        return OpenAISummarizer(configs)
    elif isinstance(configs, OllamaSummarizationConfigs):
        return OllamaSummarizer(configs)
    else:
        raise ValueError("Invalid summarization configs provided.")
