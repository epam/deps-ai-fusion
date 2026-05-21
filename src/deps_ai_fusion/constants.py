PROJECT_NAME = "ai-fusion"
DESCRIPTION = """
    A unified interface over multiple LLM providers and LLM-based applications,
    streamlining integration and interaction within DEPS.
"""

V1_PREFIX = "/v1"
BASE_API_PREFIX = "/api/ai-fusion"
V1_API_PREFIX = BASE_API_PREFIX + V1_PREFIX
SWAGGER_DOC_URL = "/docs"

AGENT_STREAM_PREFIX = f"{BASE_API_PREFIX}{V1_PREFIX}/agent/stream"

DOCUMENTS_EXCHANGER = "Documents"
AI_FUSION_DESTINATION = "AIFusion"
DOCUMENT_TYPE_EXCHANGER = "DocumentType"
EXTRACTION_EXCHANGE = "Extractor"
EXTRACTION_FIELDS_DESTINATION = "ExtractionFieldsDestination"
CONVERSATION_DESTINATION = "Conversation"

EVENTS_QUEUE = "ai-fusion-events"
COMMANDS_QUEUE = "ai-fusion-commands"

COMMANDS_CHANNEL = "AiFusionCommands"
COMMANDS_REPLIES_CHANNEL = "AiFusionCommandsReplies"
