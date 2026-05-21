from typing import Callable

from deps_gen_ai.settings import ProviderCode
from langchain_aws import ChatBedrockConverse
from langchain_core.language_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import AzureChatOpenAI, ChatOpenAI

from ..settings import AgentSettings

__all__ = ["ModelProviderFactory"]


class ModelProviderFactory:
    def __init__(self, settings: AgentSettings) -> None:
        self._settings = settings

        self._mapping: dict[ProviderCode, Callable[[], BaseChatModel]] = {
            ProviderCode.EPAM_DIAL: self._dial_llm,
            ProviderCode.AZURE: self._azure_llm,
            ProviderCode.OPENAI: self._openai_llm,
            ProviderCode.GOOGLE: self._google_llm,
            ProviderCode.AWS_BEDROCK: self._aws_bedrock_llm,
        }

    @classmethod
    def from_settings(cls, settings: AgentSettings) -> "ModelProviderFactory":
        return cls(settings)

    def create_llm(self) -> BaseChatModel:
        return self._mapping[self._settings.provider_id]()

    def _dial_llm(self) -> AzureChatOpenAI:
        return AzureChatOpenAI(
            model=self._settings.model_id,
            azure_endpoint=self._settings.dial_api_endpoint,
            openai_api_key=self._settings.dial_api_key,
            api_version=self._settings.dial_api_version,
        )

    def _azure_llm(self) -> AzureChatOpenAI:
        return AzureChatOpenAI(
            model=self._settings.model_id,
            azure_endpoint=self._settings.azure_api_endpoint,
            openai_api_key=self._settings.azure_api_key,
            api_version=self._settings.azure_api_version,
        )

    def _openai_llm(self) -> ChatOpenAI:
        return ChatOpenAI(
            model=self._settings.model_id,
            api_key=self._settings.openai_api_key,
        )

    def _google_llm(self) -> ChatGoogleGenerativeAI:
        return ChatGoogleGenerativeAI(
            model=self._settings.model_id,
            google_api_key=self._settings.google_api_key,
        )

    def _aws_bedrock_llm(self) -> ChatBedrockConverse:
        aws_auth_creds = {}
        if self._settings.aws_access_key_id and self._settings.aws_secret_access_key:
            aws_auth_creds = {
                "aws_access_key_id": self._settings.aws_access_key_id,
                "aws_secret_access_key": self._settings.aws_secret_access_key,
            }

        return ChatBedrockConverse(
            model=self._settings.model_id,
            region_name=self._settings.aws_region,
            **aws_auth_creds,
        )
