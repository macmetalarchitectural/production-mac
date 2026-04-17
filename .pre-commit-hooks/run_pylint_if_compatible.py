#!/usr/bin/env python
import sys
import subprocess
import re

MAX_VERSION = (3, 11)
MIN_SCORE = 7.5

# ✅ Compare major.minor
current_version = sys.version_info[:2]

if current_version <= MAX_VERSION:
    # Build command: start with pylint, add args from command line
    command = ["pylint"] + sys.argv[1:]

    print("[INFO] Running:", " ".join(command))
    result = subprocess.run(command, capture_output=True, text=True)

    # Print pylint output
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)

    # Extract score from output
    score_match = re.search(r"Your code has been rated at ([\d.]+)/10", result.stdout)
    score = float(score_match.group(1)) if score_match else None

    # Pylint exit codes (bitmask):
    # 1=fatal, 2=error, 4=warning, 8=refactor, 16=convention, 32=usage error
    # Only fail on fatal (1) or error (2) messages, allow warnings/conventions
    if result.returncode & 3:  # Check if bit 0 or bit 1 is set (fatal or error)
        print(f"[ERROR] Pylint found fatal or error messages")
        sys.exit(result.returncode)

    # Check minimum score
    if score is not None:
        print(f"[INFO] Code quality score: {score}/10 (minimum required: {MIN_SCORE})")
        if score < MIN_SCORE:
            print(f"[ERROR] Code quality score {score} is below minimum threshold {MIN_SCORE}")
            sys.exit(1)
    else:
        print("[WARNING] Could not extract quality score from pylint output")

    # All checks passed
    sys.exit(0)
else:
    print(f"[WARNING] Skipping pylint: Python {current_version[0]}.{current_version[1]} > {MAX_VERSION[0]}.{MAX_VERSION[1]}")
    sys.exit(0)
