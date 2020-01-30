# custom construct for fargate service to be able to run our docker image
# what is a construct? sub-class that extends the construct base class
from aws_cdk.core import Construct

from aws_cdk import aws_ecs, aws_ec2

class Traffico(Construct):
    # main business login in constructor
    def __init__(self, scope: Construct, id: str, * ,  vpc: aws_ec2.IVpc, url: str, tps: int): #using IVpc to... * means you need to specify these inputs as key word arguments
        super().__init__(scope, id)

        # define fargate service -- need cluster and task definition running within ecs cluster
        cluster = aws_ecs.Cluster(self, 'Cluster', vpc=vpc) #run it within VPC the company has -- to internal endpoint

        # task definition NEEDED define which containers need to run together and how many times
        taskdef = aws_ecs.FargateTaskDefinition(self, 'PingerTask')

        # add container to task definition + cdk assets to define docker image just like we did for lambda definition
        taskdef.add_container('Pinger', image=aws_ecs.ContainerImage.from_asset('./pinger'),  #zaslo need to spicfy environment variable for URL - general purpose traffic generator would expect an input
                                environment={
                                    'URL': url
                                    })

        aws_ecs.FargateService(self, 'PingerService',
                            cluster=cluster,
                            task_definition=taskdef,
                            desired_count=tps #translation of the mental model to run this traffic gen as many times as needed 
                            )

        #  will generate single transaction every second -- will need to scale up for more realistic traffic testing
        # duplicate container and run as many times as you want = 1:1 transaction per second and # of containers running in fargate service
        # defining abstractions for infrastructure components!
