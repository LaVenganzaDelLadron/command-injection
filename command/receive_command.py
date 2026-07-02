# signal/receive_command.py
import logging
import subprocess


logger = logging.getLogger("receive_command")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


class RemoteCommandHandler:
    """Handle remote-command requests over the existing signaling channel."""

    def __init__(self, signal=None):
        self.signal = None
        if signal is not None:
            self.attach(signal)

    def attach(self, signal):
        """Register this handler with a signaling client."""
        self.signal = signal
        signal.add_handler(self.dispatch_message)
        return self

    async def dispatch_message(self, message):
        """Route incoming signaling messages to the command handler."""
        if not isinstance(message, dict):
            logger.warning("Received invalid signaling payload: %r", message)
            await self._send_error(None, "Invalid signaling message.")
            return

        if message.get("type") == "remote-command":
            logger.debug("Dispatching remote command request: %s", message)
            await self.handle_message(message)
        else:
            logger.debug("Ignoring signaling message of type %s", message.get("type"))

    async def handle_message(self, message):
        """Process a remote-command request and respond over signaling."""
        if not isinstance(message, dict):
            logger.warning("Rejected non-dict message: %r", message)
            await self._send_error(None, "Invalid signaling message.")
            return

        sender = message.get("sender")
        command = message.get("command")

        if not isinstance(command, str) or not command.strip():
            logger.warning("Rejecting invalid remote command from %s: %r", sender, message)
            await self._send_error(sender, "Invalid remote command request.")
            return

        logger.info("Executing command from %s: %s", sender, command)
        try:
            completed = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
            )
        except subprocess.TimeoutExpired:
            logger.error("Command timed out for %s: %s", sender, command)
            await self._send_error(sender, "Command timed out.")
            return
        except Exception as exc:  # pragma: no cover - defensive fallback
            logger.exception("Command execution failed for %s: %s", sender, command)
            await self._send_error(sender, f"Command failed: {exc}")
            return

        output = completed.stdout + completed.stderr
        if not output:
            output = "Command executed successfully."

        logger.info("Command finished for %s with exit code %s", sender, completed.returncode)
        if completed.returncode == 0:
            await self._send_result(sender, "success", output=output)
        else:
            await self._send_result(sender, "error", error=output or "Command failed.")

    async def _send_result(self, target, status, output=None, error=None):
        if self.signal is None:
            logger.warning("Cannot send command result because no signaling client is attached")
            return

        response = {
            "type": "remote-command-result",
            "status": status,
            "target": target,
        }
        if output is not None:
            response["output"] = output
        if error is not None:
            response["error"] = error

        logger.debug("Sending command result to %s: %s", target, response)
        await self.signal.send(response)

    async def _send_error(self, target, error):
        await self._send_result(target, "error", error=error)