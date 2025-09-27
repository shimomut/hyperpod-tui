#!/usr/bin/env python3
"""Demo script to test backspace functionality interactively."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from hyperpod_tui.main import main


def run_backspace_demo():
    """Run interactive demo of backspace functionality."""
    print("Backspace Functionality Demo")
    print("=" * 40)
    print()
    print("This demo will test backspace in both modes:")
    print("1. Search mode backspace (deleting characters)")
    print("2. Navigation backspace (going back/up)")
    print()
    print("Test sequences:")
    print("- 'f test<BACKSPACE><BACKSPACE>q' - Search mode backspace")
    print("- '<BACKSPACE>q' - Navigation backspace")
    print()
    
    # Test search mode backspace
    print("Testing search mode backspace...")
    test_sequences = [
        "f test\x7fq",  # f, test, DEL, q
        "f hello\bq",   # f, hello, backspace, q  
        "f world\x08q", # f, world, ctrl-h, q
    ]
    
    for i, seq in enumerate(test_sequences, 1):
        print(f"Running test {i}: Search mode with backspace...")
        try:
            # Override sys.argv to pass the test sequence
            original_argv = sys.argv[:]
            sys.argv = ['test_backspace_demo.py', '--test-key-seq', seq, '--verbose']
            
            # Run the main function
            main()
            print(f"✓ Test {i} completed successfully")
            
        except SystemExit as e:
            if e.code == 0:
                print(f"✓ Test {i} completed successfully")
            else:
                print(f"✗ Test {i} failed with exit code {e.code}")
        except Exception as e:
            print(f"✗ Test {i} failed with error: {e}")
        finally:
            sys.argv = original_argv
        
        print()
    
    # Test navigation backspace
    print("Testing navigation backspace...")
    nav_sequences = [
        "\x7fq",  # DEL, q
        "\bq",    # backspace, q
        "\x08q",  # ctrl-h, q
    ]
    
    for i, seq in enumerate(nav_sequences, 1):
        print(f"Running navigation test {i}: Backspace for going back...")
        try:
            original_argv = sys.argv[:]
            sys.argv = ['test_backspace_demo.py', '--test-key-seq', seq, '--verbose']
            
            main()
            print(f"✓ Navigation test {i} completed successfully")
            
        except SystemExit as e:
            if e.code == 0:
                print(f"✓ Navigation test {i} completed successfully")
            else:
                print(f"✗ Navigation test {i} failed with exit code {e.code}")
        except Exception as e:
            print(f"✗ Navigation test {i} failed with error: {e}")
        finally:
            sys.argv = original_argv
        
        print()
    
    print("Demo completed!")
    print()
    print("Manual testing instructions:")
    print("1. Run: python run.py")
    print("2. Press 'f' to enter search mode")
    print("3. Type some text (e.g., 'test')")
    print("4. Press backspace to delete characters")
    print("5. Press ESC to exit search mode")
    print("6. Press backspace to go back/up a level")


if __name__ == "__main__":
    run_backspace_demo()