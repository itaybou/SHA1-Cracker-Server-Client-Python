import enum
import struct

TEAM_NAME = "Cybers"

BUFFER_SIZE = 586
MSG_NAME_LEN = 32
MSG_HASH_LEN = 40
MSG_RANGE_LEN = 256

MSG_TYPE_INDEX = 32
MSG_HASH_INDEX = 33
MSG_ORIG_LEN_INDEX = 73
MSG_RANGE_START_INDEX = 74

NULL = 0

ENCODING = "utf-8"


def create_message(msg_type, hash_str, orig_len, range_start, range_end):
    structure = struct.Struct('{}sc{}sc{}s{}s'.format(MSG_NAME_LEN, MSG_HASH_LEN, orig_len, orig_len))
    return structure.pack(encode_str(TEAM_NAME), bytes(encode_str(chr(msg_type))), hash_str, bytes(encode_str(chr(orig_len))), range_start, range_end)


def encode_str(s):
    return s.encode(ENCODING)


def get_from_message_as_str(message, lower, upper):
    result = ""
    for i in range(lower, upper):
        c = chr(message[i])
        if c == '\0':
            break
        result += c
    return encode_str(result)


def get_msg_hash(message):
    return get_from_message_as_str(message, MSG_HASH_INDEX, MSG_HASH_INDEX + MSG_HASH_LEN)


def get_msg_range(message, start, str_len):
    return get_from_message_as_str(message, MSG_RANGE_START_INDEX, MSG_RANGE_START_INDEX + str_len) if start \
        else get_from_message_as_str(message, MSG_RANGE_START_INDEX + str_len, MSG_RANGE_START_INDEX + str_len*2)


class Messages(enum.Enum):
    DISCOVER = 1
    OFFER = 2
    REQUEST = 3
    ACK = 4
    NACK = 5

