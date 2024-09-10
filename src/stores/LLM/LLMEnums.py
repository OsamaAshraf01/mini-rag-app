from enum import Enum

class LLMEnum(Enum):
    OPENAI = "OPENAI"
    COHERE = "COHERE"


class OpenAIEnum(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class CoHereEnum(Enum):
    SYSTEM = "SYSTEM"
    USER = "USER"
    ASSISTANT = "CHATBOT"

    INPUT_TYPE_QUERY = "search_query"
    INPUT_TYPE_DOCUMENT = "search_document"


class InputTypeEnum(Enum):
    QUERY = "query"
    DOCUMENT = "document"
