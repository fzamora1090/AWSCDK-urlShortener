from aws_cdk import core, aws_dynamodb, aws_lambda, aws_apigateway, aws_ec2
from traffico import Traffico
from cdk_watchful import Watchful

# pip install -e .  ; install requirements

class UrlShortenerStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # The code that defines your stack goes here
        # creating DynamoDb table
        table = aws_dynamodb.Table(self, "mapping_table", 
                                    # partition key required
                                    partition_key=aws_dynamodb.Attribute(name="id", 
                                    type=aws_dynamodb.AttributeType.STRING)
                                    )
#$ cdk deploy --profile workProfile   ;to deploy resource onto my account with workProfile Credentials

        # create lambda resource
        function = aws_lambda.Function(self, "backend_lambda",
                                        runtime=aws_lambda.Runtime.PYTHON_3_7,
                                        # selecting runtime for lambda code
                                        handler="handler.main",
                                        # where to find lambda handler
                                        code=aws_lambda.Code.asset("./lambda")
                                        # application code tied to lambda
                                        )

        #express intent - grant permisions in construct library such as IAM Policy solves permissions problem
        table.grant_read_write_data(function)

        # adding env var -- only creating desired state representation -- token system in cdk for late binding @ provisioning-- forward preference
        function.add_environment("TABLE_NAME", table.table_name)

        # wrapped api gateway endpoint around lambda
        api = aws_apigateway.LambdaRestApi(self, "api", handler=function)

        # monitoring system - cdk-watchful
        wf = Watchful(self, 'monitoring', alarm_email='francisco@tensoriot.com')

        # watchful can  also watch complete cdk construct scopes -- will automatically discover all watchable resources within that scope(recursively) and then add them to your dash and configure alarms for them
        wf.watch_scope(self)
        

        # traffic generator - useful for load traffic tests -- custom construct to represent load generator = trafico.py

# want traffic generator to be in different stack so that the stack can be destroyed at the end of the test -- dployed seperately

class TrafficStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # define vpc for docker image testing vpc
        vpc = aws_ec2.Vpc(self, "tensor_vpc")

        Traffico(self, 'TestTraffic', vpc=vpc,
                url='https://ave621pwll.execute-api.us-east-1.amazonaws.com/prod/6ef4641e',
                tps=10
                )
#$ cdk diff --profile workProfile -- to check difference between  local env and deployed

# will create API Gateway endpoint to hit and access lambda url shortening service
# want to add under sub domain to be availble under domain name for professional looking service to run on