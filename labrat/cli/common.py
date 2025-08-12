import argparse

def add_filtered_parser(subparsers, name, handler, aliases=[], help=None, filter_required=True, all_help="All items", filter_help="Filter by substring"):
    parser = subparsers.add_parser(name, aliases=aliases, help=help)

    filter_group = parser.add_mutually_exclusive_group(required=filter_required)

    if filter_required:
        filter_group.add_argument("-a", "--all", action="store_true", help=all_help)
        
    filter_group.add_argument("-f", "--filter", help=filter_help)
    
    parser.set_defaults(func=handler, _parser=parser)
    return parser

def print_table(headers, data):
    """
    Print a table with the given data and headers.
    """
    column_widths = [max(len(str(x)) for x in col) for col in zip(*([headers] + data))]

    # Print header
    if headers:
        print(" " + "  ".join(h.ljust(w) for h, w in zip(headers, column_widths)) + " ")
        print(" ".join("=" * (w + 1) for w in column_widths))

    # Print data rows
    for row in data:
        print(" " + "  ".join(str(x).ljust(w) for x, w in zip(row, column_widths)) + " ")