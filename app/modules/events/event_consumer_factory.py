from app.common.logger import logger
from app.config.config import get_settings
from app.domain_types.enums.messaging_provider import MessagingProvider
from app.modules.events.event_consumer_interface import IEventConsumer

###############################################################################

def get_event_consumer() -> IEventConsumer | None:
    provider = get_settings().MESSAGING_PROVIDER
    if provider == MessagingProvider.RABBITMQ.value:
        from app.modules.events.providers.rabbitmq.rabbitmq_event_consumer import RabbitMqEventConsumer
        return RabbitMqEventConsumer()
    if provider == MessagingProvider.AWS_SNS_SQS.value:
        from app.modules.events.providers.aws_sqs.sqs_event_consumer import AwsSqsEventConsumer
        return AwsSqsEventConsumer()
    logger.warning(f"Unsupported messaging provider: {provider}. Event consumer not started")
    return None
