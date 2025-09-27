"""AWS SageMaker HyperPod client."""

import boto3
from typing import List, Optional
from datetime import datetime
from botocore.exceptions import ClientError, NoCredentialsError
from .models import Cluster, InstanceGroup, Instance
from .config import config


class HyperPodClient:
    """Client for interacting with AWS SageMaker HyperPod."""
    
    def __init__(self):
        try:
            session = boto3.Session(
                profile_name=config.get('aws.profile'),
                region_name=config.get('aws.region', 'us-east-1')
            )
            self.sagemaker = session.client('sagemaker')
            self.region = config.get('aws.region', 'us-east-1')
            self._test_connection()
        except (NoCredentialsError, ClientError) as e:
            print(f"AWS credentials error: {e}")
            raise
    
    def _test_connection(self):
        """Test AWS connection by making a simple API call."""
        try:
            # Test connection with a simple call
            self.sagemaker.list_clusters(MaxResults=1)
        except ClientError as e:
            if e.response['Error']['Code'] == 'UnauthorizedOperation':
                print("Warning: No permission to list clusters. Some features may not work.")
            else:
                raise
    
    def list_clusters(self) -> List[Cluster]:
        """List all HyperPod clusters."""
        try:
            clusters = []
            next_token = None
            
            # Handle pagination to get all clusters
            while True:
                # Prepare API call parameters
                params = {'MaxResults': 100}
                if next_token:
                    params['NextToken'] = next_token
                
                response = self.sagemaker.list_clusters(**params)
                
                for cluster_summary in response.get('ClusterSummaries', []):
                    try:
                        # Get detailed cluster information
                        cluster_detail = self.sagemaker.describe_cluster(
                            ClusterName=cluster_summary['ClusterName']
                        )
                        
                        # Parse instance groups
                        instance_groups = []
                        for ig in cluster_detail.get('InstanceGroups', []):
                            instances = []
                            
                            # Get instances for this instance group
                            # Note: SageMaker HyperPod doesn't directly expose individual instances
                            # This is a simplified representation based on the instance group
                            for i in range(ig.get('CurrentCount', 0)):
                                instances.append(Instance(
                                    instance_id=f"hyperpod-{cluster_summary['ClusterName']}-{ig['InstanceGroupName']}-{i}",
                                    instance_type=ig['InstanceType'],
                                    status="InService" if cluster_summary['ClusterStatus'] == 'InService' else "Pending",
                                    availability_zone="N/A",  # Not directly available from HyperPod API
                                    private_ip="N/A",  # Not directly available from HyperPod API
                                    launch_time=cluster_summary.get('CreationTime', datetime.now())
                                ))
                            
                            instance_groups.append(InstanceGroup(
                                name=ig['InstanceGroupName'],
                                instance_type=ig['InstanceType'],
                                target_count=ig.get('TargetCount', 0),
                                current_count=ig.get('CurrentCount', 0),
                                status=cluster_summary['ClusterStatus'],
                                instances=instances
                            ))
                        
                        clusters.append(Cluster(
                            name=cluster_summary['ClusterName'],
                            arn=cluster_summary['ClusterArn'],
                            status=cluster_summary['ClusterStatus'],
                            creation_time=cluster_summary.get('CreationTime', datetime.now()),
                            instance_groups=instance_groups
                        ))
                        
                    except Exception as e:
                        # Continue with other clusters even if one fails
                        # Log error but don't print to stdout (interferes with TUI)
                        continue
                
                # Check if there are more pages
                next_token = response.get('NextToken')
                if not next_token:
                    break
            
            return clusters
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'UnauthorizedOperation':
                print("Error: No permission to list clusters. Check your AWS credentials and permissions.")
            else:
                print(f"AWS API error: {e}")
            return []
        except Exception as e:
            # If there's an error (e.g., no AWS credentials, no clusters, etc.)
            # Return empty list and let the UI handle it gracefully
            # Note: Don't print to stdout as it interferes with the TUI
            return []
    
    def get_cluster_details(self, cluster_name: str) -> Optional[Cluster]:
        """Get detailed information about a specific cluster."""
        try:
            response = self.sagemaker.describe_cluster(ClusterName=cluster_name)
            
            # Parse instance groups
            instance_groups = []
            for ig in response.get('InstanceGroups', []):
                instances = []
                
                # Create instance representations
                for i in range(ig.get('CurrentCount', 0)):
                    instances.append(Instance(
                        instance_id=f"hyperpod-{cluster_name}-{ig['InstanceGroupName']}-{i}",
                        instance_type=ig['InstanceType'],
                        status="InService" if response['ClusterStatus'] == 'InService' else "Pending",
                        availability_zone="N/A",
                        private_ip="N/A",
                        launch_time=response.get('CreationTime', datetime.now())
                    ))
                
                instance_groups.append(InstanceGroup(
                    name=ig['InstanceGroupName'],
                    instance_type=ig['InstanceType'],
                    target_count=ig.get('TargetCount', 0),
                    current_count=ig.get('CurrentCount', 0),
                    status=response['ClusterStatus'],
                    instances=instances
                ))
            
            return Cluster(
                name=response['ClusterName'],
                arn=response['ClusterArn'],
                status=response['ClusterStatus'],
                creation_time=response.get('CreationTime', datetime.now()),
                instance_groups=instance_groups
            )
            
        except ClientError as e:
            print(f"Error fetching cluster details for {cluster_name}: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error fetching cluster details: {e}")
            return None
    
    def is_connected(self) -> bool:
        """Check if the client can connect to AWS."""
        try:
            self.sagemaker.list_clusters(MaxResults=1)
            return True
        except Exception:
            return False