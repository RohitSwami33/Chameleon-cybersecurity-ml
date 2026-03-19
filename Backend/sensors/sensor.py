import socket
import logging
import json
import httpx
import asyncio
import os
import argparse

# Configure basic logging for the sensor
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [SENSOR_NODE] - %(levelname)s - %(message)s'
)
logger = logging.getLogger("sensor_node")

# Configuration
# This sensor relies purely on ENV variables or args, NOT the main config.py
# so it can run independently on a barebones server.
CENTRAL_BRAIN_URL = os.getenv("CHAMELEON_BRAIN_URL", "http://127.0.0.1:8000/trap/execute")
BIND_HOST = os.getenv("BIND_HOST", "0.0.0.0")
BIND_PORT = int(os.getenv("BIND_PORT", "9999"))

async def forward_payload(ip_address: str, raw_payload: str):
    """
    Forwards raw bytes (decoded to string) to the central brain's API.
    """
    payload = {
        "command": raw_payload.strip(),
        "ip_address": ip_address
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(CENTRAL_BRAIN_URL, json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("response", "")
    except httpx.ConnectError:
        logger.error(f"Cannot reach central brain at {CENTRAL_BRAIN_URL}.")
        return "Connection refused.\r\n"
    except Exception as e:
        logger.error(f"Error forwarding payload: {e}")
        return "Internal error.\r\n"


async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    """
    Handles a single raw socket connection.
    Reads data -> forwards to API -> sends API response back to socket.
    """
    addr = writer.get_extra_info('peername')
    client_ip = addr[0]
    logger.info(f"Incoming connection from {client_ip}:{addr[1]}")
    
    # Send a generic banner to lure attackers
    writer.write(b"Service ready.\r\n> ")
    await writer.drain()
    
    try:
        while True:
            data = await reader.read(1024)
            if not data:
                break
                
            raw_text = data.decode('utf-8', errors='ignore').strip()
            if not raw_text:
                continue
                
            logger.info(f"[{client_ip}] Received {len(data)} bytes: {raw_text[:50]}...")
            
            # Forward to brain to get ML/LLM Deceptive Response
            response_text = await forward_payload(client_ip, raw_text)
            
            # Send the deceptive response back to the attacker
            if response_text:
                if not response_text.endswith('\n'):
                    response_text += '\r\n'
                    
                writer.write(response_text.encode('utf-8'))
                await writer.drain()
                
            writer.write(b"> ")
            await writer.drain()
            
    except ConnectionResetError:
        logger.warning(f"Connection reset by {client_ip}")
    except Exception as e:
        logger.error(f"Error handling client {client_ip}: {e}")
    finally:
        logger.info(f"Closing connection for {client_ip}")
        writer.close()
        await writer.wait_closed()


async def start_sensor():
    """
    Starts the barebones socket listener.
    """
    server = await asyncio.start_server(handle_client, BIND_HOST, BIND_PORT)
    addr = server.sockets[0].getsockname()
    
    logger.info(f"✅ Distributed Sensor Node listening on {addr}")
    logger.info(f"   Forwarding traffic to: {CENTRAL_BRAIN_URL}")
    
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chameleon Distributed Sensor Node")
    parser.add_argument("--brain_url", type=str, help="URL of the central FastAPI brain (e.g. http://brain-ip:8000/trap/execute)")
    parser.add_argument("--port", type=int, help="Port to listen on")
    
    args = parser.parse_args()
    if args.brain_url:
        CENTRAL_BRAIN_URL = args.brain_url
    if args.port:
        BIND_PORT = args.port
        
    try:
        asyncio.run(start_sensor())
    except KeyboardInterrupt:
        logger.info("Sensor node stopped by user.")
