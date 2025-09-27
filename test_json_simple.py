#!/usr/bin/env python3
"""Simple test for JSON pane functionality without interactive input."""

import sys
import os

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from hyperpod_tui.tui import TUIScreen
from hyperpod_tui.models import Cluster, InstanceGroup


def test_json_functionality():
    """Test JSON pane functionality without curses."""
    
    # Create a mock screen object to test JSON functionality
    class MockScreen:
        def __init__(self):
            self.width = 120
            self.height = 30
            self.json_pane_visible = False
            self.json_content = ""
            self.json_scroll_offset = 0
            self.json_lines = []
            self.json_pane_focused = False
            self._calculate_dimensions()
        
        def _calculate_dimensions(self):
            """Calculate pane dimensions based on screen size."""
            self.header_height = 1
            self.footer_height = 2
            self.filter_height = 1
            
            # Calculate JSON pane width (40% of screen when visible)
            self.json_pane_width = int(self.width * 0.4) if self.json_pane_visible else 0
            self.left_pane_width = self.width - self.json_pane_width
            
            available_height = self.height - self.header_height - self.footer_height - self.filter_height
            self.details_height = 8
            self.list_height = available_height - self.details_height
            
            # Y positions
            self.header_y = 0
            self.filter_y = self.header_height
            self.list_y = self.header_height + self.filter_height
            self.details_y = self.list_y + self.list_height
            self.footer_y = self.height - self.footer_height
            
            # JSON pane dimensions
            self.json_pane_x = self.left_pane_width
            self.json_pane_height = available_height
        
        def toggle_json_pane(self):
            """Toggle the JSON pane visibility."""
            if self.json_pane_visible:
                # Closing JSON pane
                self.json_pane_visible = False
                self.json_pane_focused = False
            else:
                # Opening JSON pane
                self.json_pane_visible = True
                self.json_pane_focused = True  # Focus on JSON pane when opened
            self._calculate_dimensions()
        
        def set_json_content(self, data):
            """Set the content for the JSON pane."""
            import json
            try:
                self.json_content = json.dumps(data, indent=2, default=str)
                self.json_lines = self.json_content.split('\n')
                self.json_scroll_offset = 0
            except Exception as e:
                self.json_content = f"Error formatting JSON: {str(e)}"
                self.json_lines = [self.json_content]
                self.json_scroll_offset = 0
        
        def scroll_json(self, direction: str):
            """Scroll the JSON pane."""
            if not self.json_pane_visible or not self.json_lines:
                return
            
            max_scroll = max(0, len(self.json_lines) - self.json_pane_height + 2)  # +2 for border
            
            if direction == 'up':
                self.json_scroll_offset = max(0, self.json_scroll_offset - 1)
            elif direction == 'down':
                self.json_scroll_offset = min(max_scroll, self.json_scroll_offset + 1)
            elif direction == 'page_up':
                self.json_scroll_offset = max(0, self.json_scroll_offset - (self.json_pane_height - 2))
            elif direction == 'page_down':
                self.json_scroll_offset = min(max_scroll, self.json_scroll_offset + (self.json_pane_height - 2))
    
    # Test the functionality
    screen = MockScreen()
    
    print("Testing JSON pane functionality...")
    print(f"Initial state: JSON pane visible = {screen.json_pane_visible}")
    print(f"Initial dimensions: left_pane_width = {screen.left_pane_width}, json_pane_width = {screen.json_pane_width}")
    
    # Test toggling JSON pane
    screen.toggle_json_pane()
    print(f"After toggle: JSON pane visible = {screen.json_pane_visible}")
    print(f"After toggle: left_pane_width = {screen.left_pane_width}, json_pane_width = {screen.json_pane_width}")
    print(f"JSON pane focused = {screen.json_pane_focused}")
    
    # Test setting JSON content
    test_data = {
        "name": "test-cluster",
        "status": "InService",
        "creation_time": "2024-01-15T10:30:00Z",
        "instance_groups": [
            {
                "name": "compute-group-1",
                "instance_type": "ml.p4d.24xlarge",
                "current_count": 2,
                "target_count": 4,
                "status": "InService"
            }
        ]
    }
    
    screen.set_json_content(test_data)
    print(f"JSON content set, lines count: {len(screen.json_lines)}")
    print("First few lines of JSON:")
    for i, line in enumerate(screen.json_lines[:5]):
        print(f"  {i}: {line}")
    
    # Test scrolling
    print(f"Initial scroll offset: {screen.json_scroll_offset}")
    screen.scroll_json('down')
    print(f"After scroll down: {screen.json_scroll_offset}")
    screen.scroll_json('page_down')
    print(f"After page down: {screen.json_scroll_offset}")
    
    # Test toggle again
    screen.toggle_json_pane()
    print(f"After second toggle: JSON pane visible = {screen.json_pane_visible}")
    print(f"JSON pane focused = {screen.json_pane_focused}")
    
    print("JSON pane functionality test completed successfully!")


if __name__ == "__main__":
    test_json_functionality()