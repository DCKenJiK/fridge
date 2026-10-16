#!/usr/bin/env python3
"""Hermes tool wrapper for fridge CLI."""
import sys
import subprocess


def main():
    if len(sys.argv) < 2:
        print("Usage: hermes_tool.py <command> [args...]")
        print("Commands: add, list, eat, brainstorm, history, search, update, remove")
        sys.exit(1)

    cmd = sys.argv[1]
    result = subprocess.run(['fridge', cmd, *sys.argv[2:]], capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Error: {result.stderr.strip()}")
        sys.exit(1)

    print(result.stdout.strip())


if __name__ == '__main__':
    main()
