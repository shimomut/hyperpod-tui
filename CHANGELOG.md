# Changelog

## [0.2.0] - 2025-01-27

### Added
- **Real AWS SageMaker HyperPod API integration**: Application now connects to actual AWS SageMaker HyperPod clusters instead of using mock data
- AWS connection testing with `test_aws_integration.py` script
- Better error handling for AWS connection issues
- User-friendly messages when no clusters are found or connection fails
- Improved cluster details display with real AWS data

### Changed
- `HyperPodClient.list_clusters()` now makes real API calls to `sagemaker.list_clusters()` and `sagemaker.describe_cluster()`
- Enhanced error handling with specific AWS error codes and user guidance
- Updated TUI to show helpful messages when no clusters are available
- Improved connection testing and validation

### Technical Details
- Added `botocore.exceptions` imports for better error handling
- Implemented `_test_connection()` method to validate AWS connectivity
- Added `get_cluster_details()` method for individual cluster information
- Added `is_connected()` method to check AWS connectivity status
- Enhanced cluster list display to handle empty results gracefully

### Dependencies
- boto3 >= 1.26.0 (already included)
- botocore >= 1.29.0 (already included)

### Migration from Mock Data
The application previously returned hardcoded mock clusters. Now it:
1. Connects to your configured AWS account
2. Lists actual HyperPod clusters in your region
3. Shows real cluster status, instance groups, and metadata
4. Handles cases where no clusters exist or permissions are insufficient

### Testing
Run `python test_aws_integration.py` to verify your AWS setup before using the TUI.

## [0.1.0] - 2024-01-XX

### Added
- Initial TUI implementation with mock data
- Terminal-based interface for cluster browsing
- Hierarchical navigation (Clusters → Instance Groups → Instances)
- Filtering and search functionality
- Configurable key bindings
- Cross-platform support
- Automated testing framework