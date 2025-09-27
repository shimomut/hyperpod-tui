"""Terminal User Interface for HyperPod TUI."""

import curses
import fnmatch
from typing import List, Dict, Any, Optional, Union
from .models import Cluster, InstanceGroup, Instance
from .aws_client import HyperPodClient
from .config import config


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
        if curses.has_colors():
            curses.start_color()
            curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)    # Header/Footer
            curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)   # Selected
            curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)   # Normal
            curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)     # Error
            curses.init_pair(5, curses.COLOR_GREEN, curses.COLOR_BLACK)   # Info
    
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
        self.stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
        header_text = f" HyperPod TUI - {self.title} "
        self.stdscr.addstr(self.header_y, 0, header_text.ljust(self.width))
        self.stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)
    
    def draw_footer(self):
        """Draw the footer with key bindings."""
        self.stdscr.attron(curses.color_pair(1))
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
                self.stdscr.addstr(y, 0, line.ljust(self.width))
        
        self.stdscr.attroff(curses.color_pair(1))
    
    def draw_filter(self):
        """Draw the filter input box."""
        filter_prompt = config.get('ui.filter_prompt', 'Filter: ')
        filter_line = f"{filter_prompt}{self.filter_text}"
        
        self.stdscr.attron(curses.color_pair(3))
        self.stdscr.addstr(self.filter_y, 0, filter_line.ljust(self.width))
        self.stdscr.attroff(curses.color_pair(3))
    
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
        self.stdscr.hline(self.list_y, 0, curses.ACS_HLINE, self.width)
        
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
                    self.stdscr.attron(curses.color_pair(2))
                
                self.stdscr.addstr(y, 0, cluster_line.ljust(self.width))
                
                if is_selected:
                    self.stdscr.attroff(curses.color_pair(2))
            else:
                self.stdscr.addstr(y, 0, " " * self.width)
    
    def draw_cluster_details(self):
        """Draw details of the selected cluster."""
        # Draw border
        self.stdscr.hline(self.details_y, 0, curses.ACS_HLINE, self.width)
        
        filtered_clusters = self.get_filtered_items(self.clusters)
        if not filtered_clusters or self.selected_index >= len(filtered_clusters):
            return
        
        cluster = filtered_clusters[self.selected_index]
        details = cluster.to_dict()
        
        y = self.details_y + 1
        for key, value in details.items():
            if y >= self.footer_y:
                break
            self.stdscr.addstr(y, 2, f"{key}: {value}")
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
        
        self.stdscr.hline(self.list_y, 0, curses.ACS_HLINE, self.width)
        
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
                    self.stdscr.attron(curses.color_pair(2))
                
                self.stdscr.addstr(y, 0, group_line.ljust(self.width))
                
                if is_selected:
                    self.stdscr.attroff(curses.color_pair(2))
            else:
                self.stdscr.addstr(y, 0, " " * self.width)
    
    def draw_instance_group_details(self):
        """Draw details of the selected instance group."""
        self.stdscr.hline(self.details_y, 0, curses.ACS_HLINE, self.width)
        
        filtered_groups = self.get_filtered_items(self.instance_groups)
        if not filtered_groups or self.selected_index >= len(filtered_groups):
            return
        
        group = filtered_groups[self.selected_index]
        details = group.to_dict()
        
        y = self.details_y + 1
        for key, value in details.items():
            if y >= self.footer_y:
                break
            self.stdscr.addstr(y, 2, f"{key}: {value}")
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
        
        self.stdscr.hline(self.list_y, 0, curses.ACS_HLINE, self.width)
        
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
                    self.stdscr.attron(curses.color_pair(2))
                
                self.stdscr.addstr(y, 0, instance_line.ljust(self.width))
                
                if is_selected:
                    self.stdscr.attroff(curses.color_pair(2))
            else:
                self.stdscr.addstr(y, 0, " " * self.width)
    
    def draw_instance_details(self):
        """Draw details of the selected instance."""
        self.stdscr.hline(self.details_y, 0, curses.ACS_HLINE, self.width)
        
        filtered_instances = self.get_filtered_items(self.instances)
        if not filtered_instances or self.selected_index >= len(filtered_instances):
            return
        
        instance = filtered_instances[self.selected_index]
        details = instance.to_dict()
        
        y = self.details_y + 1
        for key, value in details.items():
            if y >= self.footer_y:
                break
            self.stdscr.addstr(y, 2, f"{key}: {value}")
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