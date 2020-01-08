from string import ascii_lowercase

ALPHA_RADIX = 26


def alphabetic_to_decimal(s):
    curr_pow = len(s) - 1
    decimal = 0
    lst = list(map((lambda c: ord(chr(c)) - ord('a')), s))
    for val in lst:
        decimal += val * pow(26, curr_pow)
        curr_pow -= 1
    return decimal


def decimal_to_alphabetic(num, str_len):
    alphabet = ascii_lowercase
    alphabetic = ''
    while num:
        alphabetic = alphabet[num % ALPHA_RADIX] + alphabetic
        num //= ALPHA_RADIX
    return alphabetic.rjust(str_len, 'a') if len(alphabetic) < str_len else alphabetic
