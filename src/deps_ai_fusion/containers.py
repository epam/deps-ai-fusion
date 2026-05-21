from typing import Any, Type, TypeAlias

from dependency_injector import containers, providers, resources
from deps_asb import ASBClient, ASBConsumer, ASBProducer
from deps_gen_ai.context_creators import ICreateContext, PlainLayoutContextCreator
from deps_gen_ai.loaders import LayoutLoader
from deps_kafka import KafkaClient, KafkaConsumer, KafkaProducer
from deps_message_flow import MessagingDriverEnum
from deps_message_flow.commands.producer import CommandProducer
from deps_message_flow.events.publisher import DomainEventPublisher
from deps_message_flow.messaging.consumer import IMessageConsumer
from deps_message_flow.messaging.producer import IMessageProducer
from deps_message_flow.sagas.orchestration import (
    SagaCommandProducer,
    SagaDataMapping,
    SagaInstanceFactory,
    SagaManagerFactory,
)
from deps_rabbitmq import RabbitMQClient, RabbitMQConsumer, RabbitMQProducer

from deps_ai_fusion.application import (
    AgentService,
    AnalysisService,
    ConversationService,
    IControlLLMs,
    IInsightsStore,
    LLMCoordinatesService,
    LLMExtractionService,
)
from deps_ai_fusion.constants import PROJECT_NAME
from deps_ai_fusion.domain.model import IConversationRepository, ILLMExtractorRepository
from deps_ai_fusion.extras import Database, DBDialect, DBDriver
from deps_ai_fusion.infrastructure.access_management import user
from deps_ai_fusion.infrastructure.agent import (
    AgenticWorkflowFactory,
    AgentRegistrator,
    DocumentLoadingTool,
    DocumentTypeCreationTool,
    GenAIFieldCreationTool,
    GenAIQueriesAgent,
    PerformLLMExtractionTool,
)
from deps_ai_fusion.infrastructure.proxies import (
    AgenticAIProxy,
    ExtractionProxy,
    FileStorageProxy,
    MetaAgentProxy,
    ParsingProxy,
    UnifierProxy,
)
from deps_ai_fusion.infrastructure.repositories import (
    ConversationRepository,
    InsightsRepository,
    LLMExtractorRepository,
    SagaInstanceRepository,
)
from deps_ai_fusion.infrastructure.services import (
    CoordinatesProcessor,
    CoordinatesService,
    LLMsController,
)
from deps_ai_fusion.messaging.dispatcher import make_message_dispatcher
from deps_ai_fusion.messaging.sagas import (
    CreateLLMExtractorSaga,
    CreateLLMExtractorSteps,
    make_saga_data_mapping,
)

MessagingClient: TypeAlias = ASBClient | KafkaClient | RabbitMQClient


class DatabaseResource(resources.Resource):
    def init(
        self,
        username: str,
        password: str,
        host: str,
        port: int,
        database: str,
        dialect: DBDialect,
        driver: DBDriver,
        require_secure_transport: bool,
    ) -> Database:
        db = Database(
            username=username,
            password=password,
            host=host,
            port=port,
            database=database,
            dialect=dialect,
            driver=driver,
            require_secure_transport=require_secure_transport,
        )
        db.connect()
        return db

    def shutdown(self, resource: Database) -> None:
        resource.close()


class MessageBrokerResource(resources.Resource):
    def init(
        self,
        driver_type: str,
        expected_driver: str,
        client: Type[MessagingClient],
        message_connection_string: str,
        **kwargs: dict[str, Any],
    ) -> MessagingClient | None:
        return client(message_connection_string, **kwargs) if driver_type == expected_driver else None

    def shutdown(self, resource: MessagingClient | None) -> None:
        if resource:
            resource.close()


class MessageBrokers(containers.DeclarativeContainer):
    config = providers.Configuration()
    messaging_driver_settings = providers.Dependency(instance_of=object)

    broker_client: providers.Provider[MessagingClient] = providers.Selector(
        config.messaging_driver,
        asb=providers.Resource(
            MessageBrokerResource,
            driver_type=MessagingDriverEnum.ASB.value,
            expected_driver=config.messaging_driver,
            client=ASBClient,
            message_connection_string=config.message_broker_connection_string,
            asb_settings=messaging_driver_settings,
        ),
        kafka=providers.Resource(
            MessageBrokerResource,
            driver_type=MessagingDriverEnum.KAFKA.value,
            expected_driver=config.messaging_driver,
            client=KafkaClient,
            message_connection_string=config.message_broker_connection_string,
            settings=messaging_driver_settings,
        ),
        rabbitmq=providers.Resource(
            MessageBrokerResource,
            driver_type=MessagingDriverEnum.RABBITMQ.value,
            expected_driver=config.messaging_driver,
            client=RabbitMQClient,
            message_connection_string=config.message_broker_connection_string,
            settings=messaging_driver_settings,
        ),
    )


class Messaging(containers.DeclarativeContainer):
    config = providers.Configuration()
    message_brokers = providers.DependenciesContainer()

    producer: providers.Provider[IMessageProducer] = providers.Selector(
        config.messaging_driver,
        asb=providers.Singleton(
            ASBProducer,
            client=message_brokers.broker_client,
            topic_name=config.messaging_driver_settings.topic_name,
        ),
        kafka=providers.Singleton(
            KafkaProducer,
            client=message_brokers.broker_client,
        ),
        rabbitmq=providers.Singleton(
            RabbitMQProducer,
            client=message_brokers.broker_client,
        ),
    )
    consumer: providers.Provider[IMessageConsumer] = providers.Selector(
        config.messaging_driver,
        asb=providers.Singleton(
            ASBConsumer,
            client=message_brokers.broker_client,
            topic_name=config.messaging_driver_settings.topic_name,
            custom_subscription_name=PROJECT_NAME,
        ),
        kafka=providers.Singleton(
            KafkaConsumer,
            client=message_brokers.broker_client,
        ),
        rabbitmq=providers.Singleton(
            RabbitMQConsumer,
            client=message_brokers.broker_client,
        ),
    )


class Core(containers.DeclarativeContainer):
    config = providers.Configuration()
    build_info: providers.Provider[dict] = providers.Dict(
        {
            "build_tag": config.info.tag,
            "build_date": config.info.date,
            "commit_hash": config.info.hash,
        },
    )


class Datasources(containers.DeclarativeContainer):
    config = providers.Configuration()

    postgres_datasource: providers.Provider[Database] = providers.Resource(
        DatabaseResource,
        config.user,
        config.password,
        config.host,
        config.port,
        config.db,
        config.dialect,
        config.driver,
        config.require_secure_transport,
    )


class Repositories(containers.DeclarativeContainer):
    datasources = providers.DependenciesContainer()

    conversation_repository: providers.Provider[IConversationRepository] = providers.Singleton(
        ConversationRepository,
        db=datasources.postgres_datasource,
    )
    saga_instance: providers.Provider[SagaInstanceRepository] = providers.Singleton(
        SagaInstanceRepository,
        database=datasources.postgres_datasource,
    )
    llm_extractor_repository: providers.Provider[ILLMExtractorRepository] = providers.Singleton(
        LLMExtractorRepository,
        db=datasources.postgres_datasource,
    )
    insights_repository: providers.Singleton[IInsightsStore] = providers.Singleton(
        InsightsRepository,
        db=datasources.postgres_datasource,
    )


class SagaSteps(containers.DeclarativeContainer):
    proxies = providers.DependenciesContainer()
    repositories = providers.DependenciesContainer()

    create_llm_extractor: providers.Singleton[CreateLLMExtractorSteps] = providers.Singleton(
        CreateLLMExtractorSteps,
        extraction_proxy=proxies.extraction,
        extractor_repository=repositories.llm_extractor_repository,
    )


class Sagas(containers.DeclarativeContainer):
    messaging = providers.DependenciesContainer()
    command_producer: providers.Dependency[CommandProducer] = providers.Dependency()
    repositories = providers.DependenciesContainer()
    proxies = providers.DependenciesContainer()

    saga_steps: providers.Container[SagaSteps] = providers.Container(
        SagaSteps,
        proxies=proxies,
        repositories=repositories,
    )
    saga_command_producer: providers.Singleton[SagaCommandProducer] = providers.Singleton(
        SagaCommandProducer,
        command_producer,
    )

    saga_data_mapping: providers.Singleton[SagaDataMapping] = providers.Singleton(
        make_saga_data_mapping,
    )

    saga_manager_factory: providers.Singleton[SagaManagerFactory] = providers.Singleton(
        SagaManagerFactory,
        saga_instance_repository=repositories.saga_instance,
        command_producer=command_producer,
        message_consumer=messaging.consumer,
        saga_command_producer=saga_command_producer,
        saga_data_mapping=saga_data_mapping,
    )
    sagas: providers.List = providers.List(
        providers.Singleton(CreateLLMExtractorSaga, steps=saga_steps.create_llm_extractor),
    )

    saga_instance_factory: providers.Singleton[SagaInstanceFactory] = providers.Singleton(
        SagaInstanceFactory,
        saga_manager_factory,
        sagas,
    )


class Proxies(containers.DeclarativeContainer):
    config = providers.Configuration()
    user_provider = providers.Callable(lambda: user)

    extraction: providers.Singleton[ExtractionProxy] = providers.Singleton(
        ExtractionProxy,
        base_url=config.extraction_settings.url,
        timeout=config.extraction_settings.timeout,
    )
    agentic_ai: providers.Singleton[AgenticAIProxy] = providers.Singleton(
        AgenticAIProxy,
        base_url=config.agentic_ai_settings.url,
        timeout=config.agentic_ai_settings.timeout,
    )
    meta_agent: providers.Singleton[MetaAgentProxy] = providers.Singleton(
        MetaAgentProxy,
        base_url=config.meta_agent_settings.url,
        timeout=config.meta_agent_settings.timeout,
    )
    file_storage: providers.Singleton[FileStorageProxy] = providers.Singleton(
        FileStorageProxy,
        base_url=config.storage_settings.url,
        timeout=config.storage_settings.timeout,
    )
    layout_loader: providers.Singleton[LayoutLoader] = providers.Singleton(
        LayoutLoader,
        base_url=config.parsing_settings.url,
        timeout=config.parsing_settings.timeout,
        user=user_provider,
    )
    unifier: providers.Singleton[UnifierProxy] = providers.Singleton(
        UnifierProxy,
        base_url=config.unifier_settings.url,
        timeout=config.unifier_settings.timeout,
    )
    parsing: providers.Singleton[ParsingProxy] = providers.Singleton(
        ParsingProxy,
        base_url=config.parsing_settings.url,
        timeout=config.parsing_settings.timeout,
    )


class Services(containers.DeclarativeContainer):
    config = providers.Configuration()
    providers_aggregate = providers.Dependency(instance_of=object)
    proxies = providers.DependenciesContainer()

    coordinates_processor: providers.Singleton[CoordinatesProcessor] = providers.Singleton(
        CoordinatesProcessor,
        parsing=proxies.parsing,
        unifier=proxies.unifier,
    )
    llms_controller: providers.Singleton[IControlLLMs] = providers.Singleton(
        LLMsController,
        providers=providers_aggregate,
        extraction=proxies.extraction,
        unifier=proxies.unifier,
        coordinates_processor=coordinates_processor,
        llm_coordinates_enabled=config.llm_coordinates_enabled,
    )
    layout_context_creator: providers.Singleton[ICreateContext[str]] = providers.Singleton(
        PlainLayoutContextCreator,
        loader=proxies.layout_loader,
    )
    llm_coordinates: providers.Singleton[CoordinatesService] = providers.Singleton(
        CoordinatesService,
    )


class Agent(containers.DeclarativeContainer):
    datasources = providers.DependenciesContainer()
    services = providers.DependenciesContainer()
    proxies = providers.DependenciesContainer()
    repositories = providers.DependenciesContainer()
    llm_extraction_service = providers.Dependency(instance_of=object)
    providers_aggregate = providers.Dependency(instance_of=object)

    document_loading_tool: providers.Singleton[DocumentLoadingTool] = providers.Singleton(
        DocumentLoadingTool,
        layout_cc=services.layout_context_creator,
    )

    document_type_creation: providers.Singleton[DocumentTypeCreationTool] = providers.Singleton(
        DocumentTypeCreationTool,
        extractors_app=llm_extraction_service,
    )

    genai_field_creation: providers.Singleton[GenAIFieldCreationTool] = providers.Singleton(
        GenAIFieldCreationTool,
        extractors_app=llm_extraction_service,
        extraction_proxy=proxies.extraction,
    )

    perform_llm_extraction: providers.Singleton[PerformLLMExtractionTool] = providers.Singleton(
        PerformLLMExtractionTool,
        llm_providers=providers_aggregate,
        extractors_app=llm_extraction_service,
    )

    agentic_workflow_factory: providers.Singleton[AgenticWorkflowFactory] = providers.Singleton(
        AgenticWorkflowFactory,
        document_loader=document_loading_tool,
        document_type_creation=document_type_creation,
        genai_field_creation=genai_field_creation,
        perform_llm_extraction=perform_llm_extraction,
        insights_store=repositories.insights_repository,
    )

    agent_registrator: providers.Singleton[AgentRegistrator] = providers.Singleton(
        AgentRegistrator,
        agentic_ai_proxy=proxies.agentic_ai,
        meta_agent_proxy=proxies.meta_agent,
    )

    implementation: providers.Singleton[GenAIQueriesAgent] = providers.Singleton(
        GenAIQueriesAgent,
        workflow_factory=agentic_workflow_factory,
        agent_registrator=agent_registrator,
    )


class Containers(containers.DeclarativeContainer):
    config = providers.Configuration()
    current_user_tenant = providers.Callable(lambda: user.get()["organisation"])
    messaging_driver_settings = providers.Dependency(instance_of=object)
    providers_aggregate = providers.Dependency(instance_of=object)

    datasources: providers.Container[Datasources] = providers.Container(
        Datasources,
        config=config.database,
    )

    repositories: providers.Container[Repositories] = providers.Container(
        Repositories,
        datasources=datasources,
    )

    core: providers.Container[Core] = providers.Container(Core, config=config)
    message_brokers: providers.Container[MessageBrokers] = providers.Container(
        MessageBrokers,
        config=config,
        messaging_driver_settings=messaging_driver_settings,
    )

    messaging: providers.Container[Messaging] = providers.Container(
        Messaging,
        config=config,
        message_brokers=message_brokers,
    )

    command_producer: providers.Singleton[CommandProducer] = providers.Singleton(
        CommandProducer,
        messaging.producer,
    )

    domain_event_publisher: providers.Singleton[DomainEventPublisher] = providers.Singleton(
        DomainEventPublisher,
        messaging.producer,
    )

    message_dispatcher: providers.Singleton[IMessageConsumer] = providers.Singleton(
        make_message_dispatcher,
        messaging.consumer,
        messaging.producer,
    )

    proxies: providers.Container[Proxies] = providers.Container(
        Proxies,
        config=config,
    )

    sagas: providers.Container[Sagas] = providers.Container(
        Sagas,
        messaging=messaging,
        command_producer=command_producer,
        repositories=repositories,
        proxies=proxies,
    )

    services: providers.Container[Services] = providers.Container(
        Services,
        config=config,
        providers_aggregate=providers_aggregate,
        proxies=proxies,
    )

    llm_extraction_service: providers.Factory[LLMExtractionService] = providers.Factory(
        LLMExtractionService,
        llm_extractor_repository=repositories.llm_extractor_repository,
        sagas=sagas.sagas,
        saga_instance_factory=sagas.saga_instance_factory,
        llms_controller=services.llms_controller,
        domain_event_publisher=domain_event_publisher,
    )

    agent: providers.Container[Agent] = providers.Container(
        Agent,
        datasources=datasources,
        services=services,
        proxies=proxies,
        llm_extraction_service=llm_extraction_service,
        providers_aggregate=providers_aggregate,
        repositories=repositories,
    )

    conversation_service: providers.Factory[ConversationService] = providers.Factory(
        ConversationService,
        providers=providers_aggregate,
        conversation_repository=repositories.conversation_repository,
        domain_event_publisher=domain_event_publisher,
    )

    analysis_service: providers.Factory[AnalysisService] = providers.Factory(
        AnalysisService,
        providers=providers_aggregate,
        storage=proxies.file_storage,
    )

    agent_service: providers.Factory[AgentService] = providers.Factory(
        AgentService,
        agent_implementation=agent.implementation,
        insights_repository=repositories.insights_repository,
    )

    llm_coordinates_service: providers.Factory[LLMCoordinatesService] = providers.Factory(
        LLMCoordinatesService,
        extraction=proxies.extraction,
        parsing=proxies.parsing,
        unifier=proxies.unifier,
        coordintes_service=services.llm_coordinates,
    )
