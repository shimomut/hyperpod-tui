"""Data models for HyperPod resources."""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime


@dataclass
class Instance:
    """Represents a HyperPod instance."""
    instance_id: str
    instance_type: str
    status: str
    availability_zone: str
    private_ip: Optional[str] = None
    public_ip: Optional[str] = None
    launch_time: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "Instance ID": self.instance_id,
            "Type": self.instance_type,
            "Status": self.status,
            "AZ": self.availability_zone,
            "Private IP": self.private_ip or "N/A",
            "Public IP": self.public_ip or "N/A",
            "Launch Time": self.launch_time.strftime("%Y-%m-%d %H:%M:%S") if self.launch_time else "N/A"
        }


@dataclass
class InstanceGroup:
    """Represents a HyperPod instance group."""
    name: str
    instance_type: str
    target_count: int
    current_count: int
    status: str
    instances: List[Instance]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "Name": self.name,
            "Instance Type": self.instance_type,
            "Target Count": str(self.target_count),
            "Current Count": str(self.current_count),
            "Status": self.status,
            "Instances": f"{len(self.instances)} instances"
        }


@dataclass
class Cluster:
    """Represents a HyperPod cluster."""
    name: str
    arn: str
    status: str
    creation_time: Optional[datetime]
    instance_groups: List[InstanceGroup]
    
    def to_dict(self) -> Dict[str, Any]:
        total_instances = sum(len(ig.instances) for ig in self.instance_groups)
        return {
            "Name": self.name,
            "ARN": self.arn,
            "Status": self.status,
            "Created": self.creation_time.strftime("%Y-%m-%d %H:%M:%S") if self.creation_time else "N/A",
            "Instance Groups": f"{len(self.instance_groups)} groups",
            "Total Instances": str(total_instances)
        }