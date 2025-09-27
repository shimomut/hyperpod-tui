# JSON Pane Feature Implementation

## Overview

The JSON pane feature adds a third pane to the hyperpod-tui application that displays the raw JSON data of the currently selected resource (cluster, instance group, or instance). This provides users with a detailed view of all available data in a structured format.

## Features

### Core Functionality
- **Toggle Visibility**: Press TAB to show/hide the JSON pane
- **Focus Management**: When JSON pane is visible, TAB switches focus between the main panes and JSON pane
- **Automatic Content Update**: JSON content updates automatically when selection changes
- **Syntax Highlighting**: Basic JSON syntax highlighting with different colors for keys, values, and structure
- **Scrolling Support**: Full scrolling support with Up/Down and PageUp/PageDown keys when JSON pane is focused

### Layout Changes
- **Three-Pane Layout**: When JSON pane is visible, the screen splits into:
  - Left pane (60% width): Resource list and details
  - Right pane (40% width): JSON viewer
- **Dynamic Resizing**: All existing panes automatically adjust their width when JSON pane is toggled
- **Focus Indicators**: Visual indicators show which pane currently has focus

## Key Bindings

| Key | Action |
|-----|--------|
| TAB | Toggle JSON pane visibility / Switch focus between panes |
| ↑/↓ | Navigate in focused pane (list navigation or JSON scrolling) |
| PgUp/PgDn | Page navigation in focused pane |
| q | Quit application |
| f | Enter search mode |
| ESC | Exit search mode |

## Implementation Details

### New Classes and Methods

#### TUIScreen Base Class Extensions
- `json_pane_visible`: Boolean flag for JSON pane visibility
- `json_pane_focused`: Boolean flag for JSON pane focus state
- `json_content`: String containing formatted JSON
- `json_lines`: List of JSON lines for scrolling
- `json_scroll_offset`: Current scroll position in JSON pane

#### New Methods
- `toggle_json_pane()`: Toggle JSON pane visibility and focus
- `set_json_content(data)`: Format and set JSON content from Python objects
- `scroll_json(direction)`: Handle JSON pane scrolling
- `draw_json_pane()`: Render the JSON pane with syntax highlighting
- `_draw_json_line()`: Draw individual JSON lines with basic syntax highlighting

### Layout Calculations
- `left_pane_width`: Calculated as `width - json_pane_width`
- `json_pane_width`: 40% of screen width when visible, 0 when hidden
- `json_pane_x`: X position of JSON pane (left_pane_width)

### Focus Management
When JSON pane is visible:
1. First TAB press opens JSON pane and focuses it
2. Subsequent TAB presses toggle focus between main panes and JSON pane
3. Navigation keys (↑/↓/PgUp/PgDn) operate on the focused pane

### Syntax Highlighting
Basic JSON syntax highlighting using curses color pairs:
- **Keys**: Magenta color for JSON property names
- **Values**: Blue color for JSON values
- **Structure**: Yellow color for brackets and braces `{`, `}`, `[`, `]`
- **Focus Indicator**: Reverse video for JSON pane header when focused

## Screen Updates

### ClusterListScreen
- Updated to support JSON pane in `draw()` method
- Added `_update_json_content()` method to refresh JSON when selection changes
- Navigation methods updated to call `_update_json_content()`

### InstanceGroupListScreen  
- Updated to support JSON pane in `draw()` method
- Added `_update_json_content()` method for instance group data
- Navigation methods updated to refresh JSON content

### Layout Adjustments
All drawing methods updated to use `left_pane_width` instead of full `width`:
- List drawing methods
- Details drawing methods  
- Filter drawing method
- Header drawing method (shows separate headers for each pane)

## Configuration

### Key Bindings
Added to `config.py`:
```python
"toggle_json": ["\t"]  # TAB key for JSON pane toggle
```

### Color Pairs
New color pairs added for JSON syntax highlighting:
- Color pair 7: Yellow for JSON structure
- Color pair 8: Magenta for JSON keys  
- Color pair 9: Blue for JSON values

## Testing

### Test Files
- `test_json_simple.py`: Unit tests for JSON pane functionality without curses
- `test_json_pane.py`: Interactive test with mock data for full TUI testing

### Test Coverage
- JSON pane toggle functionality
- Focus management between panes
- Content formatting and display
- Scrolling behavior
- Layout calculations
- Key binding handling

## Usage Examples

### Basic Usage
1. Start the application and navigate to any resource list
2. Press TAB to open the JSON pane - it will show the JSON data for the selected resource
3. Use ↑/↓ keys to scroll through the JSON content
4. Press TAB again to switch focus back to the main panes
5. Press TAB once more to close the JSON pane

### Advanced Navigation
- When JSON pane is focused (indicated by `*JSON*` header):
  - ↑/↓: Scroll JSON content line by line
  - PgUp/PgDn: Scroll JSON content page by page
- When main panes are focused:
  - ↑/↓: Navigate through resource list
  - PgUp/PgDn: Page through resource list

## Future Enhancements

### Potential Improvements
1. **Enhanced Syntax Highlighting**: More sophisticated JSON syntax highlighting
2. **JSON Path Display**: Show current JSON path/location
3. **Search in JSON**: Add search functionality within JSON content
4. **Copy to Clipboard**: Allow copying JSON content or selections
5. **JSON Formatting Options**: Toggle between compact and pretty-printed JSON
6. **Collapsible Sections**: Fold/unfold JSON objects and arrays
7. **Configurable Width**: Allow users to adjust JSON pane width

### Performance Optimizations
1. **Lazy Loading**: Only format JSON when pane is visible
2. **Virtual Scrolling**: For very large JSON documents
3. **Caching**: Cache formatted JSON to avoid re-formatting

## Error Handling

### JSON Formatting Errors
- If JSON formatting fails, displays error message in JSON pane
- Graceful fallback to string representation for non-serializable objects
- Uses `default=str` parameter in `json.dumps()` for robust serialization

### Layout Edge Cases
- Handles very narrow terminal windows gracefully
- Minimum width constraints prevent layout issues
- Proper bounds checking for scroll operations

## Compatibility

### Terminal Support
- Works with all terminals that support curses
- Color support is optional - falls back to monochrome if colors unavailable
- Handles missing curses constants gracefully

### Platform Support
- Cross-platform compatible (macOS, Linux, Windows with appropriate curses support)
- No platform-specific dependencies introduced