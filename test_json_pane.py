#!/usr/bin/env python3
"""Test script for JSON pane functionality."""

import curses
import sys
import os

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from hyperpod_tui.tui import ClusterListScreen
from hyperpod_tui.models import Cluster, InstanceGroup
from hyperpod_tui.aws_client import HyperPodClient


class MockHyperPodClient(HyperPodClient):
    """Mock client for testing."""
    
    def __init__(self):
        # Don't call super().__init__() to avoid AWS setup
        pass
    
    def list_clusters(self):
        """Return mock cluster data."""
        # Create mock instance groups
        ig1 = InstanceGroup(
            name="compute-group-1",
            instance_type="ml.p4d.24xlarge",
            current_count=2,
            target_count=4,
            status="InService"
        )
        
        ig2 = InstanceGroup(
            name="storage-group-1", 
            instance_type="ml.m5.large",
            current_count=1,
            target_count=1,
            status="InService"
        )
        
        # Create mock clusters
        cluster1 = Cluster(
            name="test-cluster-1",
            status="InService",
            creation_time="2024-01-15T10:30:00Z",
            instance_groups=[ig1, ig2]
        )
        
        cluster2 = Cluster(
            name="test-cluster-2", 
            status="Creating",
            creation_time="2024-01-16T14:20:00Z",
            instance_groups=[ig1]
        )
        
        return [cluster1, cluster2]
    
    def is_connected(self):
        """Mock connection status."""
        return True


def test_json_pane(stdscr):
    """Test the JSON pane functionality."""
    # Set up curses
    curses.curs_set(0)  # Hide cursor
    stdscr.nodelay(1)   # Non-blocking input
    stdscr.timeout(100) # 100ms timeout for getch()
    
    # Create mock client and screen
    client = MockHyperPodClient()
    screen = ClusterListScreen(stdscr, client)
    
    # Set initial JSON content
    screen._update_json_content()
    
    # Main loop
    while True:
        # Draw screen
        screen.draw()
        
        # Handle input
        try:
            key = stdscr.getkey()
        except curses.error:
            continue  # Timeout, continue loop
        
        # Handle key
        action = screen.handle_key(key)
        
        if action == 'quit':
            break
        elif action == 'toggle_json':
            screen.toggle_json_pane()
            screen._update_json_content()
        elif action == 'focus_changed':
            pass  # Focus already changed in handle_key
        elif action == 'up':
            screen.navigate('up')
        elif action == 'down':
            screen.navigate('down')
        elif action == 'page_up':
            screen.navigate('page_up')
        elif action == 'page_down':
            screen.navigate('page_down')
        elif action == 'home':
            screen.navigate('home')
        elif action == 'end':
            screen.navigate('end')
        elif action == 'json_up':
            screen.scroll_json('up')
        elif action == 'json_down':
            screen.scroll_json('down')
        elif action == 'json_page_up':
            screen.scroll_json('page_up')
        elif action == 'json_page_down':
            screen.scroll_json('page_down')
        elif action == 'refresh':
            screen.refresh_data()
            screen._update_json_content()
        elif action in ['filter_changed', 'search_started', 'search_cancelled']:
            screen._update_json_content()


def main():
    """Main function."""
    try:
        curses.wrapper(test_json_pane)
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("JSON Pane Test")
    print("==============")
    print("Controls:")
    print("- TAB: Toggle JSON pane / Switch focus between panes")
    print("- ↑↓: Navigate (list when focused on list, JSON when focused on JSON)")
    print("- PgUp/PgDn: Page navigation")
    print("- q: Quit")
    print("- f: Search mode")
    print("- r: Refresh")
    print()
    print("Press any key to start...")
    input()
    
    main()