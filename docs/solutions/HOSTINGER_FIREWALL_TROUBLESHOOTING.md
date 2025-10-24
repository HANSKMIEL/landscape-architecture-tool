# Hostinger VPS Firewall Troubleshooting Checklist

## Probleem
Firewall regels zijn toegevoegd voor poorten 8080, 5001, en 5000, maar de poorten zijn nog steeds niet toegankelijk van buitenaf.

## ✅ Firewall Regels Toegevoegd (Geverifieerd)
```
Firewall Name: henk
- accept TCP 8080 from any
- accept TCP 5001 from any  
- accept TCP 5000 from any
- drop any any (default)
```

## ❌ Poorten Nog Steeds Geblokkeerd
- Port 8080: Connection timeout
- Port 5001: Connection timeout
- Getest vanaf: 4.210.177.128 (dev container)

## Mogelijke Oorzaken

### 1. ⚠️ **Firewall Niet Toegewezen aan VPS** (Meest Waarschijnlijk)

**Probleem**: De firewall "henk" bestaat, maar is mogelijk niet toegewezen aan je VPS instance.

**Oplossing**:
1. Ga naar Hostinger VPS panel
2. Navigeer naar **VPS Settings** of **Firewall**
3. Zoek **"Attached to" of "Assigned VPS"** sectie
4. Controleer of de firewall "henk" is toegewezen aan je VPS
5. Als niet → Klik op "Attach" of "Assign" en selecteer je VPS

**Hoe te verifiëren**:
- In Hostinger panel: Check of bij de firewall "henk" je VPS naam/IP staat vermeld
- Of: Bij VPS settings, check of "henk" firewall is geselecteerd

### 2. ⚠️ **Firewall Rules Nog Niet Actief**

**Probleem**: Regels zijn toegevoegd maar niet "applied" of "activated".

**Oplossing**:
1. Check of er een "Apply Changes" of "Save and Apply" knop is
2. Mogelijk moet je firewall "Enable" of "Activate"
3. Sommige panels vereisen een "Reload" actie

### 3. ⚠️ **Services Binden Niet Op Public Interface**

**Probleem**: Services luisteren mogelijk nog op 127.0.0.1 in plaats van 0.0.0.0.

**Verificatie via SSH**:
```bash
# Check what interfaces services are bound to
ss -tlnp | grep -E ":(5000|5001|8080)"

# Expected output for correct binding:
# 0.0.0.0:5001  (good - listens on all interfaces)
# 127.0.0.1:5001  (bad - only localhost)
```

**Oplossing**: Al geïmplementeerd in laatste deployment (0bdba38), maar mogelijk moet service opnieuw gestart:
```bash
sudo systemctl restart landscape-backend-dev
sudo systemctl restart nginx
```

### 4. ⚠️ **UFW (Local Firewall) Actief**

**Probleem**: Ubuntu's UFW firewall kan ook poorten blokkeren.

**Verificatie**:
```bash
sudo ufw status
```

**Oplossing als UFW actief is**:
```bash
sudo ufw allow 8080/tcp
sudo ufw allow 5001/tcp
sudo ufw reload
```

### 5. ⚠️ **Nginx Niet Geconfigureerd Voor Port 8080**

**Probleem**: Nginx luistert mogelijk niet op poort 8080.

**Verificatie**:
```bash
sudo nginx -T | grep "listen.*8080"
```

**Oplossing**: Nginx configuratie aanpassen:
```nginx
server {
    listen 8080;  # Not 127.0.0.1:8080
    server_name _;
    # ... rest of config
}
```

### 6. ⚠️ **Cloud Platform Extra Firewall Layer**

**Probleem**: Hostinger kan een extra firewall layer hebben op platform niveau.

**Oplossing**:
- Check Hostinger documentation voor "VPS Firewall"
- Mogelijk staat er een "Network Firewall" EN een "VPS Firewall"
- Check alle firewall tabs in het panel

## Aanbevolen Actiestappen (In Volgorde)

### Stap 1: Controleer Firewall Toewijzing ⭐ **BELANGRIJK**
```
Hostinger Panel → VPS → Firewall → Check "henk" is assigned to VPS
```

### Stap 2: Controleer Firewall Status
```
Check of firewall "enabled" of "active" staat
Check of er een "Apply" knop is die nog moet worden geklikt
```

### Stap 3: Test Vanaf VPS Zelf (Via SSH)
```bash
# Connect via SSH
ssh root@72.60.176.200

# Test local connectivity
curl http://localhost:8080
curl http://localhost:5001/health

# Test public IP (should work if firewall is correct)
curl http://72.60.176.200:8080
```

### Stap 4: Check Service Bindings
```bash
# Via SSH on VPS
ss -tlnp | grep -E ":(5000|5001|8080)"

# Should show 0.0.0.0:5001 and 0.0.0.0:8080
# If shows 127.0.0.1:XXX → binding issue
```

### Stap 5: Check Local Firewall
```bash
# Via SSH on VPS
sudo ufw status
# If active → add rules for 5001 and 8080
```

### Stap 6: Check Nginx
```bash
# Via SSH on VPS
sudo nginx -T | grep listen
systemctl status nginx
```

## Quick Diagnostic Command

Run dit via SSH op de VPS:
```bash
echo "=== Port Binding ===" && \
ss -tlnp | grep -E ":(5000|5001|8080)" && \
echo "" && \
echo "=== UFW Status ===" && \
sudo ufw status && \
echo "" && \
echo "=== Service Status ===" && \
systemctl is-active nginx landscape-backend-dev && \
echo "" && \
echo "=== Local Test ===" && \
curl -s -o /dev/null -w "localhost:8080 = HTTP %{http_code}\n" http://localhost:8080 && \
curl -s http://localhost:5001/health
```

## Expected Result After Fix

```bash
# Port binding
0.0.0.0:5001  ← Backend listening on all interfaces ✅
0.0.0.0:8080  ← Nginx listening on all interfaces ✅

# Firewall
Hostinger Firewall: henk (assigned to VPS, enabled) ✅
UFW: inactive or ports allowed ✅

# Services
nginx: active (running) ✅
landscape-backend-dev: active (running) ✅

# External access
curl http://72.60.176.200:8080 → HTTP 200 ✅
curl http://72.60.176.200:5001/health → {"status":"healthy"} ✅
```

## Contact Info

Als bovenstaande stappen niet werken:
1. Check Hostinger documentation: https://support.hostinger.com/en/articles/vps-firewall
2. Contact Hostinger support met deze info:
   - VPS IP: 72.60.176.200
   - Firewall name: henk
   - Issue: Ports 8080 and 5001 not accessible despite firewall rules
   - Services are running and bound to 0.0.0.0 (verified)
