"""Terminal User Interface for HyperPod TUI."""

import curses
import fnmatch
import json
import os
from typing import List, Dict, Any, Optional, Union
from .models import Cluster, InstanceGroup, Instance
from .aws_client import HyperPodClient
from .config import config


def setup_esc_delay():
    """
    Set up ESC key delay for responsive ESC key handling.
    
    The ESC key is used to start escape sequences in terminals (like arrow keys).
    By default, terminals wait up to 1000ms to see if ESC is part of a sequence.
    This makes standalone ESC presses feel very slow.
    
    This function sets a much shorter delay for better responsiveness.
    """
    # Get configured ESC delay (default 25ms)
    esc_delay = config.get('ui.esc_delay', 25)
    
    # Set environment variable if not already set
    if 'ESCDELAY' not in os.environ:
        os.environ['ESCDELAY'] = str(esc_delay)
    
    # Set programmatically if available (Python 3.9+)
    try:
        curses.set_escdelay(esc_delay)
    except AttributeError:
        # Older Python versions don't have set_escdelay
        # The environment variable will still work
        pass


def safe_hline(stdscr, y, x, width):
    """Safely draw a horizontal line, handling missing curses constants."""
    try:
        # Use a fallback character if ACS_HLINE is not available
        try:
            hline_char = curses.ACS_HLINE
        except AttributeError:
            hline_char = ord('-')
        stdscr.hline(y, x, hline_char, width)
    except (curses.error, AttributeError):
        pass  # Skip border if we can't draw it


def safe_color_pair(pair_number):
    """Safely get a color pair, handling missing curses initialization."""
    try:
        return curses.color_pair(pair_number)
    except (AttributeError, curses.error):
        return 0  # Return no attributes if color pairs aren't available


def safe_attr(attr_name):
    """Safely get a curses attribute, handling missing curses initialization."""
    try:
        return getattr(curses, attr_name, 0)
    except AttributeError:
        return 0


class TUIScreen:
    """Base class for TUI screens."""
    
    def __init__(self, stdscr, title: str):
        # Set up responsive ESC key handling
        setup_esc_delay()
        
        self.stdscr = stdscr
        self.title = title
        self.height, self.width = stdscr.getmaxyx()
        self.filter_text = ""
        self.selected_index = 0
        self.scroll_offset = 0
        self.details_height_ratio = config.get('ui.default_details_height', 0.3)
        self.search_mode = False  # Track if we're in incremental search mode
        self.caret_position = 0  # Position of caret in search text
        
        # JSON pane state
        self.json_pane_visible = False
        self.json_content = ""
        self.json_scroll_offset = 0
        self.json_lines = []
        self.json_pane_focused = False  # Track which pane has focus
        
        # Calculate pane dimensions
        self._calculate_dimensions()
        
        # Initialize color pairs
        self._init_colors()
    
    def _init_colors(self):
        """Initialize color pairs."""
        try:
            if curses.has_colors():
                curses.start_color()
                curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)    # Header/Footer
                curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)   # Selected
                curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)   # Normal
                curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)     # Error
                curses.init_pair(5, curses.COLOR_GREEN, curses.COLOR_BLACK)   # Info
                curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_BLACK)   # Bright white for search mode
                curses.init_pair(7, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # JSON syntax highlighting
                curses.init_pair(8, curses.COLOR_MAGENTA, curses.COLOR_BLACK) # JSON keys
                curses.init_pair(9, curses.COLOR_BLUE, curses.COLOR_BLACK)    # JSON values
        except (curses.error, AttributeError):
            # In test mode or if curses is not properly initialized
            pass
    
    def _calculate_dimensions(self):
        """Calculate pane dimensions based on screen size."""
        self.header_height = 1
        self.footer_height = 2
        self.filter_height = 1
        
        # Calculate JSON pane width (40% of screen when visible)
        self.json_pane_width = int(self.width * 0.4) if self.json_pane_visible else 0
        self.left_pane_width = self.width - self.json_pane_width
        
        available_height = self.height - self.header_height - self.footer_height - self.filter_height
        self.details_height = max(
            config.get('ui.min_details_height', 3),
            min(
                int(available_height * self.details_height_ratio),
                int(available_height * config.get('ui.max_details_height', 0.8))
            )
        )
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
    
    def resize(self):
        """Handle screen resize."""
        self.height, self.width = self.stdscr.getmaxyx()
        self._calculate_dimensions()
    
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
    
    def set_json_content(self, data: Any):
        """Set the content for the JSON pane."""
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
    
    def draw_json_pane(self):
        """Draw the JSON pane with syntax highlighting."""
        if not self.json_pane_visible:
            return
        
        # Draw vertical border
        for y in range(self.list_y, self.footer_y):
            try:
                self.stdscr.addch(y, self.json_pane_x - 1, '|')
            except curses.error:
                pass
        
        # Draw JSON pane header with focus indicator
        focus_indicator = "*" if self.json_pane_focused else " "
        header_text = f"{focus_indicator}JSON{focus_indicator}"
        try:
            color = safe_color_pair(1) | safe_attr("A_BOLD")
            if self.json_pane_focused:
                color |= safe_attr("A_REVERSE")  # Highlight when focused
            self.stdscr.attron(color)
            self.stdscr.addstr(self.list_y, self.json_pane_x, header_text.ljust(self.json_pane_width)[:self.json_pane_width])
            self.stdscr.attroff(color)
        except curses.error:
            pass
        
        # Draw JSON content
        visible_height = self.json_pane_height - 1  # -1 for header
        start_line = self.json_scroll_offset
        
        for i in range(visible_height):
            y = self.list_y + 1 + i
            line_index = start_line + i
            
            if y >= self.footer_y:
                break
            
            if line_index < len(self.json_lines):
                line = self.json_lines[line_index]
                # Simple syntax highlighting
                self._draw_json_line(y, self.json_pane_x, line)
            else:
                # Clear empty lines
                try:
                    self.stdscr.addstr(y, self.json_pane_x, " " * self.json_pane_width)
                except curses.error:
                    pass
    
    def _draw_json_line(self, y: int, x: int, line: str):
        """Draw a single JSON line with basic syntax highlighting."""
        if not line.strip():
            try:
                self.stdscr.addstr(y, x, " " * self.json_pane_width)
            except curses.error:
                pass
            return
        
        # Truncate line to fit in pane
        display_line = line[:self.json_pane_width]
        
        # Basic syntax highlighting
        try:
            if ':' in display_line and '"' in display_line:
                # Try to highlight JSON key-value pairs
                parts = display_line.split(':', 1)
                if len(parts) == 2:
                    key_part = parts[0]
                    value_part = ':' + parts[1]
                    
                    # Draw key part (usually contains quotes)
                    self.stdscr.attron(safe_color_pair(8))  # Magenta for keys
                    self.stdscr.addstr(y, x, key_part[:self.json_pane_width])
                    self.stdscr.attroff(safe_color_pair(8))
                    
                    # Draw value part
                    remaining_width = self.json_pane_width - len(key_part)
                    if remaining_width > 0:
                        self.stdscr.attron(safe_color_pair(9))  # Blue for values
                        self.stdscr.addstr(y, x + len(key_part), value_part[:remaining_width])
                        self.stdscr.attroff(safe_color_pair(9))
                else:
                    # Fallback to normal color
                    self.stdscr.addstr(y, x, display_line)
            else:
                # Structural characters (brackets, braces)
                if any(char in display_line for char in ['{', '}', '[', ']']):
                    self.stdscr.attron(safe_color_pair(7))  # Yellow for structure
                    self.stdscr.addstr(y, x, display_line)
                    self.stdscr.attroff(safe_color_pair(7))
                else:
                    # Normal text
                    self.stdscr.addstr(y, x, display_line)
            
            # Fill remaining space
            remaining = self.json_pane_width - len(display_line)
            if remaining > 0:
                self.stdscr.addstr(y, x + len(display_line), " " * remaining)
                
        except curses.error:
            # Fallback: just draw the line without highlighting
            try:
                self.stdscr.addstr(y, x, display_line.ljust(self.json_pane_width)[:self.json_pane_width])
            except curses.error:
                pass
    
    def _is_backspace_key(self, key: str) -> bool:
        """Check if the key is a backspace key, handling multiple representations."""
        # Common backspace representations across different terminals and platforms
        backspace_keys = [
            'KEY_BACKSPACE',  # Standard curses backspace
            '\b',             # ASCII backspace (Ctrl+H)
            '\x7f',           # DEL character (common on Unix)
            '\x08',           # Another backspace representation
            '^H',             # Control-H representation
        ]
        
        # Also check the configured backspace keys
        configured_keys = config.get('key_bindings.back', ['\b', 'KEY_BACKSPACE'])
        backspace_keys.extend(configured_keys)
        
        return key in backspace_keys
    
    def adjust_details_height(self, increase: bool):
        """Adjust the height of the details pane."""
        available_height = self.height - self.header_height - self.footer_height - self.filter_height
        min_height = config.get('ui.min_details_height', 3)
        max_height = int(available_height * config.get('ui.max_details_height', 0.8))
        
        if increase:
            self.details_height = min(self.details_height + 2, max_height)
        else:
            self.details_height = max(self.details_height - 2, min_height)
        
        self.list_height = available_height - self.details_height
        self.details_y = self.list_y + self.list_height
        self.details_height_ratio = self.details_height / available_height
    
    def draw_header(self):
        """Draw the header."""
        self.stdscr.attron(safe_color_pair(1) | safe_attr("A_BOLD"))
        header_text = f" HyperPod TUI - {self.title} "
        
        if self.json_pane_visible:
            # Draw header for left pane
            left_header = header_text.ljust(self.left_pane_width)[:self.left_pane_width - 1]
            try:
                self.stdscr.addstr(self.header_y, 0, left_header)
            except curses.error:
                pass
            
            # Draw separator
            try:
                self.stdscr.addch(self.header_y, self.left_pane_width - 1, '|')
            except curses.error:
                pass
            
            # Draw header for JSON pane
            json_header = " JSON View ".ljust(self.json_pane_width)[:self.json_pane_width]
            try:
                self.stdscr.addstr(self.header_y, self.json_pane_x, json_header)
            except curses.error:
                pass
        else:
            # Draw full-width header
            safe_header = header_text.ljust(self.width)[:self.width - 1]
            try:
                self.stdscr.addstr(self.header_y, 0, safe_header)
            except curses.error:
                pass
        
        self.stdscr.attroff(safe_color_pair(1) | safe_attr("A_BOLD"))
    
    def draw_footer(self):
        """Draw the footer with key bindings."""
        self.stdscr.attron(safe_color_pair(1))
        
        if self.search_mode:
            footer_lines = [
                " Search Mode: Type to filter  Enter:Select  ESC:Cancel ",
                " ↑↓:Navigate  ←→:Move caret  Backspace:Delete  Del:Delete at caret "
            ]
        else:
            json_status = "Hide JSON" if self.json_pane_visible else "Show JSON"
            footer_lines = [
                " q:Quit  Enter:Select  Backspace:Back  {}:Shrink  {}:Expand  r:Refresh  TAB:{} ".format(
                    config.get('key_bindings.shrink_details', ['{'])[0],
                    config.get('key_bindings.expand_details', ['}'])[0],
                    json_status
                ),
                " ↑↓:Navigate  PgUp/PgDn:Page  Home/End:First/Last  f:Search  Del/x:Clear Filter "
            ]
        
        for i, line in enumerate(footer_lines):
            y = self.footer_y + i
            if y < self.height:
                # Ensure we don't write to the last column of the last row
                safe_line = line.ljust(self.width)
                if y == self.height - 1:
                    safe_line = safe_line[:self.width - 1]
                try:
                    self.stdscr.addstr(y, 0, safe_line)
                except curses.error:
                    # If we still can't write, try without the last character
                    try:
                        self.stdscr.addstr(y, 0, safe_line[:-1])
                    except curses.error:
                        pass  # Give up on this line
        
        self.stdscr.attroff(safe_color_pair(1))
    
    def draw_filter(self):
        """Draw the filter input box with caret support."""
        if self.search_mode:
            filter_prompt = config.get('ui.search_prompt', 'Filter: ')
            # Use bright white color for search mode
            color_pair = safe_color_pair(6) | safe_attr("A_BOLD")  # Bright white for search mode
        else:
            filter_prompt = config.get('ui.filter_prompt', 'Filter: ')
            color_pair = safe_color_pair(3)  # Normal color
        
        filter_line = f"{filter_prompt}{self.filter_text}"
        if not self.search_mode and not self.filter_text:
            filter_line += " (Press 'f' to search)"
        
        # Calculate available width for filter (left pane only)
        available_width = self.left_pane_width if self.json_pane_visible else self.width
        
        if self.search_mode:
            # In search mode, draw prompt and text with bright white color
            self.stdscr.attron(color_pair)
            
            # Draw the prompt
            try:
                self.stdscr.addstr(self.filter_y, 0, filter_prompt)
            except curses.error:
                pass
            
            # Draw the text with caret
            prompt_len = len(filter_prompt)
            text_start_x = prompt_len
            
            # Ensure caret position is within bounds
            self.caret_position = max(0, min(self.caret_position, len(self.filter_text)))
            
            # Draw text before caret
            if self.caret_position > 0:
                before_caret = self.filter_text[:self.caret_position]
                try:
                    self.stdscr.addstr(self.filter_y, text_start_x, before_caret)
                except curses.error:
                    pass
            
            # Draw caret (character at caret position with inverted colors)
            caret_x = text_start_x + self.caret_position
            if caret_x < available_width - 1:  # Ensure we don't go beyond available width
                if self.caret_position < len(self.filter_text):
                    # Caret is on an existing character - invert it
                    caret_char = self.filter_text[self.caret_position]
                else:
                    # Caret is at the end - show a space with inverted colors
                    caret_char = ' '
                
                # Invert colors for caret - turn off bright white first, then apply inversion
                try:
                    self.stdscr.attroff(color_pair)
                    self.stdscr.attron(safe_color_pair(2))  # Use selected color pair for inversion
                    self.stdscr.addstr(self.filter_y, caret_x, caret_char)
                    self.stdscr.attroff(safe_color_pair(2))
                    self.stdscr.attron(color_pair)  # Restore bright white for remaining text
                except curses.error:
                    pass
            
            # Draw text after caret
            if self.caret_position < len(self.filter_text):
                after_caret = self.filter_text[self.caret_position + 1:]
                after_caret_x = text_start_x + self.caret_position + 1
                if after_caret and after_caret_x < available_width - 1:
                    try:
                        self.stdscr.addstr(self.filter_y, after_caret_x, after_caret)
                    except curses.error:
                        pass
            
            # Fill the rest of the line with normal background
            remaining_start = text_start_x + len(self.filter_text) + (1 if self.caret_position >= len(self.filter_text) else 0)
            if remaining_start < available_width:
                remaining_spaces = " " * (available_width - remaining_start - 1)
                try:
                    self.stdscr.attroff(color_pair)  # Turn off bright white for background
                    self.stdscr.attron(safe_color_pair(3))  # Use normal color for background
                    self.stdscr.addstr(self.filter_y, remaining_start, remaining_spaces)
                    self.stdscr.attroff(safe_color_pair(3))
                except curses.error:
                    pass
            
            self.stdscr.attroff(color_pair)
        else:
            # Normal mode - draw as before
            self.stdscr.attron(color_pair)
            safe_filter = filter_line.ljust(available_width)[:available_width - 1]
            try:
                self.stdscr.addstr(self.filter_y, 0, safe_filter)
            except curses.error:
                pass  # Skip if we can't draw the filter
            self.stdscr.attroff(color_pair)
    
    def get_filtered_items(self, items: List[Any]) -> List[Any]:
        """Filter items based on filter text."""
        if not self.filter_text:
            return items
        
        filtered = []
        for item in items:
            # Get the display name for filtering
            if hasattr(item, 'name'):
                name = item.name
            elif hasattr(item, 'instance_id'):
                name = item.instance_id
            else:
                name = str(item)
            
            if fnmatch.fnmatch(name.lower(), f"*{self.filter_text.lower()}*"):
                filtered.append(item)
        
        return filtered
    
    def handle_key(self, key: str) -> Optional[str]:
        """Handle key input. Returns action or None."""
        # Handle search mode keys first
        if self.search_mode:
            # Enter key - select current item and exit search mode
            if key in config.get('key_bindings.enter', ['\n', '\r']):
                self.search_mode = False
                self.caret_position = 0
                return 'enter'
            
            # Escape key - first clear filter text, then exit search mode
            elif key == '\x1b':  # ESC key
                if self.filter_text:
                    # If there's filter text, clear it first
                    self.filter_text = ""
                    self.caret_position = 0
                    self.selected_index = 0
                    self.scroll_offset = 0
                    return 'filter_changed'
                else:
                    # If filter text is already empty, exit search mode
                    self.search_mode = False
                    self.caret_position = 0
                    return 'search_cancelled'
            
            # Caret movement keys
            elif key in config.get('key_bindings.left', ['KEY_LEFT', 'h']):
                self.caret_position = max(0, self.caret_position - 1)
                return None  # No need to refresh filter
            elif key in config.get('key_bindings.right', ['KEY_RIGHT', 'l']):
                self.caret_position = min(len(self.filter_text), self.caret_position + 1)
                return None  # No need to refresh filter
            
            # Home/End keys for caret positioning
            elif key in config.get('key_bindings.home', ['KEY_HOME']):
                self.caret_position = 0
                return None
            elif key in config.get('key_bindings.end', ['KEY_END']):
                self.caret_position = len(self.filter_text)
                return None
            
            # Navigation keys work even in search mode
            elif key in config.get('key_bindings.up', ['KEY_UP', 'k']):
                return 'up'
            elif key in config.get('key_bindings.down', ['KEY_DOWN', 'j']):
                return 'down'
            
            # Backspace in search mode - delete character before caret
            elif self._is_backspace_key(key) and self.caret_position > 0:
                self.filter_text = (self.filter_text[:self.caret_position - 1] + 
                                  self.filter_text[self.caret_position:])
                self.caret_position -= 1
                self.selected_index = 0
                self.scroll_offset = 0
                return 'filter_changed'
            
            # Delete key - delete character at caret position
            elif key in config.get('key_bindings.delete', ['KEY_DC']):
                if self.caret_position < len(self.filter_text):
                    self.filter_text = (self.filter_text[:self.caret_position] + 
                                      self.filter_text[self.caret_position + 1:])
                    self.selected_index = 0
                    self.scroll_offset = 0
                    return 'filter_changed'
            
            # Add printable characters to search at caret position
            elif len(key) == 1 and key.isprintable():
                self.filter_text = (self.filter_text[:self.caret_position] + 
                                  key + 
                                  self.filter_text[self.caret_position:])
                self.caret_position += 1
                self.selected_index = 0
                self.scroll_offset = 0
                return 'filter_changed'
            
            return None
        
        # Normal mode (not in search)
        # Quit
        if key in config.get('key_bindings.quit', ['q', 'Q']):
            return 'quit'
        
        # Start search mode with 'f' key
        elif key in ['f', 'F']:
            self.search_mode = True
            self.caret_position = len(self.filter_text)  # Position caret at end of existing text
            return 'search_started'
        
        # Navigation - route to appropriate pane based on focus
        elif key in config.get('key_bindings.up', ['KEY_UP', 'k']):
            if self.json_pane_visible and self.json_pane_focused:
                return 'json_up'
            return 'up'
        elif key in config.get('key_bindings.down', ['KEY_DOWN', 'j']):
            if self.json_pane_visible and self.json_pane_focused:
                return 'json_down'
            return 'down'
        elif key in config.get('key_bindings.page_up', ['KEY_PPAGE']):
            if self.json_pane_visible and self.json_pane_focused:
                return 'json_page_up'
            return 'page_up'
        elif key in config.get('key_bindings.page_down', ['KEY_NPAGE']):
            if self.json_pane_visible and self.json_pane_focused:
                return 'json_page_down'
            return 'page_down'
        elif key in config.get('key_bindings.home', ['KEY_HOME']):
            return 'home'
        elif key in config.get('key_bindings.end', ['KEY_END']):
            return 'end'
        
        # Actions
        elif key in config.get('key_bindings.enter', ['\n', '\r']):
            return 'enter'
        elif self._is_backspace_key(key):
            return 'back'
        elif key in config.get('key_bindings.refresh', ['r', 'R', 'KEY_F5']):
            return 'refresh'
        
        # Details pane adjustment
        elif key in config.get('key_bindings.expand_details', ['}']):
            return 'expand_details'
        elif key in config.get('key_bindings.shrink_details', ['{']):
            return 'shrink_details'
        
        # Filter management
        elif key in config.get('key_bindings.clear_filter', ['KEY_DC', 'x']):
            return 'clear_filter'
        
        # JSON pane toggle and focus
        elif key == '\t':  # TAB key
            if self.json_pane_visible:
                # Toggle focus between panes
                self.json_pane_focused = not self.json_pane_focused
                return 'focus_changed'
            else:
                # Open JSON pane
                return 'toggle_json'
        
        return None


class ClusterListScreen(TUIScreen):
    """Screen for listing HyperPod clusters."""
    
    def __init__(self, stdscr, client: HyperPodClient):
        super().__init__(stdscr, "Clusters")
        self.client = client
        self.clusters = []
        self.refresh_data()
    
    def refresh_data(self):
        """Refresh cluster data from AWS."""
        try:
            self.clusters = self.client.list_clusters()
        except Exception as e:
            self.clusters = []
            # In a real app, we'd show an error message
    
    def draw(self):
        """Draw the cluster list screen."""
        self.stdscr.clear()
        
        # Draw components
        self.draw_header()
        self.draw_filter()
        self.draw_cluster_list()
        self.draw_cluster_details()
        self.draw_json_pane()
        self.draw_footer()
        
        self.stdscr.refresh()
    
    def draw_cluster_list(self):
        """Draw the list of clusters."""
        filtered_clusters = self.get_filtered_items(self.clusters)
        
        # Adjust selection if needed
        if filtered_clusters:
            self.selected_index = min(self.selected_index, len(filtered_clusters) - 1)
        else:
            self.selected_index = 0
        
        # Calculate visible range
        visible_count = self.list_height - 1  # -1 for border
        if self.selected_index < self.scroll_offset:
            self.scroll_offset = self.selected_index
        elif self.selected_index >= self.scroll_offset + visible_count:
            self.scroll_offset = self.selected_index - visible_count + 1
        
        # Draw border
        safe_hline(self.stdscr, self.list_y, 0, self.left_pane_width - 1)
        
        # Handle empty cluster list
        if not filtered_clusters:
            y = self.list_y + 1
            if not self.clusters:
                # No clusters at all
                message = "No HyperPod clusters found. Press 'r' to refresh."
                if not self.client.is_connected():
                    message = "Unable to connect to AWS. Check your credentials and try again (r)."
            else:
                # Clusters exist but filtered out
                message = f"No clusters match filter '{self.filter_text}'. Press 'x' to clear filter."
            
            try:
                self.stdscr.addstr(y, 2, message[:self.left_pane_width - 4])
            except curses.error:
                pass
            return
        
        # Draw clusters
        for i in range(visible_count):
            cluster_index = self.scroll_offset + i
            y = self.list_y + 1 + i
            
            if y >= self.details_y:
                break
            
            if cluster_index < len(filtered_clusters):
                cluster = filtered_clusters[cluster_index]
                is_selected = cluster_index == self.selected_index
                
                # Format cluster line
                status_indicator = "●" if cluster.status == "InService" else "○"
                cluster_line = f" {status_indicator} {cluster.name:<30} {cluster.status:<15}"
                
                if is_selected:
                    self.stdscr.attron(safe_color_pair(2))
                
                safe_line = cluster_line.ljust(self.left_pane_width)[:self.left_pane_width - 1]
                try:
                    self.stdscr.addstr(y, 0, safe_line)
                except curses.error:
                    pass  # Skip if we can't draw this line
                
                if is_selected:
                    self.stdscr.attroff(safe_color_pair(2))
            else:
                try:
                    self.stdscr.addstr(y, 0, " " * (self.left_pane_width - 1))
                except curses.error:
                    pass
    
    def draw_cluster_details(self):
        """Draw details of the selected cluster."""
        # Draw border
        safe_hline(self.stdscr, self.details_y, 0, self.left_pane_width - 1)
        
        filtered_clusters = self.get_filtered_items(self.clusters)
        if not filtered_clusters or self.selected_index >= len(filtered_clusters):
            # Show helpful message when no cluster is selected
            y = self.details_y + 1
            if not self.clusters:
                message = "No cluster details available."
            else:
                message = "No cluster selected."
            try:
                self.stdscr.addstr(y, 2, message)
            except curses.error:
                pass
            return
        
        cluster = filtered_clusters[self.selected_index]
        details = cluster.to_dict()
        
        y = self.details_y + 1
        for key, value in details.items():
            if y >= self.footer_y:
                break
            detail_line = f"{key}: {value}"
            safe_detail = detail_line[:self.left_pane_width - 3]  # Leave room for the indent
            try:
                self.stdscr.addstr(y, 2, safe_detail)
            except curses.error:
                pass  # Skip if we can't draw this line
            y += 1
    
    def get_selected_cluster(self) -> Optional[Cluster]:
        """Get the currently selected cluster."""
        filtered_clusters = self.get_filtered_items(self.clusters)
        if filtered_clusters and self.selected_index < len(filtered_clusters):
            return filtered_clusters[self.selected_index]
        return None
    
    def navigate(self, direction: str):
        """Handle navigation."""
        filtered_clusters = self.get_filtered_items(self.clusters)
        if not filtered_clusters:
            return
        
        if direction == 'up':
            self.selected_index = max(0, self.selected_index - 1)
        elif direction == 'down':
            self.selected_index = min(len(filtered_clusters) - 1, self.selected_index + 1)
        elif direction == 'page_up':
            self.selected_index = max(0, self.selected_index - (self.list_height - 1))
        elif direction == 'page_down':
            self.selected_index = min(len(filtered_clusters) - 1, 
                                    self.selected_index + (self.list_height - 1))
        elif direction == 'home':
            self.selected_index = 0
        elif direction == 'end':
            self.selected_index = len(filtered_clusters) - 1
        
        # Update JSON content when selection changes
        self._update_json_content()
    
    def _update_json_content(self):
        """Update JSON pane content with selected cluster data."""
        if self.json_pane_visible:
            cluster = self.get_selected_cluster()
            if cluster:
                self.set_json_content(cluster.to_dict())
            else:
                self.set_json_content({"message": "No cluster selected"})


class InstanceGroupListScreen(TUIScreen):
    """Screen for listing instance groups in a cluster."""
    
    def __init__(self, stdscr, cluster: Cluster):
        super().__init__(stdscr, f"Instance Groups - {cluster.name}")
        self.cluster = cluster
        self.instance_groups = cluster.instance_groups
    
    def draw(self):
        """Draw the instance group list screen."""
        self.stdscr.clear()
        
        self.draw_header()
        self.draw_filter()
        self.draw_instance_group_list()
        self.draw_instance_group_details()
        self.draw_json_pane()
        self.draw_footer()
        
        self.stdscr.refresh()
    
    def draw_instance_group_list(self):
        """Draw the list of instance groups."""
        filtered_groups = self.get_filtered_items(self.instance_groups)
        
        if filtered_groups:
            self.selected_index = min(self.selected_index, len(filtered_groups) - 1)
        else:
            self.selected_index = 0
        
        visible_count = self.list_height - 1
        if self.selected_index < self.scroll_offset:
            self.scroll_offset = self.selected_index
        elif self.selected_index >= self.scroll_offset + visible_count:
            self.scroll_offset = self.selected_index - visible_count + 1
        
        try:
            safe_hline(self.stdscr, self.list_y, 0, self.left_pane_width - 1)
        except curses.error:
            pass  # Skip border if we can't draw it
        
        for i in range(visible_count):
            group_index = self.scroll_offset + i
            y = self.list_y + 1 + i
            
            if y >= self.details_y:
                break
            
            if group_index < len(filtered_groups):
                group = filtered_groups[group_index]
                is_selected = group_index == self.selected_index
                
                status_indicator = "●" if group.status == "InService" else "○"
                group_line = f" {status_indicator} {group.name:<25} {group.instance_type:<20} {group.current_count}/{group.target_count}"
                
                if is_selected:
                    self.stdscr.attron(safe_color_pair(2))
                
                safe_line = group_line.ljust(self.left_pane_width)[:self.left_pane_width - 1]
                try:
                    self.stdscr.addstr(y, 0, safe_line)
                except curses.error:
                    pass  # Skip if we can't draw this line
                
                if is_selected:
                    self.stdscr.attroff(safe_color_pair(2))
            else:
                safe_empty = " " * (self.left_pane_width - 1)
                try:
                    self.stdscr.addstr(y, 0, safe_empty)
                except curses.error:
                    pass  # Skip if we can't draw this line
    
    def draw_instance_group_details(self):
        """Draw details of the selected instance group."""
        safe_hline(self.stdscr, self.details_y, 0, self.left_pane_width - 1)
        
        filtered_groups = self.get_filtered_items(self.instance_groups)
        if not filtered_groups or self.selected_index >= len(filtered_groups):
            return
        
        group = filtered_groups[self.selected_index]
        details = group.to_dict()
        
        y = self.details_y + 1
        for key, value in details.items():
            if y >= self.footer_y:
                break
            detail_line = f"{key}: {value}"
            safe_detail = detail_line[:self.left_pane_width - 3]  # Leave room for the indent
            try:
                self.stdscr.addstr(y, 2, safe_detail)
            except curses.error:
                pass  # Skip if we can't draw this line
            y += 1
    
    def get_selected_instance_group(self) -> Optional[InstanceGroup]:
        """Get the currently selected instance group."""
        filtered_groups = self.get_filtered_items(self.instance_groups)
        if filtered_groups and self.selected_index < len(filtered_groups):
            return filtered_groups[self.selected_index]
        return None
    
    def navigate(self, direction: str):
        """Handle navigation."""
        filtered_groups = self.get_filtered_items(self.instance_groups)
        if not filtered_groups:
            return
        
        if direction == 'up':
            self.selected_index = max(0, self.selected_index - 1)
        elif direction == 'down':
            self.selected_index = min(len(filtered_groups) - 1, self.selected_index + 1)
        elif direction == 'page_up':
            self.selected_index = max(0, self.selected_index - (self.list_height - 1))
        elif direction == 'page_down':
            self.selected_index = min(len(filtered_groups) - 1, 
                                    self.selected_index + (self.list_height - 1))
        elif direction == 'home':
            self.selected_index = 0
        elif direction == 'end':
            self.selected_index = len(filtered_groups) - 1
        
        # Update JSON content when selection changes
        self._update_json_content()
    
    def _update_json_content(self):
        """Update JSON pane content with selected instance group data."""
        if self.json_pane_visible:
            group = self.get_selected_instance_group()
            if group:
                self.set_json_content(group.to_dict())
            else:
                self.set_json_content({"message": "No instance group selected"})


class InstanceListScreen(TUIScreen):
    """Screen for listing instances in an instance group."""
    
    def __init__(self, stdscr, instance_group: InstanceGroup):
        super().__init__(stdscr, f"Instances - {instance_group.name}")
        self.instance_group = instance_group
        self.instances = instance_group.instances
    
    def draw(self):
        """Draw the instance list screen."""
        self.stdscr.clear()
        
        self.draw_header()
        self.draw_filter()
        self.draw_instance_list()
        self.draw_instance_details()
        self.draw_footer()
        
        self.stdscr.refresh()
    
    def draw_instance_list(self):
        """Draw the list of instances."""
        filtered_instances = self.get_filtered_items(self.instances)
        
        if filtered_instances:
            self.selected_index = min(self.selected_index, len(filtered_instances) - 1)
        else:
            self.selected_index = 0
        
        visible_count = self.list_height - 1
        if self.selected_index < self.scroll_offset:
            self.scroll_offset = self.selected_index
        elif self.selected_index >= self.scroll_offset + visible_count:
            self.scroll_offset = self.selected_index - visible_count + 1
        
        try:
            safe_hline(self.stdscr, self.list_y, 0, self.width - 1)
        except curses.error:
            pass  # Skip border if we can't draw it
        
        for i in range(visible_count):
            instance_index = self.scroll_offset + i
            y = self.list_y + 1 + i
            
            if y >= self.details_y:
                break
            
            if instance_index < len(filtered_instances):
                instance = filtered_instances[instance_index]
                is_selected = instance_index == self.selected_index
                
                status_indicator = "●" if instance.status == "InService" else "○"
                instance_line = f" {status_indicator} {instance.instance_id:<20} {instance.instance_type:<20} {instance.status:<15}"
                
                if is_selected:
                    self.stdscr.attron(safe_color_pair(2))
                
                safe_line = instance_line.ljust(self.width)[:self.width - 1]
                try:
                    self.stdscr.addstr(y, 0, safe_line)
                except curses.error:
                    pass  # Skip if we can't draw this line
                
                if is_selected:
                    self.stdscr.attroff(safe_color_pair(2))
            else:
                safe_empty = " " * (self.width - 1)
                try:
                    self.stdscr.addstr(y, 0, safe_empty)
                except curses.error:
                    pass  # Skip if we can't draw this line
    
    def draw_instance_details(self):
        """Draw details of the selected instance."""
        safe_hline(self.stdscr, self.details_y, 0, self.width - 1)
        
        filtered_instances = self.get_filtered_items(self.instances)
        if not filtered_instances or self.selected_index >= len(filtered_instances):
            return
        
        instance = filtered_instances[self.selected_index]
        details = instance.to_dict()
        
        y = self.details_y + 1
        for key, value in details.items():
            if y >= self.footer_y:
                break
            detail_line = f"{key}: {value}"
            safe_detail = detail_line[:self.width - 3]  # Leave room for the indent
            try:
                self.stdscr.addstr(y, 2, safe_detail)
            except curses.error:
                pass  # Skip if we can't draw this line
            y += 1
    
    def navigate(self, direction: str):
        """Handle navigation."""
        filtered_instances = self.get_filtered_items(self.instances)
        if not filtered_instances:
            return
        
        if direction == 'up':
            self.selected_index = max(0, self.selected_index - 1)
        elif direction == 'down':
            self.selected_index = min(len(filtered_instances) - 1, self.selected_index + 1)
        elif direction == 'page_up':
            self.selected_index = max(0, self.selected_index - (self.list_height - 1))
        elif direction == 'page_down':
            self.selected_index = min(len(filtered_instances) - 1, 
                                    self.selected_index + (self.list_height - 1))
        elif direction == 'home':
            self.selected_index = 0
        elif direction == 'end':
            self.selected_index = len(filtered_instances) - 1