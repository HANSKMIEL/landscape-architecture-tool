# VPS Access Test Report - Na Firewall Activatie

**Datum**: 2 oktober 2025, 06:55 UTC  
**Test Locatie**: Dev Container (IP: 4.210.177.128)  
**VPS**: 72.60.176.200  

## Test Resultaten

### TCP Port Connectivity Tests ❌

| Poort | Service | Status | Opmerking |
|-------|---------|--------|-----------|
| 22    | SSH     | ❌ CLOSED/FILTERED | Zelfs SSH is geblokkeerd |
| 5001  | Backend API | ❌ CLOSED/FILTERED | Geen connectie mogelijk |
| 8080  | Frontend | ❌ CLOSED/FILTERED | Geen connectie mogelijk |

### Diagnostic Info

**Alle poorten zijn CLOSED/FILTERED**, inclusief SSH (poort 22). Dit wijst op één van deze situaties:

## Mogelijke Oorzaken

### 1. ⚠️ Firewall Niet Correct Toegewezen (Meest Waarschijnlijk)

De firewall "henk" bestaat en heeft de juiste regels, maar is mogelijk:
- Niet toegewezen aan de VPS instance
- Toegewezen maar niet "enabled" of "activated"
- In een "pending" staat

**Hoe te controleren in Hostinger Panel:**
```
VPS Dashboard → Firewall
└── Firewall "henk"
    ├── Status: Should show "Active" or "Enabled"
    ├── Attached to: Should show your VPS name/IP
    └── Rules: ✅ Correct (accept 8080, 5001, 5000)
```

### 2. ⚠️ SSH Niet in Firewall Regels

Je huidige firewall heeft:
- ✅ TCP 8080 accept
- ✅ TCP 5001 accept
- ✅ TCP 5000 accept
- ❌ **GEEN regel voor SSH (port 22)**

**KRITIEK**: Als je SSH toegang wilt behouden, moet je toevoegen:
```
Action: accept
Protocol: TCP
Port: 22
Source: any (of je eigen IP voor extra veiligheid)
```

**Zonder SSH regel kun je:**
- ❌ Niet via SSH inloggen
- ❌ Geen deployments uitvoeren (die SSH gebruiken)
- ❌ Geen diagnostics draaien

### 3. ⚠️ Default Policy is "Drop All"

Hostinger VPS Firewall heeft:
> "By default, the Hostinger VPS Firewall drops all incoming traffic"

Dit betekent dat **ALLEEN** poorten met een explicit "accept" regel toegankelijk zijn.

**Huidige situatie:**
- Poort 22 (SSH): ❌ Geen regel → BLOCKED
- Poort 8080: ✅ Accept regel → Zou open moeten zijn
- Poort 5001: ✅ Accept regel → Zou open moeten zijn

### 4. ⚠️ Firewall Regel Volgorde

Ik zie dat je een "drop any any" regel hebt onderaan. Check of deze regel:
- **Na** de accept regels staat (correct)
- **Voor** de accept regels staat (verkeerd - blokkeert alles)

**Correcte volgorde:**
```
1. accept TCP 8080 any any
2. accept TCP 5001 any any  
3. accept TCP 5000 any any
4. accept TCP 22 any any      ← ADD THIS!
5. drop any any any any       ← Should be LAST
```

## Aanbevolen Acties (URGENT)

### Stap 1: Voeg SSH Regel Toe ⚠️ **BELANGRIJK**

**Voor je de firewall volledig activeert**, voeg SSH toe:
```
Action: accept
Protocol: TCP
Port: 22
Source: any
Source detail: any
```

**Waarom urgent**: Anders lock je jezelf uit van de VPS!

### Stap 2: Controleer Firewall Status

In Hostinger panel, check:
- [ ] Firewall "henk" status = "Active" of "Enabled"
- [ ] Firewall is "Attached to" je VPS (zie VPS naam/IP)
- [ ] Alle regels zijn "Applied" (geen pending changes)

### Stap 3: Controleer Regel Volgorde

Zorg dat "drop any any" de **laatste** regel is:
```
Rules should be in this order:
1. accept rules (8080, 5001, 5000, 22)
2. drop rule (last)
```

### Stap 4: Test Opnieuw

Na bovenstaande stappen:
1. Wacht 1-2 minuten voor propagatie
2. Test SSH eerst: `ssh root@72.60.176.200` (moet werken)
3. Test poort 8080: `curl http://72.60.176.200:8080/`
4. Test poort 5001: `curl http://72.60.176.200:5001/health`

## GitHub Actions Test

We hebben een workflow klaargezet die vanuit GitHub Actions (andere locatie) test:
- Workflow: `test-vps-access.yml`
- Kan handmatig getriggerd worden
- Test alle poorten vanuit een ander netwerk

## Hostinger Support Info

Als bovenstaande niet werkt, contact Hostinger support met:
```
Subject: VPS Firewall not blocking external access after activation

Details:
- VPS IP: 72.60.176.200
- Firewall name: henk
- Firewall rules configured: TCP 8080, 5001, 5000 (accept from any)
- Issue: All ports remain blocked after firewall activation
- Expected: Ports 8080 and 5001 should be accessible externally
- Verified: Services are running and bound to 0.0.0.0 (all interfaces)
```

## Volgende Stappen

1. ⚠️ **EERST**: Voeg SSH (port 22) regel toe aan firewall
2. Check firewall status/attachment in Hostinger panel
3. Check regel volgorde (drop rule moet laatste zijn)
4. Apply/Enable firewall indien nodig
5. Test opnieuw na 1-2 minuten
6. Run GitHub Actions test workflow voor vergelijking

---

**Status**: Wachten op firewall configuratie verificatie en SSH regel toevoeging.
