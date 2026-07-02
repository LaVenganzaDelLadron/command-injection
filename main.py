# main.py
import sys
import asyncio

from signaling.receive_signal import SignalClient
from command.receive_command import RemoteCommandHandler as ReceiverHandler
from command.send_command import RemoteCommandHandler as SenderHandler


HOST = "http//localhost:8000"
ROOM = "testroom"


async def listen_mode(client_id):
    signal = SignalClient(ROOM, client_id, HOST)

    await signal.connect()

    # Register command receiver
    ReceiverHandler(signal)

    print(f"[+] Listening as {client_id}")

    while True:
        await asyncio.sleep(1)


async def connect_mode(client_id, target, command):
    signal = SignalClient(ROOM, client_id, HOST)

    await signal.connect()

    sender = SenderHandler(signal)

    result = await sender.send_command(
        target=target,
        command=command,
        wait_for_result=True,
        timeout=15,
    )

    if result is None:
        print("[+] Command sent")
    elif result.get("status") == "success":
        print(result.get("output", "Command executed successfully"))
    else:
        print("ERROR:", result.get("error", "Unknown error"))

    await signal.close()


def help():
    print(f"""
Usage:

Listen:
    python main.py -l <client_id>

Send:
    python main.py -c <client_id> <target_id> "<command>"
""")


def main():
    if len(sys.argv) < 2:
        help()
        return

    if sys.argv[1] == "-l":
        if len(sys.argv) != 3:
            help()
            return

        client_id = sys.argv[2]
        asyncio.run(listen_mode(client_id))

    elif sys.argv[1] == "-c":
        if len(sys.argv) != 5:
            help()
            return

        client_id = sys.argv[2]
        target = sys.argv[3]
        command = sys.argv[4]

        asyncio.run(
            connect_mode(
                client_id,
                target,
                command
            )
        )

    else:
        help()


if __name__ == "__main__":
    main()