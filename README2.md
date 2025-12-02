# AI-Powered SDN Security Agent

## Overview
This project implements an AI-powered security operations agent for Software-Defined Networks (SDN). The agent uses LLM-based reasoning to assist network administrators with threat detection, IP reputation analysis, and automated firewall rule enforcement through natural language interaction.

## Architecture
- **SDN Controller:** Ryu (Python-based OpenFlow controller)
- **Network Emulation:** Mininet
- **Agent Framework:** LangChain with Claude 3.5 Sonnet or GPT-4
- **Backend:** Flask (Python web server)
- **Threat Intelligence:** AbuseIPDB API
- **Frontend:** HTML/CSS/JS chat interface

## Prerequisites
- Mininet Virtual Machine (as used in course labs)
- Python 3.11+ installed on host machine (Mac/Linux)
- VirtualBox or VMware with SSH/port forwarding configured
- API keys for OpenAI/Anthropic and AbuseIPDB

---

## Setup Instructions

### 1. VM Setup (Ryu + Mininet)

**Clone this repository in your Mininet VM:**
```bash
git clone <your-repo-url>
cd ryu
```

**Start Ryu Controller (Terminal 1 in VM):**
```bash
./bin/ryu-manager --wsapi-host 0.0.0.0 --wsapi-port 8080 ryu.app.rest_firewall
```

Wait for: `(16877) wsgi starting up on http://0.0.0.0:8080`

**Start Mininet Topology (Terminal 2 in VM):**
```bash
sudo mn --topo=linear,3 --controller=remote,ip=127.0.0.1,port=6633 --switch ovsk,protocols=OpenFlow13 --mac
```

**Enable Firewall and Set Default Rules:**
```bash
# Enable firewall on all switches
curl -X PUT http://localhost:8080/firewall/module/enable/all

# Install default allow rule
curl -X POST -H "Content-Type: application/json" \
  -d '{"priority": 1, "dl_type": "IPv4", "actions": "ALLOW"}' \
  http://127.0.0.1:8080/firewall/rules/all
```

**Verify Ryu is Running:**
```bash
curl http://localhost:8080/firewall/module/status | python3 -m json.tool
```

---

### 2. Agent Setup (Host Machine)

**Navigate to agent directory:**
```bash
cd agent/
```

**Create Python virtual environment:**
```bash
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

**Install dependencies:**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Configure API keys:**

Create `agent/.env` file:
```bash
# Choose ONE LLM provider:
OPENAI_API_KEY=your_openai_key_here

# Threat Intelligence (get free key from https://www.abuseipdb.com/)
ABUSEIPDB_API_KEY=your_abuseipdb_key_here
```

**Verify network connectivity to VM:**

If using VS Code Remote SSH or SSH port forwarding:
```bash
curl http://localhost:8080/firewall/module/status
```

Should return switch status. If not, ensure port forwarding is configured (see Network Configuration below).

**Start Flask Agent:**
```bash
python app.py
```

You should see:
```
 * Running on http://0.0.0.0:5000
```

**Access the Agent UI:**

Open browser: `http://localhost:5000`

---

## Network Configuration

### Option A: VS Code Remote SSH (Recommended)
If using VS Code with Remote SSH extension, ports 8080 and 5000 are automatically forwarded.

### Option B: Manual SSH Port Forwarding
```bash
ssh -p 2222 -L 8080:localhost:8080 -L 5000:localhost:5000 mininet@localhost
```

### Option C: VirtualBox Port Forwarding
In VirtualBox: Settings → Network → Adapter 1 → Advanced → Port Forwarding:
- SSH: Host Port 2222 → Guest Port 22
- Ryu: Host Port 8080 → Guest Port 8080
- Flask: Host Port 5000 → Guest Port 5000

---

## Firewall API Reference

### Get Status
```bash
curl http://localhost:8080/firewall/module/status | python3 -m json.tool
curl http://localhost:8080/firewall/log/status | python3 -m json.tool
```

### Query Rules
```bash
curl http://localhost:8080/firewall/rules/all | python3 -m json.tool
```

### Install Rule
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{
    "priority": 1000,
    "dl_type": "IPv4",
    "nw_proto": "ICMP",
    "nw_src": "10.0.0.1/32",
    "nw_dst": "10.0.0.2/32",
    "actions": "DENY"
  }' \
  http://localhost:8080/firewall/rules/all
```

### Enable/Disable Firewall
```bash
curl -X PUT http://localhost:8080/firewall/module/enable/all
curl -X PUT http://localhost:8080/firewall/module/disable/all
```

---

## Project Structure
```
ryu/
├── bin/
│   └── ryu-manager              # Ryu controller binary
├── ryu/
│   └── app/
│       └── rest_firewall.py     # Firewall REST API
├── agent/                       # AI Agent application
│   ├── app.py                   # Flask web server
│   ├── agent.py                 # LangChain agent logic
│   ├── tools/
│   │   ├── network_tools.py     # Ryu API integration
│   │   └── threat_tools.py      # AbuseIPDB integration
│   ├── frontend/
│   │   └── index.html           # Chat UI
│   ├── requirements.txt         # Python dependencies
│   ├── .env                     # API keys (not committed)
│   └── venv/                    # Virtual environment
└── README.md
```

---

## Troubleshooting

**"Connection refused" when accessing Ryu API:**
- Ensure Ryu is running and listening on port 8080
- Verify port forwarding is configured correctly
- Test with: `curl http://localhost:8080/firewall/module/status`

**"AbuseIPDB authentication failed":**
- Check API key in `.env` file (no spaces, no quotes)
- Verify key is valid at https://www.abuseipdb.com/account/api
- Ensure `python-dotenv` is installed

**Agent not responding:**
- Check Flask is running on port 5000
- Verify LLM API key (OpenAI or Anthropic) in `.env`
- Check terminal for error messages

**Mininet can't connect to controller:**
- Ensure Ryu started before Mininet
- Verify controller is listening on port 6633
- Check with: `sudo ovs-vsctl show` in VM

---

## Development Workflow

**Terminal Layout:**
- VM Terminal 1: Ryu controller
- VM Terminal 2: Mininet CLI
- Host Terminal: Flask agent
- Browser: Agent UI at `http://localhost:5000`

**Typical Development Cycle:**
1. Make changes to agent code on host machine
2. Restart Flask app (`Ctrl+C`, then `python app.py`)
3. Test in browser
4. No need to restart Ryu/Mininet unless testing network changes

---

## Contributors
Nicholas Faylor, Nathaniel Walser
