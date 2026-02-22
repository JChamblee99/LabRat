import re

def parse_host_range(host_pattern):
    """Parse a host pattern and generate a list of individual host addresses.

    Keyword arguments:
    - host_pattern: The host pattern to parse (e.g., "team{01..15}.ccdc.local")
    """
    
    hosts = []

    # Match brace expansion patter (e.g., "team{01..15}.ccdc.local")
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
    - Simple substring matching on all fields (e.g., `j.doe`)
    - Field selection (e.g., `username=j.doe`)

    Keyword arguments:
    - obj: The object to filter.
    - filter_strings: A list of filter strings to apply.
    """

    result = False
    for filter_string in filter_strings:
        # Determine whether to use simple or complex filtering
        if "=" in filter_string:
            # Complex filtering with operator
            equals_op = "!=" not in filter_string
            filter = filter_string.split("!=") if "!=" in filter_string else filter_string.split("=")
        else:
            # Simple filtering on all attribute values
            equals_op = True
            if hasattr(obj, "_updated_attrs"):
                obj._attrs.update(obj._updated_attrs) # Include extended GitLab attributes
            else:
                # Add _attrs for non-GitLab objects
                obj._attrs = {k: v for k, v in vars(obj).items() if not hasattr(v, '__dict__')}
            filter = ["_attrs", filter_string]

        value = getattr(obj, filter[0], None)
        if value is not None:
            # Exclude keys from search
            if isinstance(value, dict):
                value = str(value.values())
            else:
                value = str(value)

            match = re.search(filter[1], value, flags=re.IGNORECASE) is not None
            if match == equals_op:
                result = True
            else:
                return False
        elif equals_op:
            return False

    return result