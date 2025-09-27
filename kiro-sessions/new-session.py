#!/usr/bin/env python3
"""
Script to create new Kiro session files with auto-incrementing numbers
Usage: python new-session.py "Topic description"
"""

import os
import sys
from datetime import datetime
from pathlib import Path

def get_next_session_number():
    """Find the next available session number"""
    sessions_dir = Path("kiro-sessions")
    if not sessions_dir.exists():
        sessions_dir.mkdir()
        return 1
    
    existing_files = list(sessions_dir.glob("*.md"))
    numbers = []
    
    for file in existing_files:
        if file.name.startswith("template"):
            continue
        try:
            # Extract number from filename like "0001.md"
            num_str = file.stem
            if num_str.isdigit():
                numbers.append(int(num_str))
        except:
            continue
    
    return max(numbers, default=0) + 1

def create_session_file(topic="New Kiro Session"):
    """Create a new session file with template"""
    session_num = get_next_session_number()
    filename = f"kiro-sessions/{session_num:04d}.md"
    
    template = f"""# Kiro Session {session_num:04d}

**Date:** {datetime.now().strftime('%Y-%m-%d')}  
**Topic:** {topic}  
**Duration:** [To be filled]  

## Summary
[Brief overview of what was accomplished]

## Key Outcomes
- [Main results and decisions]

## Conversation

### User Request
> [Copy the initial user request here]

### Kiro Response
[Summary of Kiro's response and actions]

## Files Created/Modified
- [List files with descriptions]

## Next Steps
- [Action items for follow-up]

## Tags
#kiro-session #{datetime.now().strftime('%Y-%m')}
"""
    
    with open(filename, 'w') as f:
        f.write(template)
    
    print(f"Created session file: {filename}")
    return filename

if __name__ == "__main__":
    topic = sys.argv[1] if len(sys.argv) > 1 else "New Kiro Session"
    create_session_file(topic)