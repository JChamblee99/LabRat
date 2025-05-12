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