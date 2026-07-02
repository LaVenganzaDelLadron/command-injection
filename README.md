# Command Injection Demo

This project is a small proof-of-concept for sending shell commands from one client to another over a WebSocket-based signaling channel. It is intended for learning and controlled local testing of remote command execution patterns.

## Purpose

The system lets you:
- run one process in listening mode on a target machine;
- send a command from another client;
- receive the command output or an error response.

In practice, this is a minimal remote-command demo built around a signaling server and simple message passing.

## How the system works

The project has three main parts:

1. Signaling layer
   - [signaling/receive_signal.py](signaling/receive_signal.py) opens a WebSocket connection to a signaling server and dispatches incoming messages.
   - [signaling/send_signal.py](signaling/send_signal.py) provides the client-side signaling helper used by the command modules.

2. Command sender
   - [command/send_command.py](command/send_command.py) packages a command into a signaling message, sends it to a target client, and waits for a response.

3. Command receiver
   - [command/receive_command.py](command/receive_command.py) listens for incoming remote-command requests, executes them with the local shell, and sends the result back.

The entry point [main.py](main.py) exposes a simple CLI for two modes:
- listen mode: wait for incoming commands;
- send mode: send a command to a specific target client.

## Requirements

- Python 3.8+
- The `websockets` package

Install dependencies with:

```bash
pip install websockets
```

## Usage

### 1. Start a signaling server

This project expects a signaling server at the default host `http://localhost:8000` and room `testroom`. Make sure your signaling server is reachable before running the clients.

### 2. Start a listener

Run one terminal in listen mode:

```bash
python main.py -l alice
```

This makes the client named `alice` wait for incoming commands.

### 3. Send a command from another client

In a second terminal, send a command to `alice`:

```bash
python main.py -c bob alice "echo hello from alice"
```

The command is executed on the machine running the listener, and the sender receives the output.

## Example commands

```bash
python main.py -l target
python main.py -c sender target "uname -a"
python main.py -c sender target "whoami"
python main.py -c sender target "ls -la"
```

## Notes

- The commands are executed with the privileges of the listener process, so this can be dangerous if used carelessly.
- The default implementation uses `shell=True`, which means the command is interpreted by the system shell.
- The default room and host are defined in [main.py](main.py) and can be changed if needed.

## Security warning

This repository is a demonstration and should only be used in controlled, authorized environments. Remote command execution is inherently risky and should not be exposed to untrusted networks or users.
