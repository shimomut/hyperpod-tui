"""Test framework for automated TUI testing with keyboard input simulation."""

import curses
import time
from typing import List, Optional, Callable, Any
from dataclasses import dataclass
from enum import Enum
from unittest.mock import patch


class TestResult(Enum):
    """Test result status."""
    PASS = "PASS"
    FAIL = "FAIL"
    SKIP = "SKIP"
    ERROR = "ERROR"


@dataclass
class TestStep:
    """A single test step with key input and optional validation."""
    keys: str
    description: str
    delay_ms: int = 100
    validator: Optional[Callable] = None
    expected_screen: Optional[str] = None


@dataclass
class TestCase:
    """A complete test case with multiple steps."""
    name: str
    description: str
    steps: List[TestStep]
    setup: Optional[Callable] = None
    teardown: Optional[Callable] = None


@dataclass
class TestReport:
    """Test execution report."""
    test_name: str
    result: TestResult
    duration_ms: int
    error_message: Optional[str] = None
    steps_executed: int = 0
    total_steps: int = 0


class KeySequenceSimulator:
    """Simulates keyboard input for TUI testing."""
    
    def __init__(self, key_sequence: str, delay_ms: int = 100):
        self.keys = self._parse_key_sequence(key_sequence)
        self.delay_ms = delay_ms
        self.current_index = 0
    
    def _parse_key_sequence(self, sequence: str) -> List[str]:
        """Parse key sequence string into individual keys."""
        keys = []
        i = 0
        while i < len(sequence):
            if sequence[i] == '<' and '>' in sequence[i:]:
                # Special key like <ENTER>, <UP>, <DOWN>, etc.
                end = sequence.find('>', i)
                special_key = sequence[i+1:end]
                keys.append(self._map_special_key(special_key))
                i = end + 1
            elif sequence[i] == '\\' and i + 1 < len(sequence):
                # Escaped character
                next_char = sequence[i + 1]
                if next_char == 'n':
                    keys.append('\n')
                elif next_char == 't':
                    keys.append('\t')
                elif next_char == 'r':
                    keys.append('\r')
                elif next_char == '\\':
                    keys.append('\\')
                else:
                    keys.append(next_char)
                i += 2
            else:
                # Regular character
                keys.append(sequence[i])
                i += 1
        return keys
    
    def _map_special_key(self, key_name: str) -> str:
        """Map special key names to curses key constants."""
        key_map = {
            'ENTER': '\n',
            'RETURN': '\r',
            'TAB': '\t',
            'SPACE': ' ',
            'ESC': '\x1b',
            'BACKSPACE': 'KEY_BACKSPACE',
            'DELETE': 'KEY_DC',
            'UP': 'KEY_UP',
            'DOWN': 'KEY_DOWN',
            'LEFT': 'KEY_LEFT',
            'RIGHT': 'KEY_RIGHT',
            'HOME': 'KEY_HOME',
            'END': 'KEY_END',
            'PAGEUP': 'KEY_PPAGE',
            'PAGEDOWN': 'KEY_NPAGE',
            'F1': 'KEY_F1',
            'F2': 'KEY_F2',
            'F3': 'KEY_F3',
            'F4': 'KEY_F4',
            'F5': 'KEY_F5',
            'F6': 'KEY_F6',
            'F7': 'KEY_F7',
            'F8': 'KEY_F8',
            'F9': 'KEY_F9',
            'F10': 'KEY_F10',
            'F11': 'KEY_F11',
            'F12': 'KEY_F12',
        }
        return key_map.get(key_name.upper(), key_name)
    
    def has_next(self) -> bool:
        """Check if there are more keys to simulate."""
        return self.current_index < len(self.keys)
    
    def get_next_key(self) -> Optional[str]:
        """Get the next key in the sequence."""
        if self.has_next():
            key = self.keys[self.current_index]
            self.current_index += 1
            return key
        return None
    
    def reset(self):
        """Reset the simulator to the beginning."""
        self.current_index = 0


class MockStdscr:
    """Mock stdscr for testing that captures key inputs."""
    
    def __init__(self, simulator: KeySequenceSimulator):
        self.simulator = simulator
        self.height = 24
        self.width = 80
        self.timeout_ms = 100
        self.keypad_enabled = False
        self.cursor_visible = True
        self.output_buffer = []
        self.last_key_time = 0
        
        # Add curses constants that might be used
        self._add_curses_constants()
    
    def getmaxyx(self):
        """Get screen dimensions."""
        return self.height, self.width
    
    def getkey(self):
        """Get next key from simulator."""
        if not self.simulator.has_next():
            # Simulate timeout
            time.sleep(self.timeout_ms / 1000.0)
            raise curses.error("timeout")
        
        # Add delay between keys
        current_time = time.time() * 1000
        if current_time - self.last_key_time < self.simulator.delay_ms:
            time.sleep((self.simulator.delay_ms - (current_time - self.last_key_time)) / 1000.0)
        
        key = self.simulator.get_next_key()
        self.last_key_time = time.time() * 1000
        return key
    
    def timeout(self, ms):
        """Set timeout for getkey."""
        self.timeout_ms = ms
    
    def keypad(self, enable):
        """Enable/disable keypad."""
        self.keypad_enabled = enable
    
    def clear(self):
        """Clear screen."""
        self.output_buffer.append("CLEAR")
        return 0
    
    def refresh(self):
        """Refresh screen."""
        self.output_buffer.append("REFRESH")
        return 0
    
    def addstr(self, y, x, text, attr=0):
        """Add string to screen."""
        self.output_buffer.append(f"ADDSTR({y},{x}): {text}")
        return 0
    
    def hline(self, y, x, ch, n):
        """Draw horizontal line."""
        self.output_buffer.append(f"HLINE({y},{x}): {n} chars")
        return 0
    
    def attron(self, attr):
        """Turn on attribute."""
        self.output_buffer.append(f"ATTRON: {attr}")
        return 0
    
    def attroff(self, attr):
        """Turn off attribute."""
        self.output_buffer.append(f"ATTROFF: {attr}")
        return 0
    
    def color_pair(self, pair_number):
        """Mock color pair function."""
        return pair_number
    
    def _add_curses_constants(self):
        """Add curses constants that might be referenced."""
        # Add common curses constants as attributes
        import curses
        try:
            self.ACS_HLINE = curses.ACS_HLINE
            self.A_BOLD = curses.A_BOLD
            self.COLOR_CYAN = curses.COLOR_CYAN
            self.COLOR_BLACK = curses.COLOR_BLACK
            self.COLOR_WHITE = curses.COLOR_WHITE
            self.COLOR_RED = curses.COLOR_RED
            self.COLOR_GREEN = curses.COLOR_GREEN
        except AttributeError:
            # Fallback values if curses constants aren't available
            self.ACS_HLINE = ord('-')
            self.A_BOLD = 1
            self.COLOR_CYAN = 6
            self.COLOR_BLACK = 0
            self.COLOR_WHITE = 7
            self.COLOR_RED = 1
            self.COLOR_GREEN = 2


class TUITestRunner:
    """Test runner for TUI applications."""
    
    def __init__(self, app_class, verbose: bool = False):
        self.app_class = app_class
        self.verbose = verbose
        self.test_cases: List[TestCase] = []
        self.reports: List[TestReport] = []
    
    def add_test_case(self, test_case: TestCase):
        """Add a test case to the runner."""
        self.test_cases.append(test_case)
    
    def run_test_case(self, test_case: TestCase) -> TestReport:
        """Run a single test case."""
        start_time = time.time() * 1000
        
        if self.verbose:
            print(f"Running test: {test_case.name}")
            print(f"Description: {test_case.description}")
        
        try:
            # Setup
            if test_case.setup:
                test_case.setup()
            
            # Create key sequence from all steps
            key_sequence = ""
            for step in test_case.steps:
                key_sequence += step.keys
            
            # Create simulator and mock screen
            simulator = KeySequenceSimulator(key_sequence)
            mock_stdscr = MockStdscr(simulator)
            
            # Mock curses functions that might cause issues
            with patch('curses.curs_set', return_value=0), \
                 patch('curses.has_colors', return_value=True), \
                 patch('curses.start_color', return_value=None), \
                 patch('curses.init_pair', return_value=None), \
                 patch('curses.color_pair', side_effect=lambda x: x):
                
                # Run the application
                app = self.app_class(mock_stdscr, test_mode=True)
                
                # Execute steps
                steps_executed = 0
                for i, step in enumerate(test_case.steps):
                    if self.verbose:
                        print(f"  Step {i+1}: {step.description}")
                    
                    # Let the app process the keys for this step
                    step_keys = KeySequenceSimulator(step.keys)
                    while step_keys.has_next():
                        try:
                            key = mock_stdscr.getkey()
                            if not app.handle_input(key):
                                # App requested quit
                                break
                        except curses.error:
                            # Timeout or other error
                            break
                    
                    # Run validator if provided
                    if step.validator:
                        if not step.validator(app, mock_stdscr):
                            raise AssertionError(f"Validation failed for step: {step.description}")
                    
                    steps_executed += 1
                    
                    # Add delay between steps
                    if step.delay_ms > 0:
                        time.sleep(step.delay_ms / 1000.0)
            
            # Teardown
            if test_case.teardown:
                test_case.teardown()
            
            end_time = time.time() * 1000
            duration = int(end_time - start_time)
            
            return TestReport(
                test_name=test_case.name,
                result=TestResult.PASS,
                duration_ms=duration,
                steps_executed=steps_executed,
                total_steps=len(test_case.steps)
            )
            
        except Exception as e:
            end_time = time.time() * 1000
            duration = int(end_time - start_time)
            
            return TestReport(
                test_name=test_case.name,
                result=TestResult.ERROR,
                duration_ms=duration,
                error_message=str(e),
                steps_executed=steps_executed,
                total_steps=len(test_case.steps)
            )
    
    def run_all_tests(self) -> List[TestReport]:
        """Run all test cases."""
        self.reports = []
        
        for test_case in self.test_cases:
            report = self.run_test_case(test_case)
            self.reports.append(report)
            
            if self.verbose:
                print(f"  Result: {report.result.value} ({report.duration_ms}ms)")
                if report.error_message:
                    print(f"  Error: {report.error_message}")
                print()
        
        return self.reports
    
    def print_summary(self):
        """Print test summary."""
        if not self.reports:
            print("No tests executed.")
            return
        
        total_tests = len(self.reports)
        passed = sum(1 for r in self.reports if r.result == TestResult.PASS)
        failed = sum(1 for r in self.reports if r.result == TestResult.FAIL)
        errors = sum(1 for r in self.reports if r.result == TestResult.ERROR)
        skipped = sum(1 for r in self.reports if r.result == TestResult.SKIP)
        
        total_duration = sum(r.duration_ms for r in self.reports)
        
        print("=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"Total tests: {total_tests}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Errors: {errors}")
        print(f"Skipped: {skipped}")
        print(f"Total duration: {total_duration}ms")
        print()
        
        if failed > 0 or errors > 0:
            print("FAILED TESTS:")
            for report in self.reports:
                if report.result in [TestResult.FAIL, TestResult.ERROR]:
                    print(f"  {report.test_name}: {report.result.value}")
                    if report.error_message:
                        print(f"    {report.error_message}")
            print()
        
        success_rate = (passed / total_tests) * 100 if total_tests > 0 else 0
        print(f"Success rate: {success_rate:.1f}%")