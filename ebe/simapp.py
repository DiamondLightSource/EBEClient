import sys
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

from ebesim import EBESim

help_message = """
-------------------------------------------------------------------------------
A script to run an EBE-4 simulator
-------------------------------------------------------------------------------
"""


def parse_args():
    """Parse command line arguments."""
    parser = ArgumentParser(usage=help_message,
                            formatter_class=ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        "-i", "--ip", type=str, default="127.0.0.1", dest="ip",
        help="IP Address of EBE")
    parser.add_argument(
        "-p", "--port", type=int, default=8080, dest="port",
        help="Port of EBE")

    return parser.parse_args()


def main():
    """Run program."""
    args = parse_args()

    EBESim(args.ip, args.port).recv()


if __name__ == "__main__":
    sys.exit(main())
