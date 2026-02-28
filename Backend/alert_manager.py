import httpx
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import json

from config import settings

logger = logging.getLogger(__name__)

class AlertManager:
    def __init__(self):
        # We assume these exist in config.py or environment variables.
        self.slack_webhook_url = getattr(settings, "SLACK_WEBHOOK_URL", None)
        self.discord_webhook_url = getattr(settings, "DISCORD_WEBHOOK_URL", None)

    async def _send_slack_alert(self, message: str, payload: Dict[str, Any]):
        if not self.slack_webhook_url:
            return
            
        slack_data = {
            "text": f"🚨 *{message}*\n```\n{json.dumps(payload, indent=2)}\n```"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.slack_webhook_url, json=slack_data)
                response.raise_for_status()
        except Exception as e:
            logger.error(f"Failed to send Slack alert: {e}")

    async def _send_discord_alert(self, message: str, payload: Dict[str, Any]):
        if not self.discord_webhook_url:
            return
            
        discord_data = {
            "content": f"🚨 **{message}**\n```json\n{json.dumps(payload, indent=2)}\n```"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.discord_webhook_url, json=discord_data)
                response.raise_for_status()
        except Exception as e:
            logger.error(f"Failed to send Discord alert: {e}")

    async def trigger_critical_attack_alert(self, ip_address: str, command: str, score: float, session_id: Optional[str] = None):
        message = "CRITICAL ATTACK DETECTED"
        payload = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "ip_address": ip_address,
            "command": command,
            "prediction_score": score,
            "honeytoken_session_id": session_id
        }
        
        # Run asynchronously without blocking
        await self._send_slack_alert(message, payload)
        await self._send_discord_alert(message, payload)

    async def trigger_beacon_exfiltration_alert(self, session_id: str, ip_address: str, user_agent: str):
        message = "HONEYTOKEN EXFILTRATION (BEACON EVENT)"
        payload = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "session_id": session_id,
            "source_ip": ip_address,
            "user_agent": user_agent,
        }
        
        await self._send_slack_alert(message, payload)
        await self._send_discord_alert(message, payload)

# Singleton instance for the application
alert_manager = AlertManager()
