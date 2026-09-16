import json
import os
import re
import sys

# Global paths
CACHE_DIR = "cache_html"


def do_list():
    if not os.path.exists(CACHE_DIR):
        print(f"[ERROR] Directory {CACHE_DIR} was not found.")
        return
    else:
        # Get the list of files and sort them alphabetically for consistency
        files = sorted(os.listdir(CACHE_DIR))

        if not files:
            print(f"Directory {CACHE_DIR} is empty.")
            return

        print(f"Files in {CACHE_DIR} (sorted):")

        # enumerate(..., start=0) provides the numeric index
        # (you can change start to 1 if you prefer to start from 1)
        for index, file in enumerate(files):
            print(f"[{index}] {file}")


if __name__ == "__main__":
    do_list()