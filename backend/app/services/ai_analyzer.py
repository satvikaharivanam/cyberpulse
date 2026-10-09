import requests


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.1:8b"


def analyze_alert(
    threat_type: str,
    severity: str,
    source_ip: str,
    message: str,
) -> str:
    prompt = f"""
You are a cybersecurity analyst working inside CyberPulse.

Analyze the following security alert.

Threat type: {threat_type}
Severity: {severity}
Source IP: {source_ip}
Alert message: {message}

Provide:
1. What this threat means
2. Why it is suspicious
3. Recommended immediate action

Keep the response concise and practical.
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
        },
        timeout=120,
    )

    response.raise_for_status()

    return response.json()["response"]