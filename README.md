# Setup of development environment
## 1. Run Development Infrastructure
```bash
sudo mn --topo=linear,3 --controller=remote,ip=127.0.0.1,port=6633 --switch ovsk,protocols=OpenFlow13 --mac
```

## 2. Run Firewall RestApi (Port 8080)
```bash
./bin/ryu-manager --wsapi-host 0.0.0.0 --wsapi-port 8080 ryu.app.rest_firewall
```

## 3. Setup Correct Flows
```bash
# enable all switches and install default rule
curl -X PUT http://localhost:8080/firewall/module/enable/all
curl -X POST -H "Content-Type: application/json" \
  -d '{"priority": 1, "dl_type": "IPv4", "actions": "ALLOW"}' \
  http://127.0.0.1:8080/firewall/rules/all
```

## Firewall requests
```bash
# enable firewall behaviour on all switches
curl -X PUT http://localhost:8080/firewall/module/enable/all

# get status of connected switches
curl http://127.0.0.1:8080/firewall/module/status | python3 -m json.tool
curl http://127.0.0.1:8080/firewall/log/status | python3 -m json.tool
curl http://127.0.0.1:8080/firewall/rules/all | python3 -m json.tool

# full rule example
curl -X POST -H "Content-Type: application/json" \
  -d '{"priority": 1000, "dl_type":"IPv4", "nw_proto":"ICMP", "nw_src":"10.0.0.1/32", "nw_dst":"10.0.0.2/32", "actions":"DENY"}' \
  http://127.0.0.1:8080/firewall/rules/all
```