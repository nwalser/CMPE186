# In VM - ensure these are running:
# Terminal 1: Ryu controller ✓
# Terminal 2: Mininet with 3 switches ✓

# Prepare port scanner (don't run yet)
# Have /tmp/port_scanner.py ready
```

---

## **Demo Sequence**

### **Prompt 1: Network Status** (20 seconds)
```
Can you check my network?
```

**Expected:**
- ✅ Calls `get_network_status`
- Shows 3 switches (all enabled)
- Shows logging status



---

### **Prompt 2: Query Rules** (15 seconds)
```
Show me all firewall rules
```

**Expected:**
- ✅ Calls `get_firewall_rules`
- Shows default ALLOW rule


---

### **Prompt 3: Check Malicious IP** (25 seconds)
```
Is 185.220.101.1 dangerous?
```

**Expected:**
- ✅ Calls `check_ip_reputation`
- Returns high abuse score (~98%)
- Shows threat details



---

### **Prompt 4: Block Malicious IP** (20 seconds)
```
Block that IP immediately
```

**Expected:**
- ✅ Calls `install_firewall_rule`
- Confirms rule installation
- Shows success message



---

### **Prompt 5: Verify Block** (15 seconds)
```
Show me the rules now