import requests
from langchain.tools import tool
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

ABUSEIPDB_KEY = os.getenv("ABUSEIPDB_API_KEY")

@tool
def check_ip_reputation(ip_address: str) -> str:
    """Check if an IP address is malicious using AbuseIPDB.
    
    Args:
        ip_address: IP address to check (e.g., '192.168.1.50')
    """
    if not ABUSEIPDB_KEY:
        return "AbuseIPDB API key not configured"
    
    try:
        response = requests.get(
            'https://api.abuseipdb.com/api/v2/check',
            headers={'Key': ABUSEIPDB_KEY, 'Accept': 'application/json'},
            params={'ipAddress': ip_address, 'maxAgeInDays': 90, 'verbose': ''}
        )
        response.raise_for_status()
        result = response.json()

        if 'data' not in result:
            return f"Unexpected API response format: {result}"

        data = result['data']

        score = data.get('abuseConfidenceScore', 0)
        total_reports = data.get('totalReports', 0)

        # Determine threat level
        if score >= 75:
            threat_level = "🔴 **HIGH RISK**"
        elif score >= 25:
            threat_level = "🟡 **MEDIUM RISK**"
        else:
            threat_level = "🟢 **LOW RISK**"

        return f"""### IP Reputation Report: `{ip_address}`

**Threat Level:** {threat_level}

- **Abuse Confidence Score:** {score}%
- **Total Reports:** {total_reports}
- **Country:** {data.get('countryCode', 'Unknown')}
- **Is Whitelisted:** {data.get('isWhitelisted', False)}
- **Last Reported:** {data.get('lastReportedAt', 'Never')}"""
    except requests.exceptions.HTTPError as e:
        return f"HTTP Error checking IP reputation: {e.response.status_code} - {e.response.text}"
    except Exception as e:
        return f"Error checking IP reputation: {str(e)}"