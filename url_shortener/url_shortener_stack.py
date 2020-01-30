from aws_cdk import core, aws_dynamodb


class UrlShortenerStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # The code that defines your stack goes here
        # creating DynamoDb table
        table = aws_dynamodb.Table(self, "mapping-table", 
                                partition_key=aws_dynamodb.Attribute(name="id", type=aws_dynamodb.AttributeType.STRING))
# cdk deploy --profile-workProfile to deploy resource onto my account
