import argparse
import re

def add_filtered_parser(subparsers, name, handler, aliases=[], help=None, filter_required=True, all_help="All items", filter_help="Filter by substring"):
    parser = subparsers.add_parser(name, aliases=aliases, help=help)

    filter_group = parser.add_mutually_exclusive_group(required=filter_required)

    if filter_required:
        filter_group.add_argument("-a", "--all", action="store_true", help=all_help)

    filter_group.add_argument("-f", "--filter", action="append", help=filter_help)

    parser.set_defaults(func=handler, _parser=parser)
    return parser

def print_table(headers, data, sort_key=None):
    """
    Print a table with the given data and headers.
    """
    column_widths = [max(len(re.sub(r'\x1b\[[0-9;]*m', '', str(x))) for x in col) for col in zip(*([headers] + data))]

    # Print header
    if headers:
        print(" " + "  ".join(h.ljust(w) for h, w in zip(headers, column_widths)) + " ")
        print(" ".join("=" * (w + 1) for w in column_widths))

    # Sort data by the specified key
    if sort_key is not None:
        data = sorted(data, key=lambda x: x[headers.index(sort_key)])

    # Print data rows
    for row in data:
        print(" " + "  ".join(str(x).ljust(w) for x, w in zip(row, column_widths)) + " ")

def ansi_for_level(level):
    shades = [
        "\x1b[0m",      # guest - none
        "\x1b[0m",      # planner - none
        "\x1b[0m",      # reporter - none
        "\x1b[0;32m",   # developer - green
        "\x1b[0;33m",   # maintainer - yellow
        "\x1b[0;91m",   # owner - bright red (highest)
    ]
    idx = min(len(shades)-1, max(0, (level // 10)))
    return shades[idx]