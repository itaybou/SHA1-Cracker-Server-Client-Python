import protocol


def get_user_input():
    hash_str = input('Welcome to {}. Please enter the hash:\n'.format(protocol.TEAM_NAME))
    str_len = input('Please enter the input string length:\n')
    if len(hash_str) != protocol.MSG_HASH_LEN or not str_len.isdecimal():
        raise ValueError("Illegal arguments given.")
    return hash_str, int(str_len)


def print_error(err):
    print(err)


def print_result(result, address):
    print('Result received from {}:{}.\nThe input string is: {}'
          .format(address[0], address[1], result))


def print_nack(address):
    print('Server at {}:{} returned NACK'.format(address[0], address[1]))