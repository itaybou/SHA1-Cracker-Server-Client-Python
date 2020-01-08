import udp_server as server


def main():
    udp_server = server.UDPServer()
    udp_server.start()
    return


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Exited")
