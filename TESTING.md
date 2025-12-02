# Testing Guide

This document provides essential test cases to verify all agent functionality.

---

## Prerequisites

Ensure the following are running:
- ✅ Ryu controller (VM Terminal 1)
- ✅ Mininet topology (VM Terminal 2)
- ✅ Flask agent (Host Terminal)
- ✅ Browser open at `http://localhost:5000`

---

## Core Functionality Tests

### Test 1: Network Status Query
**Purpose:** Verify agent can query Ryu controller

**Prompt:**
```
Can you check my network status?
```

**Expected Result:**
- Agent calls `get_network_status` tool
- Returns status of 3 switches (all enabled)
- Shows logging status for each switch

---

### Test 2: Query Firewall Rules
**Purpose:** Verify agent can retrieve current firewall rules

**Prompt:**
```
Show me all firewall rules
```

**Expected Result:**
- Agent calls `get_firewall_rules` tool
- Returns list of current rules (should include default ALLOW rule)

---

### Test 3: Check External IP Reputation
**Purpose:** Verify threat intelligence integration

**Prompt:**
```
Is 45.95.168.123 malicious?
```

**Expected Result:**
- Agent calls `check_ip_reputation` tool
- Returns AbuseIPDB data: abuse score, total reports, country
- High abuse score (~98%) indicates known malicious IP

---

### Test 4: Install Blocking Rule
**Purpose:** Verify agent can create firewall rules

**Prompt:**
```
Block all traffic from 10.0.0.1
```

**Expected Result:**
- Agent calls `install_firewall_rule` tool
- Confirms rule installation successful
- Returns confirmation message

---

### Test 5: Verify Rule Creation
**Purpose:** Confirm rule was actually installed

**Prompt:**
```
Show me the firewall rules again
```

**Expected Result:**
- Agent calls `get_firewall_rules` tool
- Returns updated rule list including the new DENY rule for 10.0.0.1

---

## Multi-Step Reasoning Tests

### Test 6: Investigate and Recommend
**Purpose:** Verify agent chains multiple tools and provides recommendations

**Prompt:**
```
Should I be worried about traffic from 185.220.101.45?
```

**Expected Result:**
- Agent calls `check_ip_reputation` automatically
- Analyzes abuse score
- Provides recommendation (block/monitor/allow)
- May ask for confirmation before taking action

---

### Test 7: Internal IP Investigation
**Purpose:** Verify agent recognizes internal vs external IPs

**Prompt:**
```
Investigate 10.0.0.2
```

**Expected Result:**
- Agent recognizes this is an internal IP (10.x.x.x range)
- Does NOT call threat intelligence (pointless for private IPs)
- May call `get_network_status` or suggest checking local network activity

---

## Real Traffic Scenario

### Test 8: Normal Network Activity
**Purpose:** Verify agent can describe network state with active traffic

**Setup (in Mininet):**
```bash
mininet> h1 ping -c 5 h2
```

**Prompt:**
```
What's happening on the network right now?
```

**Expected Result:**
- Agent calls `get_network_status`
- Describes connected switches and current activity
- May reference active flows if visible in Ryu stats

---

## Advanced Scenario

### Test 9: Simulate Port Scanning Attack
**Purpose:** Demonstrate realistic security incident response

**Setup (in VM, create script):**
```bash
nano /tmp/port_scanner.py
```

Paste:
```python
#!/usr/bin/env python3
import socket
target_subnet = "10.0.0."
ports = [22, 80, 443, 3306, 5432, 8080]
for host_num in range(1, 4):
    target = f"{target_subnet}{host_num}"
    for port in ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.1)
            sock.connect((target, port))
            sock.close()
        except:
            pass
```

Make executable and run:
```bash
chmod +x /tmp/port_scanner.py
```

**In Mininet:**
```bash
mininet> h1 python3 /tmp/port_scanner.py &
```

**Prompt:**
```
I'm seeing suspicious activity from 10.0.0.1. What should I do?
```

**Expected Result:**
- Agent may call `get_network_status` to investigate
- Recognizes 10.0.0.1 is internal (no threat intel needed)
- Recommends investigating or blocking based on behavior patterns
- If you confirm blocking, agent installs deny rule

---

### Test 10: Verify Block Effectiveness
**Purpose:** Confirm firewall rules are actually enforced

**After blocking 10.0.0.1 in Test 9, run in Mininet:**
```bash
mininet> h1 ping h2
```

**Expected Result:**
- Ping should fail or have significant packet loss
- Demonstrates firewall rule is active

**Then ask agent:**
```
Confirm that 10.0.0.1 is blocked
```

**Expected Result:**
- Agent calls `get_firewall_rules`
- Shows DENY rule for 10.0.0.1
- Confirms blocking is in effect

---

## Success Criteria

All tests pass if:
- ✅ Each tool (`get_network_status`, `get_firewall_rules`, `check_ip_reputation`, `install_firewall_rule`) executes successfully
- ✅ Agent chains multiple tools when appropriate (Test 6)
- ✅ Agent provides natural language explanations
- ✅ Firewall rules are actually created in Ryu (Test 5, 10)
- ✅ Agent recognizes internal vs external IPs (Test 7)
- ✅ Real network changes are reflected in agent responses (Test 8, 10)

---

## Notes

- Tests 1-5: Basic single-tool functionality
- Tests 6-7: Multi-step reasoning
- Tests 8-10: Real network interaction
- Total time: ~10-15 minutes for all tests
- For demo: Run Tests 1, 3, 4, 9, 10 (shows complete workflow)