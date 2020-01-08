import protocol
import utils
import math
import io_handler as io

EMPTY = protocol.encode_str("")


def handle_response(data, address, client):
    message_type = data[protocol.MSG_TYPE_INDEX]
    action = switcher.get(message_type)
    action(data, address, client)


def add_active_server(data, address, client):
    client.active_servers.put(address)


def fetch_result(data, address, client):
    result = ''
    str_len = data[protocol.MSG_ORIG_LEN_INDEX] + protocol.MSG_RANGE_START_INDEX
    index = protocol.MSG_RANGE_START_INDEX
    while index < str_len:
        result += chr(data[index])
        index += 1
    io.print_result(result, address)
    while client.active_servers.qsize() != 0:
        client.active_servers.get(False)
    client.terminate()


def inform_nack(data, address, client):
    io.print_nack(address)
    client.active_servers.get(False)
    if client.active_servers.qsize() == 0:
        io.print_error('Result was not found.')
        client.terminate()


def create_request(hash_str, str_len):
    return protocol.create_message(protocol.Messages.DISCOVER.value, bytes(protocol.encode_str(hash_str)), int(str_len), EMPTY, EMPTY)


def create_request_with_ranges(hash_str, str_len, range):
    lower, upper = range
    return protocol.create_message(protocol.Messages.REQUEST.value, bytes(protocol.encode_str(hash_str)), str_len,
                                   bytes(protocol.encode_str(lower)), bytes(protocol.encode_str(upper)))


def divide_to_equal_ranges(str_len, server_count):
    alphabetics = 26
    total_range = pow(alphabetics, str_len)
    divided_ranges = math.ceil(total_range / server_count) - 1
    ranges, curr_start_range, curr_end_range = [], 0, divided_ranges
    for i in range(0, server_count):
        ranges.append((utils.decimal_to_alphabetic(curr_start_range, str_len), utils.decimal_to_alphabetic(curr_end_range, str_len)))
        curr_start_range, curr_end_range = curr_end_range + 1, curr_end_range + (total_range - curr_end_range - 1 if i == server_count - 2 else divided_ranges)
    return ranges


switcher = {
    protocol.Messages.OFFER.value: add_active_server,
    protocol.Messages.ACK.value: fetch_result,
    protocol.Messages.NACK.value: inform_nack
}
