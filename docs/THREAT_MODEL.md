# Threat Model — VANRAKSHA AI

## Assets

| Asset | Sensitivity |
|-------|-------------|
| Incident data (locations, evidence, risk scores) | HIGH |
| Camera feeds / evidence JPEGs | HIGH |
| Ranger locations / SOS signals | HIGH |
| User credentials (JWT, passwords) | CRITICAL |
| Model weights (ONNX) | MEDIUM |
| Configuration (risk weights, zones) | MEDIUM |

## Threats & Mitigations

| Threat | Likelihood | Impact | Mitigation |
|--------|------------|--------|------------|
| Stolen JWT / session hijack | Medium | High | Short expiry (8h), httpOnly cookies, HTTPS in prod, rotation |
| Evidence scraping (unauthenticated) | High | Medium | `restrict_evidence` flag, role-based access, audit logs |
| RTSP credential leak in logs | Low | High | URI redaction in metadata, no logging of passwords |
| Model theft (ONNX weights) | Low | Medium | Weights not in repo, Apache-2.0 model only |
| Log injection (fake events) | Medium | Medium | Structured JSON logs, request-id correlation, no raw payload in logs |
| Path traversal in evidence upload | Medium | High | SHA-256 naming, sharded dirs, no user-controlled paths |
| Insecure demo passwords | High (if deployed) | Critical | `DEMO_MODE` flag, `SECRET_KEY` check, prod deploy docs |
| SQL injection | Low | High | SQLAlchemy ORM, parameterized queries |
| XSS via event payloads | Low | Medium | Content-Type validation, no HTML rendering of payloads |
| DoS via ingest API | Medium | Medium | Rate limit on `/auth/login`, job queue limits |

## Controls Implemented

- **Authentication**: JWT HS256, bcrypt passwords, 8h expiry, httpOnly cookies
- **Authorization**: 4-role RBAC (ADMIN, FOREST_OFFICER, RANGER, VIEWER) on all mutating endpoints
- **Rate limiting**: Login 5/min/IP (in-memory token bucket)
- **Input validation**: Pydantic models on all endpoints
- **Audit logging**: All state changes, evidence access, auth events
- **Evidence integrity**: SHA-256 on all stored files, content-addressed storage
- **Secrets management**: `.env` file (gitignored), `SECRET_KEY` minimum length enforcement
- **CORS**: Restricted to configured origins
- **Security headers**: CSP, X-Frame-Options, X-Content-Type-Options via Next.js

## Residual Risks

- In-memory rate limiter doesn't scale to multi-instance (acceptable for MVP single-node)
- No WAF / DDoS protection at network level
- Evidence files served via direct file paths (no signed URLs)
- Demo mode uses weak default password (documented, not for production)

## Out of Scope for MVP

- Hardware security modules
- Hardware-backed key storage
- Formal penetration testing
- SOC 2 / ISO 27001 compliance
- Advanced persistent threat detection