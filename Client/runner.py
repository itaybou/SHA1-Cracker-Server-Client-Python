import udp_client as client


def main():
    udp_client = client.UDPClient()
    udp_client.start()
    return


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Exited")
