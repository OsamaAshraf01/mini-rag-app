from ..LLMInterface import LLMInterface
from ..LLMEnums import CoHereEnum, InputTypeEnum
import cohere
import logging

class CoHereProvider(LLMInterface):
    def __init__(self, api_key:str,
                       default_input_max_characters: int = 1000,
                       default_generation_max_output_tokens: int = 1000,
                       default_generation_temprature: float = 0.1):
        
        self.api_key = api_key

        self.default_input_max_characters = default_input_max_characters
        self.default_generation_max_output_tokens = default_generation_max_output_tokens
        self.default_generation_temprature = default_generation_temprature

        self.generation_model_id = None
        self.embedding_model_id = None
        self.embedding_size = None
        
        self.client = cohere.Client(
            api_key=self.api_key
        )

        self.logger = logging.getLogger(__name__)


    def set_generation_model(self, model_id: str):
        self.generation_model_id = model_id


    def set_embedding_model(self, model_id: str, embedding_size: int):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size


    def generate_text(self, prompt: str, chat_history: list = [], max_output_tokens: int = None, temprature: float = None):
        if not self.client:
            self.logger.error("CoHere Client was not set.")
            return None
        
        if not self.generation_model_id:
            self.logger.error("Generation Model for CoHere was not set.")
            return None
        
        max_output_tokens = max_output_tokens if max_output_tokens else self.default_generation_max_output_tokens
        temprature = temprature if temprature else self.default_generation_temprature
        
        response = self.client.chat(
            model= self.generation_model_id,
            chat_history= chat_history,
            message= self.process_text(self.construct_prompt(prompt)),
            max_tokens= max_output_tokens,
            temperature= temprature
        )

        if not response or not response.text:
            self.logger.error("Error while generating response with CoHere.")
            return None
        
        return response.text


    def embed_text(self, text: str, document_type: str = InputTypeEnum.DOCUMENT.value):
        if not self.client:
            self.logger.error("CoHere Client was not set.")
            return None
        
        if not self.embedding_model_id:
            self.logger.error("Embedding Model for CoHere was not set.")
            return None
            
        
        input_type = CoHereEnum.INPUT_TYPE_DOCUMENT.value

        if document_type == InputTypeEnum.QUERY.value:
            input_type = CoHereEnum.INPUT_TYPE_QUERY.value

        result = self.client.embed(
            texts=[self.process_text(text)],
            model= self.embedding_model_id,
            input_type= input_type,
            embedding_types= ['float']
        )

        if not result or not result.embeddings or not result.embeddings.float_ or len(result.embeddings.float_) == 0:
            self.logger.error("Error while embedding text with CoeHere.")
            return None
        
        return result.embeddings.float_[0]


    def construct_prompt(self, prompt: str, role: str):
        return {
            "role": role,
            "text": self.process_text(prompt)
        }


    def process_text(self, text:str):
        return text.strip()[:self.default_input_max_characters].strip()