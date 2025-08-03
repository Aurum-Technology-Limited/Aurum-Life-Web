# SendGrid Domain Authentication Setup

## Steps to Fix Outlook Delivery Issues

### 1. Domain Authentication (Most Important)
Log into your SendGrid dashboard and set up domain authentication for `aurumtechnologyltd.com`:

**DNS Records to Add:**
```
CNAME: s1._domainkey.aurumtechnologyltd.com → s1.domainkey.u29808021.wl137.sendgrid.net
CNAME: s2._domainkey.aurumtechnologyltd.com → s2.domainkey.u29808021.wl137.sendgrid.net
```

**SPF Record (TXT):**
```
TXT: aurumtechnologyltd.com → "v=spf1 include:sendgrid.net ~all"
```

**DMARC Record (TXT):**
```
TXT: _dmarc.aurumtechnologyltd.com → "v=DMARC1; p=none; rua=mailto:marc.alleyne@aurumtechnologyltd.com"
```

### 2. Alternative: Use SendGrid Subdomain
Create a subdomain like `mail.aurumtechnologyltd.com` and authenticate it instead.

### 3. Quick Test: Use SendGrid Domain
Temporarily use `@sendgrid.net` domain for testing:
- Change SENDER_EMAIL to use a verified SendGrid domain