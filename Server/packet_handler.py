import protocol
import hash_cracker as cracker
import time


EMPTY = protocol.encode_str("")


def handle_packet(data, address):
    message_type = data[protocol.MSG_TYPE_INDEX]
    print("Packet of type {} received from address: {}:{}!".format(data[protocol.MSG_TYPE_INDEX], address[0], address[1]))
    generate_message = switcher.get(message_type)
    return generate_message(data), address


def add_offer_message(message):
    return protocol.create_message(protocol.Messages.OFFER.value, EMPTY, protocol.NULL, EMPTY, EMPTY)


def add_ack_nack_message(message):
    start_time = time.time()
    str_len = message[protocol.MSG_ORIG_LEN_INDEX]
    result = cracker.search_in_range(protocol.get_msg_range(message, True, str_len), protocol.get_msg_range(message, False, str_len),
                                     protocol.get_msg_hash(message), message[protocol.MSG_ORIG_LEN_INDEX])
    print("--- Completed request in {} seconds and {} ---".format((time.time() - start_time), "failed" if result is None else "succeeded"))
    return protocol.create_message(protocol.Messages.NACK.value, EMPTY, protocol.NULL, EMPTY, EMPTY)\
        if result is None else protocol.create_message(protocol.Messages.ACK.value,EMPTY, message[protocol.MSG_ORIG_LEN_INDEX], bytes(protocol.encode_str(result)), EMPTY)


def add_nack_message(address):
    return protocol.create_message(protocol.Messages.NACK.value, EMPTY, protocol.NULL, EMPTY, EMPTY), address


switcher = {
    protocol.Messages.DISCOVER.value: add_offer_message,
    protocol.Messages.REQUEST.value: add_ack_nack_message
}




