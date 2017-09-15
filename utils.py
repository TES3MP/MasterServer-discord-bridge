import re
import socket


def is_valid_ip(addr):
    try:
        if addr.count('.') < 3:
            return False
        socket.inet_aton(addr)
        return True
    except socket.error:
        return False


def is_valid_hostname(hostname):  # https://stackoverflow.com/a/33214423/8144273
    if hostname[-1] == ".":
        # strip exactly one dot from the right, if present
        hostname = hostname[:-1]
    if len(hostname) > 253:
        return False

    labels = hostname.split(".")

    # the TLD must be not all-numeric
    if re.match(r"[0-9]+$", labels[-1]):
        return False

    allowed = re.compile(r"(?!-)[a-z0-9-]{1,63}(?<!-)$", re.IGNORECASE)
    return all(allowed.match(label) for label in labels)


def is_valid_address(addr):
    return is_valid_hostname(addr) or is_valid_ip(addr)
