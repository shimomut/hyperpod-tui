#!/usr/bin/env python3
"""
Test script to verify AWS SageMaker HyperPod integration.
This script tests the real AWS API connection without running the full TUI.
"""

import sys
import os
from pathlib import Path

# Add src to path so we can import our modules
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from hyperpod_tui.aws_client import HyperPodClient
from hyperpod_tui.config import config


def test_aws_connection():
    """Test AWS connection and list clusters."""
    print("Testing AWS SageMaker HyperPod integration...")
    print(f"Region: {config.get('aws.region', 'us-east-1')}")
    print(f"Profile: {config.get('aws.profile', 'default')}")
    print()
    
    try:
        # Create client
        print("Creating HyperPod client...")
        client = HyperPodClient()
        print("✓ Client created successfully")
        
        # Test connection
        print("Testing AWS connection...")
        if client.is_connected():
            print("✓ Successfully connected to AWS")
        else:
            print("✗ Failed to connect to AWS")
            return False
        
        # List clusters
        print("Fetching HyperPod clusters...")
        clusters = client.list_clusters()
        
        if clusters:
            print(f"✓ Found {len(clusters)} cluster(s):")
            for cluster in clusters:
                print(f"  - {cluster.name} ({cluster.status})")
                print(f"    ARN: {cluster.arn}")
                print(f"    Created: {cluster.creation_time}")
                print(f"    Instance Groups: {len(cluster.instance_groups)}")
                for ig in cluster.instance_groups:
                    print(f"      - {ig.name}: {ig.current_count}/{ig.target_count} {ig.instance_type} ({ig.status})")
                print()
        else:
            print("ℹ No HyperPod clusters found in this region")
            print("  This could mean:")
            print("  - No clusters exist in the current region")
            print("  - Insufficient permissions to list clusters")
            print("  - AWS credentials are not properly configured")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure AWS credentials are configured:")
        print("   - Run 'aws configure' to set up credentials")
        print("   - Or set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables")
        print("   - Or use IAM roles if running on EC2")
        print("2. Ensure you have permissions for SageMaker HyperPod:")
        print("   - sagemaker:ListClusters")
        print("   - sagemaker:DescribeCluster")
        print("3. Check that you're in the correct AWS region")
        return False


def main():
    """Main function."""
    print("HyperPod TUI - AWS Integration Test")
    print("=" * 40)
    
    success = test_aws_connection()
    
    print("\n" + "=" * 40)
    if success:
        print("✓ AWS integration test completed successfully!")
        print("You can now run the TUI with: python -m hyperpod_tui.main")
    else:
        print("✗ AWS integration test failed!")
        print("Please fix the issues above before running the TUI.")
        sys.exit(1)


if __name__ == "__main__":
    main()