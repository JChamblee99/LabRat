import re

def parse_host_range(host_pattern):
    """Parse a host pattern and generate a list of individual host addresses.

    Keyword arguments:
    - host_pattern: The host pattern to parse (e.g., "team{01..15}.ccdc.local")
    """

    hosts = []

    # Match brace expansion pattern (e.g., "team{01..15}.ccdc.local")
    brace_expansion_match = re.match(r"(.*)\{(\d+)\.\.(\d+)\}(.*)", host_pattern)
    if brace_expansion_match:
        prefix = brace_expansion_match.group(1)
        start = brace_expansion_match.group(2)
        end = brace_expansion_match.group(3)
        suffix = brace_expansion_match.group(4)

        # Padding for leading zeros
        padding = max(len(start), len(end)) if start[0] == '0' or end[0] == '0' else 0

        for i in range(int(start), int(end) + 1):
            hosts.append(f"{prefix}{i:0{padding}d}{suffix}")
        return hosts

    # If no range is detected, return the host as-is
    return [host_pattern]

def obj_filter(obj, filter_strings):
    """Filter an object based on a list of filters. Filters can include simple substrings or field selection and regex patterns.

    Filter criteria:
    - Searching on all fields (e.g., `j\\.doe`)
    - Field selection (e.g., `username=j.doe`)

    Operators:
    - `=`: Equal
    - `!=`: Not equal
    - `=~`: Regex match
    - `!~`: Regex not match

    Keyword arguments:
    - obj: The object to filter.
    - filter_strings: A list of filter strings to apply.
    """

    result = False
    for filter_string in filter_strings:
        equals_op = True
        regex_op = True

        # Operator parsing
        match = re.match(r"([a-zA-Z_]+)(!=|=~|!~|=)(.*)", filter_string)
        if match:
            field = match.group(1)
            operator = match.group(2)
            filter = match.group(3)

            equals_op = not operator[0] == "!"
            regex_op = operator[-1] == "~"

            value = getattr(obj, field, None)
        else:
            filter = filter_string
            value = get_attrs(obj)

        # Ensure value is searchable
        if value is not None:
            # Exclude keys from search
            if isinstance(value, dict):
                value = str(value.values())
            else:
                value = str(value)

            # Regex or literal search
            if regex_op:
                search = re.search(filter, value, flags=re.IGNORECASE) is not None
            else:
                search = filter == value

            # Negate search if using not-operator
            if search == equals_op:
                result = True
            else:
                return False
        elif equals_op:
            return False

    return result

def get_attrs(obj):
    """Get attributes of an object as a dictionary.

    Keyword arguments:
    - obj: The object to get attributes from.
    """
    attrs = {}
    if hasattr(obj, "_attrs"):
        attrs.update(obj._attrs) # Include extended GitLab attributes
    if hasattr(obj, "_updated_attrs"):
        attrs.update(obj._updated_attrs) # Include updated attributes
    if not attrs:
        attrs = {k: v for k, v in vars(obj).items() if not hasattr(v, '__dict__')}

    return attrs if attrs else None