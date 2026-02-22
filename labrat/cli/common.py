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

class Colors:
    RESET = "\x1b[0m"
    BRIGHT_RED = "\x1b[0;91m"
    RED = "\x1b[0;31m"
    GREEN = "\x1b[0;32m"
    YELLOW = "\x1b[0;33m"
    BLUE = "\x1b[0;34m"
    MAGENTA = "\x1b[0;35m"
    CYAN = "\x1b[0;36m"
    WHITE = "\x1b[0;37m"

def color_access_level(level, text):
    shades = [
        Colors.RESET,      # guest - none
        Colors.RESET,      # planner - none
        Colors.RESET,      # reporter - none
        Colors.GREEN,      # developer - green
        Colors.YELLOW,     # maintainer - yellow
        Colors.BRIGHT_RED, # owner - bright red (highest)
    ]
    idx = min(len(shades)-1, max(0, (level // 10)))
    return f"{shades[idx]}{text}{Colors.RESET}"

def color_diff(diff):
    lines = []
    for line in diff.splitlines():
        if line.startswith("@@"):
            match = re.match(r"(@@[^@]*@@)(.*)", line)
            if match:
                header = match.group(1)
                tail = match.group(2)
                lines.append(f"{Colors.CYAN}{header}{Colors.RESET}{tail}")
            else:
                lines.append(line)
        elif line.startswith("+"):
            lines.append(f"{Colors.GREEN}{line}{Colors.RESET}")  # Green for additions
        elif line.startswith("-"):
            lines.append(f"{Colors.RED}{line}{Colors.RESET}")  # Red for deletions
        else:
            lines.append(line)

    return "\n".join(lines)