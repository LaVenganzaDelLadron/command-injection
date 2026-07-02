import os
import sys

import requests
import subprocess

def help():
    print("""
    Usage: python3 main.py [options]
        -l      --listen
        -c      --connect
    """)

def sender():
    print()

def receiver():
    print()

def main():
    global listen, connect

    if not len(sys.argv[1:]):
        help()
        sys.exit(1)

    print()

if __name__ == "__main__":
    main()