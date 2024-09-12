from .LLMEnums import LLMEnum
from .providers import CoHereProvider, OpenAIProvider
from helpers.config import Settings
class LLMProviderFactory:
    def __init__(self, config: Settings):
        self.config = config

    def create(self, provider):
        if provider == LLMEnum.OPENAI.value:
            return OpenAIProvider(
                api_key= self.config.OPENAI_API_KEY,
                api_url= self.config.OPENAI_API_URL,
                default_input_max_characters= self.config.DEFAULT_INPUT_MAX_CHARACTERS,
                default_generation_max_output_tokens= self.config.DEFAULT_GENERATION_MAX_OUTPUT_TOKENS,
                default_generation_temprature= self.config.DEFAULT_GENERATION_TEMPRATURE
            )

        elif provider == LLMEnum.COHERE.value:
            return CoHereProvider(
                api_key= self.config.COHERE_API_KEY,
                default_input_max_characters= self.config.DEFAULT_INPUT_MAX_CHARACTERS,
                default_generation_max_output_tokens= self.config.DEFAULT_GENERATION_MAX_OUTPUT_TOKENS,
                default_generation_temprature= self.config.DEFAULT_GENERATION_TEMPRATURE
            )

        return None