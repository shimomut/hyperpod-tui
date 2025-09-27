"""Main application entry point for HyperPod TUI."""

import curses
import sys
from typing import List, Optional
from .tui import ClusterListScreen, InstanceGroupListScreen, InstanceListScreen
from .aws_client import HyperPodClient
from .config import config


class HyperPodTUI:
    """Main TUI application class."""
    
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.client = HyperPodClient()
        self.screen_stack: List = []
        
        # Configure curses - be more defensive about these calls
        try:
            curses.curs_set(0)  # Hide cursor
        except curses.error:
            pass  # Some terminals don't support cursor visibility control
        
        try:
            self.stdscr.keypad(True)  # Enable special keys
        except curses.error:
            pass  # Some terminals don't support keypad
        
        self.stdscr.timeout(100)  # Non-blocking input with 100ms timeout
        
        # Start with cluster list screen
        self.current_screen = ClusterListScreen(stdscr, self.client)
    
    def run(self):
        """Main application loop."""
        try:
            while True:
                # Handle screen resize
                try:
                    self.current_screen.resize()
                except curses.error:
                    pass  # Ignore resize errors
                
                # Draw current screen
                self.current_screen.draw()
                
                # Get user input
                try:
                    key = self.stdscr.getkey()
                except curses.error:
                    # Timeout or no input
                    continue
                
                # Handle input
                if not self.handle_input(key):
                    break
                    
        except KeyboardInterrupt:
            pass
    
    def handle_input(self, key: str) -> bool:
        """Handle user input. Returns False to quit."""
        # Let the current screen handle the key first
        action = self.current_screen.handle_key(key)
        
        if action == 'quit':
            return False
        
        elif action == 'refresh':
            if hasattr(self.current_screen, 'refresh_data'):
                self.current_screen.refresh_data()
        
        elif action == 'back':
            return self.go_back()
        
        elif action == 'enter':
            return self.handle_enter()
        
        elif action in ['up', 'down', 'page_up', 'page_down', 'home', 'end']:
            self.current_screen.navigate(action)
        
        elif action == 'expand_details':
            self.current_screen.adjust_details_height(True)
        
        elif action == 'shrink_details':
            self.current_screen.adjust_details_height(False)
        
        elif action == 'clear_filter':
            self.current_screen.filter_text = ""
            self.current_screen.selected_index = 0
            self.current_screen.scroll_offset = 0
        
        elif action == 'filter_changed':
            # Filter was updated, screen will redraw automatically
            pass
        
        # Handle window resize
        elif key == 'KEY_RESIZE':
            self.current_screen.resize()
        
        return True
    
    def handle_enter(self) -> bool:
        """Handle Enter key press to drill down."""
        if isinstance(self.current_screen, ClusterListScreen):
            cluster = self.current_screen.get_selected_cluster()
            if cluster:
                self.screen_stack.append(self.current_screen)
                self.current_screen = InstanceGroupListScreen(self.stdscr, cluster)
        
        elif isinstance(self.current_screen, InstanceGroupListScreen):
            instance_group = self.current_screen.get_selected_instance_group()
            if instance_group:
                self.screen_stack.append(self.current_screen)
                self.current_screen = InstanceListScreen(self.stdscr, instance_group)
        
        # Instance screen is the deepest level, no further drilling
        
        return True
    
    def go_back(self) -> bool:
        """Go back to the previous screen."""
        if self.screen_stack:
            self.current_screen = self.screen_stack.pop()
        return True


def main():
    """Main entry point."""
    try:
        def run_tui(stdscr):
            # Create and run the TUI
            tui = HyperPodTUI(stdscr)
            tui.run()
        
        curses.wrapper(run_tui)
    except Exception as e:
        import traceback
        print(f"Error starting HyperPod TUI: {e}", file=sys.stderr)
        print(f"Traceback: {traceback.format_exc()}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()