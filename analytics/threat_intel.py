import requests
import time

# Cache to prevent hitting API limits
IP_CACHE = {}

# Simple Country to Flag mapping for your demo IPs
FLAG_MAP = {
    "United States": "🇺🇸",
    "India": "🇮🇳",
    "China": "🇨🇳",
    "Russia": "🇷🇺",
    "Germany": "🇩🇪",
    "Local Network": "🏠"
}

def get_ip_intelligence(ip_address):
    """
    Fetches real-world geographic data.
    """
    if ip_address in IP_CACHE:
        return IP_CACHE[ip_address]
    
    if ip_address.startswith(("192.168.", "10.", "172.16.", "127.")):
        return {"country": "Local Network", "city": "Internal", "isp": "Private", "flag": "🏠"}

    try:
        url = f"http://ip-api.com/json/{ip_address}"
        response = requests.get(url, timeout=3)
        
        # Handle Rate Limiting (HTTP 429)
        if response.status_code == 429:
            return {"country": "Rate Limited", "city": "Wait", "isp": "API Cooldown", "flag": "⏳"}

        data = response.json()
        
        if data.get('status') == 'success':
            country = data.get("country", "Unknown")
            intel = {
                "country": country,
                "city": data.get("city", "Unknown"),
                "isp": data.get("isp", "Unknown"),
                "flag": FLAG_MAP.get(country, "🌐")
            }
            IP_CACHE[ip_address] = intel
            return intel
            
    except Exception:
        pass

    return {"country": "Unknown", "city": "Unknown", "isp": "Unknown", "flag": "❓"}