"""Terminal User Interface for HyperPod TUI."""

import curses
import fnmatch
from typing import List, Dict, Any, Optional, Union
from .models import Cluster, InstanceGroup, Instance
from .aws_client import HyperPodClient
from .config import config


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
        self.stdscr = stdscr
        self.title = title
        self.height, self.width = stdscr.getmaxyx()
        self.filter_text = ""
        self.selected_index = 0
        self.scroll_offset = 0
        self.details_height_ratio = config.get('ui.default_details_height', 0.3)
        
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
        except (curses.error, AttributeError):
            # In test mode or if curses is not properly initialized
            pass
    
    def _calculate_dimensions(self):
        """Calculate pane dimensions based on screen size."""
        self.header_height = 1
        self.footer_height = 2
        self.filter_height = 1
        
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
    
    def resize(self):
        """Handle screen resize."""
        self.height, self.width = self.stdscr.getmaxyx()
        self._calculate_dimensions()
    
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
        safe_header = header_text.ljust(self.width)[:self.width - 1]
        try:
            self.stdscr.addstr(self.header_y, 0, safe_header)
        except curses.error:
            pass  # Skip if we can't draw the header
        self.stdscr.attroff(safe_color_pair(1) | safe_attr("A_BOLD"))
    
    def draw_footer(self):
        """Draw the footer with key bindings."""
        self.stdscr.attron(safe_color_pair(1))
        footer_lines = [
            " q:Quit  Enter:Select  Backspace:Back  {}:Shrink  {}:Expand  r:Refresh ".format(
                config.get('key_bindings.shrink_details', ['{'])[0],
                config.get('key_bindings.expand_details', ['}'])[0]
            ),
            " ↑↓:Navigate  PgUp/PgDn:Page  Home/End:First/Last  Del/x:Clear Filter "
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
        """Draw the filter input box."""
        filter_prompt = config.get('ui.filter_prompt', 'Filter: ')
        filter_line = f"{filter_prompt}{self.filter_text}"
        
        self.stdscr.attron(safe_color_pair(3))
        safe_filter = filter_line.ljust(self.width)[:self.width - 1]
        try:
            self.stdscr.addstr(self.filter_y, 0, safe_filter)
        except curses.error:
            pass  # Skip if we can't draw the filter
        self.stdscr.attroff(safe_color_pair(3))
    
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
        # Quit
        if key in config.get('key_bindings.quit', ['q', 'Q']):
            return 'quit'
        
        # Navigation
        elif key in config.get('key_bindings.up', ['KEY_UP', 'k']):
            return 'up'
        elif key in config.get('key_bindings.down', ['KEY_DOWN', 'j']):
            return 'down'
        elif key in config.get('key_bindings.page_up', ['KEY_PPAGE']):
            return 'page_up'
        elif key in config.get('key_bindings.page_down', ['KEY_NPAGE']):
            return 'page_down'
        elif key in config.get('key_bindings.home', ['KEY_HOME']):
            return 'home'
        elif key in config.get('key_bindings.end', ['KEY_END']):
            return 'end'
        
        # Actions
        elif key in config.get('key_bindings.enter', ['\n', '\r']):
            return 'enter'
        elif key in config.get('key_bindings.back', ['\b', 'KEY_BACKSPACE']):
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
        elif key == 'KEY_BACKSPACE' and self.filter_text:
            self.filter_text = self.filter_text[:-1]
            self.selected_index = 0
            self.scroll_offset = 0
            return 'filter_changed'
        elif len(key) == 1 and key.isprintable():
            self.filter_text += key
            self.selected_index = 0
            self.scroll_offset = 0
            return 'filter_changed'
        
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
        safe_hline(self.stdscr, self.list_y, 0, self.width - 1)
        
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
                self.stdscr.addstr(y, 2, message[:self.width - 4])
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
                
                safe_line = cluster_line.ljust(self.width)[:self.width - 1]
                try:
                    self.stdscr.addstr(y, 0, safe_line)
                except curses.error:
                    pass  # Skip if we can't draw this line
                
                if is_selected:
                    self.stdscr.attroff(safe_color_pair(2))
            else:
                try:
                    self.stdscr.addstr(y, 0, " " * (self.width - 1))
                except curses.error:
                    pass
    
    def draw_cluster_details(self):
        """Draw details of the selected cluster."""
        # Draw border
        safe_hline(self.stdscr, self.details_y, 0, self.width - 1)
        
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
            safe_detail = detail_line[:self.width - 3]  # Leave room for the indent
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
            safe_hline(self.stdscr, self.list_y, 0, self.width - 1)
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
                
                safe_line = group_line.ljust(self.width)[:self.width - 1]
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
    
    def draw_instance_group_details(self):
        """Draw details of the selected instance group."""
        safe_hline(self.stdscr, self.details_y, 0, self.width - 1)
        
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
            safe_detail = detail_line[:self.width - 3]  # Leave room for the indent
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