import requests
from langchain.tools import tool

RYU_API = "http://localhost:8080"

@tool
def get_firewall_rules(switch_id: str = "all") -> str:
    """Get current firewall rules from Ryu controller.

    Args:
        switch_id: Switch DPID or 'all' for all switches
    """
    try:
        response = requests.get(f"{RYU_API}/firewall/rules/{switch_id}", timeout=5)
        response.raise_for_status()
        rules = response.json()

        if not rules or (isinstance(rules, dict) and not any(rules.values())):
            return "### Firewall Rules\n\n**No rules currently configured.**"

        # Format rules as markdown
        output = "### Current Firewall Rules\n\n"
        if isinstance(rules, dict):
            for switch, switch_rules in rules.items():
                output += f"**Switch:** `{switch}`\n\n"
                if switch_rules:
                    for rule in switch_rules:
                        action = rule.get('actions', 'UNKNOWN')
                        src = rule.get('nw_src', 'any')
                        dst = rule.get('nw_dst', 'any')
                        priority = rule.get('priority', 'N/A')
                        output += f"- **{action}** | Source: `{src}` → Dest: `{dst}` | Priority: {priority}\n"
                else:
                    output += "  *No rules*\n"
                output += "\n"
        return output
    except requests.exceptions.Timeout:
        return "⚠️ **Error:** Connection to Ryu controller timed out. Is Ryu running?"
    except requests.exceptions.ConnectionError:
        return "⚠️ **Error:** Cannot connect to Ryu controller. Please ensure Ryu is running on port 8080."
    except Exception as e:
        return f"⚠️ **Error querying rules:** {str(e)}"

@tool
def install_firewall_rule(
    nw_src: str,
    nw_dst: str = "0.0.0.0/0",
    action: str = "DENY",
    priority: int = 1000
) -> str:
    """Install a firewall rule to block or allow traffic.
    
    Args:
        nw_src: Source IP address (e.g., '10.0.0.1/32')
        nw_dst: Destination IP address (default: any)
        action: DENY or ALLOW
        priority: Rule priority (higher = more important)
    """
    try:
        rule = {
            "priority": priority,
            "dl_type": "IPv4",
            "nw_src": nw_src,
            "nw_dst": nw_dst,
            "actions": action
        }
        response = requests.post(
            f"{RYU_API}/firewall/rules/all",
            json=rule,
            timeout=5
        )
        if response.status_code == 200:
            return f"""### ✅ Firewall Rule Installed

**Action:** {action}
**Source IP:** `{nw_src}`
**Destination IP:** `{nw_dst}`
**Priority:** {priority}

The rule has been successfully applied to all switches."""
        else:
            return f"⚠️ **Failed to install rule:** {response.text}"
    except requests.exceptions.Timeout:
        return "⚠️ **Error:** Connection to Ryu controller timed out. Is Ryu running?"
    except requests.exceptions.ConnectionError:
        return "⚠️ **Error:** Cannot connect to Ryu controller. Please ensure Ryu is running on port 8080."
    except Exception as e:
        return f"⚠️ **Error installing rule:** {str(e)}"

@tool
def get_network_status() -> str:
    """Get status of all connected switches and firewall module."""
    try:
        switch_response = requests.get(f"{RYU_API}/firewall/module/status", timeout=5)
        switch_response.raise_for_status()
        switch_status = switch_response.json()

        log_response = requests.get(f"{RYU_API}/firewall/log/status", timeout=5)
        log_response.raise_for_status()
        log_status = log_response.json()

        # Format status as markdown
        output = "### Network Status\n\n**Firewall Modules:**\n\n"

        if isinstance(switch_status, dict):
            for switch, status in switch_status.items():
                enabled = "✅ Enabled" if status == "enable" else "❌ Disabled"
                output += f"- Switch `{switch}`: {enabled}\n"

        output += "\n**Logging Status:**\n\n"
        if isinstance(log_status, dict):
            for switch, status in log_status.items():
                enabled = "✅ Enabled" if status == "enable" else "❌ Disabled"
                output += f"- Switch `{switch}`: {enabled}\n"

        return output
    except requests.exceptions.Timeout:
        return "⚠️ **Error:** Connection to Ryu controller timed out. Is Ryu running?"
    except requests.exceptions.ConnectionError:
        return "⚠️ **Error:** Cannot connect to Ryu controller. Please ensure Ryu is running on port 8080."
    except Exception as e:
        return f"⚠️ **Error getting status:** {str(e)}"