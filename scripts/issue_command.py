#!/usr/bin/env python3
"""
Simple issue command that uses ISSUE.md template to create GitHub issues.

Usage:
    python3 scripts/issue_command.py "feature description here"
"""

import sys
import subprocess
from pathlib import Path


def create_issue_from_template(feature_description: str) -> bool:
    """Create a GitHub issue using the ISSUE.md template."""
    
    # Read the ISSUE.md template
    template_path = Path("ISSUE.md")
    if not template_path.exists():
        print("❌ ISSUE.md template not found!")
        return False
    
    try:
        with open(template_path, 'r') as f:
            template_content = f.read()
        
        # Replace #ARGUMENTS with the actual feature description
        issue_prompt = template_content.replace("#ARGUMENTS", feature_description)
        
        # Write to a temporary file for the AI to process
        temp_file = Path("temp_issue_prompt.md")
        with open(temp_file, 'w') as f:
            f.write(issue_prompt)
        
        print(f"✅ Created issue prompt with feature: '{feature_description}'")
        print(f"📄 Prompt saved to: {temp_file}")
        print(f"\n📋 Next steps:")
        print(f"   1. Use this prompt with an AI assistant")
        print(f"   2. AI will research the repository and create a structured issue")
        print(f"   3. AI will use 'gh issue create' to submit the issue")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating issue prompt: {e}")
        return False
    finally:
        # Clean up temp file if it exists
        if 'temp_file' in locals() and temp_file.exists():
            temp_file.unlink()


def main():
    """Main entry point."""
    if len(sys.argv) != 2:
        print("Usage: python3 scripts/issue_command.py \"feature description\"")
        print("Example: python3 scripts/issue_command.py \"Add Excel formula validation\"")
        sys.exit(1)
    
    feature_description = sys.argv[1].strip()
    
    if not feature_description:
        print("❌ Feature description cannot be empty!")
        sys.exit(1)
    
    print(f"🚀 Creating issue for: {feature_description}")
    
    success = create_issue_from_template(feature_description)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()