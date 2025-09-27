"""Tests for data models."""

from datetime import datetime

import pytest

from hyperpod_tui.models import Instance, InstanceGroup, Cluster


class TestInstance:
    """Test Instance model."""
    
    def test_instance_creation(self):
        """Test creating an instance."""
        instance = Instance(
            instance_id="i-123456789",
            instance_type="ml.p4d.24xlarge",
            status="InService",
            availability_zone="us-east-1a",
            private_ip="10.0.1.100",
            launch_time=datetime(2024, 1, 15, 10, 30, 0)
        )
        
        assert instance.instance_id == "i-123456789"
        assert instance.instance_type == "ml.p4d.24xlarge"
        assert instance.status == "InService"
    
    def test_instance_to_dict(self):
        """Test converting instance to dictionary."""
        instance = Instance(
            instance_id="i-123456789",
            instance_type="ml.p4d.24xlarge",
            status="InService",
            availability_zone="us-east-1a",
            private_ip="10.0.1.100",
            launch_time=datetime(2024, 1, 15, 10, 30, 0)
        )
        
        result = instance.to_dict()
        
        assert result["Instance ID"] == "i-123456789"
        assert result["Type"] == "ml.p4d.24xlarge"
        assert result["Status"] == "InService"
        assert result["Private IP"] == "10.0.1.100"
        assert result["Launch Time"] == "2024-01-15 10:30:00"
    
    def test_instance_to_dict_with_none_values(self):
        """Test converting instance with None values to dictionary."""
        instance = Instance(
            instance_id="i-123456789",
            instance_type="ml.p4d.24xlarge",
            status="InService",
            availability_zone="us-east-1a"
        )
        
        result = instance.to_dict()
        
        assert result["Private IP"] == "N/A"
        assert result["Public IP"] == "N/A"
        assert result["Launch Time"] == "N/A"


class TestInstanceGroup:
    """Test InstanceGroup model."""
    
    def test_instance_group_creation(self):
        """Test creating an instance group."""
        instances = [
            Instance("i-123", "ml.p4d.24xlarge", "InService", "us-east-1a"),
            Instance("i-456", "ml.p4d.24xlarge", "InService", "us-east-1b")
        ]
        
        group = InstanceGroup(
            name="worker-group",
            instance_type="ml.p4d.24xlarge",
            target_count=4,
            current_count=2,
            status="Scaling",
            instances=instances
        )
        
        assert group.name == "worker-group"
        assert group.target_count == 4
        assert group.current_count == 2
        assert len(group.instances) == 2
    
    def test_instance_group_to_dict(self):
        """Test converting instance group to dictionary."""
        instances = [Instance("i-123", "ml.p4d.24xlarge", "InService", "us-east-1a")]
        
        group = InstanceGroup(
            name="worker-group",
            instance_type="ml.p4d.24xlarge",
            target_count=4,
            current_count=1,
            status="Scaling",
            instances=instances
        )
        
        result = group.to_dict()
        
        assert result["Name"] == "worker-group"
        assert result["Target Count"] == "4"
        assert result["Current Count"] == "1"
        assert result["Instances"] == "1 instances"


class TestCluster:
    """Test Cluster model."""
    
    def test_cluster_creation(self):
        """Test creating a cluster."""
        instance_groups = [
            InstanceGroup("group1", "ml.p4d.24xlarge", 2, 2, "InService", []),
            InstanceGroup("group2", "ml.m5.xlarge", 1, 1, "InService", [])
        ]
        
        cluster = Cluster(
            name="test-cluster",
            arn="arn:aws:sagemaker:us-east-1:123456789012:cluster/test-cluster",
            status="InService",
            creation_time=datetime(2024, 1, 15, 10, 30, 0),
            instance_groups=instance_groups
        )
        
        assert cluster.name == "test-cluster"
        assert cluster.status == "InService"
        assert len(cluster.instance_groups) == 2
    
    def test_cluster_to_dict(self):
        """Test converting cluster to dictionary."""
        instances = [Instance("i-123", "ml.p4d.24xlarge", "InService", "us-east-1a")]
        instance_groups = [
            InstanceGroup("group1", "ml.p4d.24xlarge", 2, 2, "InService", instances)
        ]
        
        cluster = Cluster(
            name="test-cluster",
            arn="arn:aws:sagemaker:us-east-1:123456789012:cluster/test-cluster",
            status="InService",
            creation_time=datetime(2024, 1, 15, 10, 30, 0),
            instance_groups=instance_groups
        )
        
        result = cluster.to_dict()
        
        assert result["Name"] == "test-cluster"
        assert result["Status"] == "InService"
        assert result["Instance Groups"] == "1 groups"
        assert result["Total Instances"] == "1"
        assert result["Created"] == "2024-01-15 10:30:00"