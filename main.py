import sys

from backend.core import Core


class Main:
    def __init__(self):
        Core(False, sys.argv)  # Change to False to disable debug


if __name__ == "__main__":
    Main()
