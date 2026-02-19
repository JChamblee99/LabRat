import re

def parse_host_range(host_pattern):
    """
    Parse a host pattern and generate a list of individual host addresses.
    Supports:
    - IP ranges like "10.10.101-115.80"
    - Hostname ranges like "team{01...15}.farm.local"
    """
    hosts = []

    # Match IP range pattern (e.g., "10.10.101-115.80")
    ip_range_match = re.match(r"([0-9.]*)\.(\d+)-(\d+)([0-9.:]*)", host_pattern)
    if ip_range_match:
        prefix = ip_range_match.group(1)
        start = int(ip_range_match.group(2))
        end = int(ip_range_match.group(3))
        suffix = ip_range_match.group(4)
        for i in range(start, end + 1):
            hosts.append(f"{prefix}.{i}{suffix}")
        return hosts

    # Match hostname range pattern (e.g., "team{01..15}.farm.local")
    hostname_range_match = re.match(r"(.*)\{(\d+)\.\.(\d+)\}(.*)", host_pattern)
    if hostname_range_match:
        prefix = hostname_range_match.group(1)
        start = int(hostname_range_match.group(2))
        end = int(hostname_range_match.group(3))
        suffix = hostname_range_match.group(4)
        for i in range(start, end + 1):
            hosts.append(f"{prefix}{i:02}{suffix}")
        return hosts

    # If no range is detected, return the host as-is
    return [host_pattern]

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

def obj_filter(obj, filter_strings):
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
            obj._attrs.update(obj._updated_attrs) # Include extended GitLab attributes
            filter = ["_attrs", filter_string]

        value = getattr(obj, filter[0], None)
        if value is not None:
            # Exclude keys from search
            if isinstance(value, dict):
                value = str(value.values())
            else:
                value = str(value)

            match = re.search(filter[1], value) is not None
            if match == equals_op:
                result = True
            else:
                return False

    return result