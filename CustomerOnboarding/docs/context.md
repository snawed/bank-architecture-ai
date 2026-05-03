# Customer Onboarding – Domain Context

## 1. Business Overview
Digital bank onboarding journey for retail and SME customers.
Goal is to allow customers to open an account digitally via mobile/web.

## 2. Actors
- Customer (Retail / SME)
- Bank Operations Team
- Compliance Team

## 3. Channels
- Mobile App
- Web Application

## 4. Core Processes
- User registration
- Identity verification (KYC)
- AML screening
- Document upload and validation
- Account creation
- Notifications (SMS/Email)

## 5. External Systems
- Identity Provider (e.g., Nafath, Yoti, etc.)
- AML/KYC vendors
- Core Banking System
- Notification service (SMS/Email gateway)

## 6. Internal Systems (Target)
- Onboarding Service
- KYC Service
- AML Service
- Document Management Service
- Notification Service
- Audit & Logging Service

## 7. Key Constraints
- Must comply with PCI DSS, ISO 27001
- Full audit trail required
- Secure identity verification (MFA / biometrics)
- Data encryption in transit and at rest
- Regulatory compliance (BAM / FCA style)

## 8. High-Level Flow
1. Customer initiates onboarding via mobile/web
2. Identity verification via external provider
3. KYC + AML checks performed
4. Documents validated
5. Account created in Core Banking
6. Customer notified

## 9. Non-Functional Requirements
- High availability (24/7)
- Scalable onboarding volume
- Low latency for customer interactions
- Observability (logs, metrics, tracing)