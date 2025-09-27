"""AWS SageMaker HyperPod client."""

import boto3
from typing import List
from datetime import datetime
from .models import Cluster, InstanceGroup, Instance
from .config import config


class HyperPodClient:
    """Client for interacting with AWS SageMaker HyperPod."""
    
    def __init__(self):
        session = boto3.Session(
            profile_name=config.get('aws.profile'),
            region_name=config.get('aws.region', 'us-east-1')
        )
        self.sagemaker = session.client('sagemaker')
    
    def list_clusters(self) -> List[Cluster]:
        """List all HyperPod clusters."""
        # For demo purposes, return mock data
        # In real implementation, this would call SageMaker API
        return [
            Cluster(
                name="training-cluster-1",
                arn="arn:aws:sagemaker:us-east-1:123456789012:cluster/training-cluster-1",
                status="InService",
                creation_time=datetime(2024, 1, 15, 10, 30, 0),
                instance_groups=[
                    InstanceGroup(
                        name="worker-group",
                        instance_type="ml.p4d.24xlarge",
                        target_count=4,
                        current_count=4,
                        status="InService",
                        instances=[
                            Instance(
                                instance_id="i-0123456789abcdef0",
                                instance_type="ml.p4d.24xlarge",
                                status="InService",
                                availability_zone="us-east-1a",
                                private_ip="10.0.1.100",
                                launch_time=datetime(2024, 1, 15, 10, 35, 0)
                            ),
                            Instance(
                                instance_id="i-0123456789abcdef1",
                                instance_type="ml.p4d.24xlarge",
                                status="InService",
                                availability_zone="us-east-1b",
                                private_ip="10.0.2.100",
                                launch_time=datetime(2024, 1, 15, 10, 36, 0)
                            )
                        ]
                    ),
                    InstanceGroup(
                        name="controller-group",
                        instance_type="ml.m5.xlarge",
                        target_count=1,
                        current_count=1,
                        status="InService",
                        instances=[
                            Instance(
                                instance_id="i-0123456789abcdef2",
                                instance_type="ml.m5.xlarge",
                                status="InService",
                                availability_zone="us-east-1a",
                                private_ip="10.0.1.101",
                                launch_time=datetime(2024, 1, 15, 10, 33, 0)
                            )
                        ]
                    )
                ]
            ),
            Cluster(
                name="inference-cluster-1",
                arn="arn:aws:sagemaker:us-east-1:123456789012:cluster/inference-cluster-1",
                status="Creating",
                creation_time=datetime(2024, 1, 20, 14, 15, 0),
                instance_groups=[
                    InstanceGroup(
                        name="inference-group",
                        instance_type="ml.g4dn.xlarge",
                        target_count=2,
                        current_count=1,
                        status="Creating",
                        instances=[
                            Instance(
                                instance_id="i-0123456789abcdef3",
                                instance_type="ml.g4dn.xlarge",
                                status="Pending",
                                availability_zone="us-east-1c",
                                private_ip="10.0.3.100",
                                launch_time=datetime(2024, 1, 20, 14, 20, 0)
                            )
                        ]
                    )
                ]
            )
        ]