# services/mcp_server.py
# Placeholder "MCP server" adapter for assignment: exposes tool-like functions.
# In a real MCP server you'd run a separate process; here we simulate calls.
import requests

def get_emergency_numbers(country_code: str = "LK") -> dict:
    # Placeholder: static map for demo; extend with a real API if needed.