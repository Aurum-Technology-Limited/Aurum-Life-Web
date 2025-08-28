# Aurum Life Security & Privacy Policy

**Last Updated:** January 2025  
**Effective Date:** Upon Launch  
**Document Type:** Security & Legal Compliance

---

## 🔐 Security Overview

### Security Principles
1. **Privacy by Design**: Security built into every feature
2. **Least Privilege**: Minimal access rights by default
3. **Defense in Depth**: Multiple layers of security
4. **Continuous Monitoring**: Real-time threat detection
5. **Transparency**: Clear communication about data usage

---

## 🛡️ Technical Security Measures

### 1. **Data Encryption**

#### At Rest
- **Database**: AES-256 encryption via Supabase
- **File Storage**: Encrypted S3 buckets
- **Backups**: Encrypted with separate keys
- **Local Storage**: No sensitive data in browser storage

#### In Transit
- **HTTPS**: TLS 1.3 minimum for all connections
- **API Communication**: Certificate pinning for mobile apps
- **WebSocket**: WSS protocol for real-time features
- **Email**: TLS for SMTP communications

### 2. **Authentication & Access Control**

#### Authentication Methods
- **Password Requirements**:
  - Minimum 8 characters
  - Mix of uppercase, lowercase, numbers, symbols
  - No common passwords (NIST guidelines)
  - Bcrypt hashing with cost factor 12

- **OAuth 2.0**:
  - Google OAuth integration
  - No password storage for OAuth users
  - Scope limited to basic profile info

#### Session Management
- **JWT Tokens**:
  - 24-hour expiration
  - Refresh token rotation
  - Secure, HttpOnly cookies
  - CSRF protection

#### Multi-Factor Authentication (Planned)
- TOTP (Time-based One-Time Password)
- SMS backup (with security warnings)
- Recovery codes

### 3. **API Security**

#### Rate Limiting
```
Standard Users:
- 1000 requests/hour general
- 100 requests/hour AI endpoints
- 10 requests/minute auth endpoints

Premium Users:
- 5000 requests/hour general
- 500 requests/hour AI endpoints
```

#### Input Validation
- **SQL Injection**: Parameterized queries only
- **XSS Prevention**: Content Security Policy (CSP)
- **CSRF Protection**: Double-submit cookies
- **File Uploads**: Type validation, size limits, virus scanning

### 4. **Infrastructure Security**

#### Network Security
- **Firewall Rules**: Whitelist-only approach
- **VPC Isolation**: Private subnets for databases
- **DDoS Protection**: Cloudflare integration
- **SSL/TLS**: A+ rating on SSL Labs

#### Container Security
- **Base Images**: Minimal Alpine Linux
- **Vulnerability Scanning**: Daily automated scans
- **Runtime Protection**: Read-only filesystems
- **Secrets Management**: Kubernetes secrets, never in code

### 5. **Monitoring & Incident Response**

#### Security Monitoring
- **Failed Login Attempts**: Alert after 5 failures
- **Unusual Access Patterns**: Geographic anomaly detection
- **API Abuse**: Automated blocking of suspicious IPs
- **Data Exfiltration**: Large data transfer alerts

#### Incident Response Plan
1. **Detection**: Automated + manual monitoring
2. **Containment**: Immediate isolation of affected systems
3. **Investigation**: Forensic analysis of logs
4. **Remediation**: Patch vulnerabilities, reset credentials
5. **Communication**: Notify affected users within 72 hours
6. **Post-Mortem**: Document lessons learned

---

## 📊 Data Privacy Policy

### 1. **Data Collection**

#### What We Collect
- **Account Information**: Name, email, username
- **User Content**: Tasks, projects, journal entries
- **Usage Data**: Feature usage, session duration
- **Technical Data**: IP address, browser type
- **AI Interactions**: Queries and feedback

#### What We DON'T Collect
- Social Security Numbers
- Financial information (except payment processor)
- Health records (journal entries are private)
- Biometric data
- Third-party tracking cookies

### 2. **Data Usage**

#### How We Use Your Data
- **Service Provision**: Core app functionality
- **AI Improvement**: Anonymous pattern analysis
- **Communication**: Service updates, optional newsletters
- **Security**: Fraud prevention, abuse detection
- **Legal Compliance**: As required by law

#### How We DON'T Use Your Data
- Sell to third parties
- Behavioral advertising
- Train public AI models
- Share without consent

### 3. **Data Storage & Retention**

#### Storage Locations
- **Primary**: US-East (Virginia)
- **Backups**: US-West (Oregon)
- **CDN**: Global edge locations (static assets only)

#### Retention Periods
- **Active Account Data**: Duration of account + 30 days
- **Deleted Items**: 30-day soft delete, then permanent
- **Logs**: 90 days
- **Backups**: 30 days rolling
- **Closed Accounts**: 6 months, then anonymized

### 4. **Third-Party Services**

#### Service Providers
| Service | Purpose | Data Shared |
|---------|---------|-------------|
| Supabase | Database & Auth | All user data |
| Google | OAuth & AI | Email, AI queries |
| SendGrid | Email delivery | Email address |
| Stripe | Payments | Email, payment tokens |
| Cloudflare | CDN & DDoS | IP addresses |

#### Data Processing Agreements
- All providers are GDPR compliant
- Data Processing Agreements (DPAs) in place
- Annual security audits required

### 5. **User Rights**

#### GDPR Rights (EU Users)
- **Access**: Download all your data
- **Rectification**: Correct inaccurate data
- **Erasure**: Delete your account and data
- **Portability**: Export in machine-readable format
- **Restriction**: Limit processing of your data
- **Objection**: Opt-out of certain processing

#### CCPA Rights (California Users)
- **Know**: What personal information we collect
- **Delete**: Request deletion of personal information
- **Opt-Out**: Of sale of personal information (we don't sell)
- **Non-Discrimination**: Equal service regardless of privacy choices

#### How to Exercise Rights
- **In-App**: Settings → Privacy → Data Rights
- **Email**: privacy@aurumlife.com
- **Response Time**: Within 30 days

### 6. **AI & Machine Learning**

#### AI Data Usage
- **Personalization**: AI learns from your patterns
- **Isolation**: Each user's AI model is separate
- **No Cross-Training**: Your data never trains other users' models
- **Gemini API**: Queries are not stored by Google
- **Anonymization**: Aggregate insights only

#### AI Transparency
- **Explainable AI**: See why recommendations are made
- **Confidence Scores**: Understand AI certainty
- **Feedback Loop**: Correct AI mistakes
- **Opt-Out**: Disable AI features while keeping core functionality

### 7. **Children's Privacy**

- **Age Requirement**: 13+ years old (16+ in EU)
- **Parental Consent**: Required for users under 18
- **School Accounts**: Special privacy protections
- **No Targeted Ads**: Ever, for any age group

### 8. **International Data Transfers**

#### Transfer Mechanisms
- **Standard Contractual Clauses**: For EU data
- **Privacy Shield**: Where applicable
- **Adequacy Decisions**: Preferred when available

#### Your Location Options
- Choose data residency (coming soon)
- Local processing where possible
- Clear notice of cross-border transfers

### 9. **Cookies & Tracking**

#### Essential Cookies Only
- **Authentication**: Session management
- **Preferences**: Language, theme
- **Security**: CSRF tokens

#### No Tracking Cookies
- No Google Analytics
- No Facebook Pixel
- No advertising cookies
- No cross-site tracking

### 10. **Security Breach Notification**

#### Our Commitment
- **Detection**: Continuous monitoring
- **Assessment**: Immediate risk evaluation
- **Notification**: Within 72 hours if risk to users
- **Transparency**: Clear communication about impact
- **Remediation**: Free credit monitoring if warranted

#### What We'll Tell You
- What happened
- When it happened
- What data was affected
- What we're doing about it
- What you should do

---

## 🔒 Best Practices for Users

### Account Security
1. Use a strong, unique password
2. Enable two-factor authentication (when available)
3. Don't share your login credentials
4. Log out on shared devices
5. Keep your email account secure

### Data Safety
1. Regular backups (export feature)
2. Review sharing settings
3. Be cautious with AI prompts
4. Report suspicious activity
5. Keep app updated

---

## 📞 Contact Information

### Security Issues
- **Email**: security@aurumlife.com
- **PGP Key**: Available on website
- **Bug Bounty**: security.aurumlife.com/bugbounty

### Privacy Concerns
- **Email**: privacy@aurumlife.com
- **Privacy Officer**: Jamie Chen
- **Mailing Address**: [To be added]

### Data Protection Officer
- **Name**: [To be appointed]
- **Email**: dpo@aurumlife.com
- **Certification**: CIPP/E, CIPM

---

## 🔄 Policy Updates

- **Review Frequency**: Quarterly
- **Major Changes**: 30-day notice via email
- **Minor Changes**: Posted to website
- **Archive**: Previous versions available on request

---

## 🏛️ Compliance & Certifications

### Current Compliance
- [x] GDPR (General Data Protection Regulation)
- [x] CCPA (California Consumer Privacy Act)
- [x] PIPEDA (Canadian Privacy Law)
- [x] OWASP Top 10 Security Practices

### Planned Certifications
- [ ] SOC 2 Type II (2025)
- [ ] ISO 27001 (2025)
- [ ] HIPAA (if health features added)

---

By using Aurum Life, you agree to these security and privacy practices. We're committed to protecting your data as if it were our own.