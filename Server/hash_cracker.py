import utils
import hashlib

SHA1_RADIX = 16


def search_in_range(lower, upper, sha1_hash, str_len):
    hash_val = int(sha1_hash, SHA1_RADIX)
    low = utils.alphabetic_to_decimal(lower)
    high = utils.alphabetic_to_decimal(upper)
    for s in range(low, high + 1):
        alpha = utils.decimal_to_alphabetic(s, str_len)
        if sha1_160bit_from_str(alpha) == hash_val:
            return alpha


def sha1_160bit_from_str(s):
    return int(hashlib.sha1(s.encode()).hexdigest(), SHA1_RADIX)
