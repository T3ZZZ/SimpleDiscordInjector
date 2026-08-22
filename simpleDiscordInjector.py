import subprocess
import json
import requests
import websocket

def start_discord(discord_path: str, port: int = 9222):
    """Start Discord with remote debugging enabled."""
    return subprocess.Popen(
        [
            discord_path,
            f"--remote-debugging-port={port}",
            f"--remote-allow-origins=http://localhost:{port}",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

def send_js(code: str, port: int = 9222):
    """Execute JavaScript in the Discord client."""
    response = requests.get(
        f"http://localhost:{port}/json",
        timeout=5,
    )

    response.raise_for_status()

    targets = response.json()

    page = next(
        (target for target in targets if target.get("type") == "page"),
        None,
    )

    if page is None:
        raise RuntimeError("No Discord page found.")

    ws_url = page.get("webSocketDebuggerUrl")

    if not ws_url:
        raise RuntimeError("Discord WebSocket URL not found.")

    ws = websocket.create_connection(ws_url, timeout=5)

    ws.send(
        json.dumps(
            {
                "id": 1,
                "method": "Runtime.evaluate",
                "params": {
                    "expression": code,
                    "returnByValue": True,
                },
            }
        )
    )

    result = json.loads(ws.recv())

    if "error" in result:
        raise RuntimeError(result["error"])

    return result

if __name__ == "__main__":
    """Demo Code"""
    start_discord(r"...\DiscordCanary.exe")
    input("Press [Enter] to inject")
    code_result = send_js("document.title")
    print(f"Page title: {code_result["result"]["result"]["value"]}")