#!/usr/bin/env python
"""
FluidLearn CLI Entry Point

Run from project root in your prepared environment:
    python init.py
"""
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Import and run CLI
from cli import cli

if __name__ == "__main__":
    cli()
