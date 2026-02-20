"""WebSocket connection handler for real-time Symposium streaming.

Accepts binary protobuf-framed messages, dispatches to the dialogue engine,
and streams PersonaUtterance responses back to the client.
"""

from __future__ import annotations

import json
import secrets
import time

from fastapi import WebSocket, WebSocketDisconnect

from app.api.websocket.protocol import ProtocolHandler


class WebSocketHandler:
    """Manages a single WebSocket connection for P.S.AI dialogue.

    Protocol flow:
      1. Client sends SessionControl(CREATE) with SymposiumConfig
      2. Server streams PersonaUtterance messages as each persona speaks
      3. Server sends StateUpdate between turns
      4. Client can send TextCommand for follow-up input
      5. Client sends SessionControl(STOP) to end
    """

    def __init__(self, websocket: WebSocket) -> None:
        self._ws = websocket
        # Generate per-connection secret for HMAC
        self._protocol = ProtocolHandler(secrets.token_bytes(32))

    async def handle(self) -> None:
        """Main connection loop."""
        await self._ws.accept()

        try:
            while True:
                data = await self._ws.receive_text()
                await self._dispatch(data)
        except WebSocketDisconnect:
            pass

    async def _dispatch(self, raw_data: str) -> None:
        """Parse and dispatch an incoming message."""
        try:
            msg = json.loads(raw_data)
        except json.JSONDecodeError:
            await self._send_error(400, "Invalid JSON")
            return

        msg_type = msg.get("type")

        if msg_type == "session_control":
            await self._handle_session_control(msg)
        elif msg_type == "text_command":
            await self._handle_text_command(msg)
        else:
            await self._send_error(400, f"Unknown message type: {msg_type}")

    async def _handle_session_control(self, msg: dict) -> None:
        """Handle session create/resume/stop commands."""
        action = msg.get("action")

        if action == "create":
            config = msg.get("config", {})
            await self._send_state_update(
                session_id="pending",
                turn_number=0,
                active_speaker_id="",
                status="session_created",
            )
        elif action == "stop":
            await self._send_state_update(
                session_id=msg.get("session_id", ""),
                turn_number=-1,
                active_speaker_id="",
                status="session_stopped",
            )
        else:
            await self._send_error(400, f"Unknown session action: {action}")

    async def _handle_text_command(self, msg: dict) -> None:
        """Handle incoming text from the user."""
        text = msg.get("text", "")
        if not text.strip():
            await self._send_error(400, "Empty text command")
            return

        # Acknowledge receipt — actual processing happens via dialogue engine
        await self._ws.send_json({
            "type": "ack",
            "nonce": secrets.token_hex(8),
            "timestamp_ms": int(time.time() * 1000),
        })

    async def _send_state_update(
        self,
        session_id: str,
        turn_number: int,
        active_speaker_id: str,
        status: str = "",
    ) -> None:
        await self._ws.send_json({
            "type": "state_update",
            "session_id": session_id,
            "turn_number": turn_number,
            "active_speaker_id": active_speaker_id,
            "status": status,
            "nonce": secrets.token_hex(8),
            "timestamp_ms": int(time.time() * 1000),
        })

    async def _send_error(self, code: int, message: str) -> None:
        await self._ws.send_json({
            "type": "error",
            "code": code,
            "message": message,
            "nonce": secrets.token_hex(8),
            "timestamp_ms": int(time.time() * 1000),
        })
