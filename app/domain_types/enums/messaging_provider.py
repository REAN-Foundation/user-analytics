from enum import Enum

###############################################################################

class MessagingProvider(str, Enum):
    AWS_SNS_SQS       = "AWS-SNS-SQS"
    AZURE_SERVICE_BUS = "Azure-ServiceBus"
    GCP_PUB_SUB       = "GCP-PubSub"
    RABBITMQ          = "RabbitMQ"
