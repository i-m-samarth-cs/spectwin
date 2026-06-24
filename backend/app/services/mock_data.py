"""Realistic mock data for demo mode - 3 projects with artifacts, issues, twin graphs."""
from uuid import uuid4
from datetime import datetime, timedelta
import random

def _uuid():
    return str(uuid4())

NOW = datetime.utcnow()

PROJECTS = [
    {
        "id": "a1b2c3d4-0001-0001-0001-000000000001",
        "name": "Payments Platform v3",
        "description": "Redesign of the core payments processing pipeline with real-time fraud detection and multi-currency support.",
        "status": "ready",
        "release_readiness_score": 62.0,
        "open_issues_count": 8,
        "artifact_count": 12,
        "created_at": (NOW - timedelta(days=14)).isoformat(),
        "updated_at": NOW.isoformat(),
    },
    {
        "id": "a1b2c3d4-0002-0002-0002-000000000002",
        "name": "Auth & Identity Service",
        "description": "SSO, MFA, and role-based access control overhaul to support enterprise customers.",
        "status": "analyzing",
        "release_readiness_score": 41.0,
        "open_issues_count": 14,
        "artifact_count": 9,
        "created_at": (NOW - timedelta(days=7)).isoformat(),
        "updated_at": NOW.isoformat(),
    },
    {
        "id": "a1b2c3d4-0003-0003-0003-000000000003",
        "name": "Notification Engine",
        "description": "Unified notification delivery system with templating, scheduling, and preference management.",
        "status": "ready",
        "release_readiness_score": 78.0,
        "open_issues_count": 4,
        "artifact_count": 7,
        "created_at": (NOW - timedelta(days=21)).isoformat(),
        "updated_at": NOW.isoformat(),
    },
]

ARTIFACTS = {
    "a1b2c3d4-0001-0001-0001-000000000001": [
        {
            "id": _uuid(), "artifact_type": "prd", "title": "Payments Platform v3 PRD",
            "status": "indexed",
            "raw_content": """# Payments Platform v3 - Product Requirements Document

## Overview
The Payments Platform v3 will redesign our core payment processing pipeline to support real-time fraud detection, multi-currency transactions, and instant settlement for premium merchants.

## Goals
- Process payments in < 200ms (p99)
- Support 50+ currencies with live exchange rates
- Fraud detection accuracy > 99.2%
- Instant settlement for Tier-1 merchants

## Requirements
REQ-001: The system SHALL process all payment transactions within 200ms at p99 latency.
REQ-002: The system SHALL support a minimum of 50 currencies using live exchange rate feeds.
REQ-003: The fraud detection model SHALL achieve a minimum accuracy of 99.2% on the validation set.
REQ-004: Instant settlement SHALL be available to merchants on the Premium tier only.
REQ-005: The refund API SHALL process refunds within 24 hours.
REQ-006: The system SHALL maintain 99.99% uptime SLA.
REQ-007: All payment data SHALL be encrypted at rest using AES-256.
REQ-008: The system SHALL support webhook notifications for all payment state changes.

## Out of Scope
- Cryptocurrency payments
- Subscription billing (handled by Billing Service)

## Acceptance Criteria
- Payment processing p99 < 200ms under 10k TPS load
- All 50+ currency pairs tested with live rate feeds
- Fraud model evaluated on holdout set monthly""",
            "parsed_content": {"requirements": 8, "parsed": True},
        },
        {
            "id": _uuid(), "artifact_type": "ticket", "title": "PAY-1042: Instant Settlement for All Tiers",
            "status": "indexed",
            "raw_content": """TICKET: PAY-1042
Title: Enable instant settlement for all merchant tiers
Status: In Progress
Assignee: Jordan Lee
Priority: High

Description:
As discussed in the Q3 planning call, instant settlement should be rolled out to ALL merchant tiers, not just Premium. The product team confirmed this in Slack on Sept 12.

Acceptance Criteria:
- Instant settlement enabled for Basic, Standard, and Premium tiers
- Settlement latency < 5 seconds
- Configurable per-merchant in admin panel

Notes: Jordan mentioned that the PRD says Premium only but the PM confirmed the scope was expanded.""",
            "parsed_content": {"ticket_id": "PAY-1042", "status": "In Progress"},
        },
        {
            "id": _uuid(), "artifact_type": "discussion", "title": "Slack: Fraud threshold discussion",
            "status": "indexed",
            "raw_content": """Slack #payments-eng, Sept 14

Jordan Lee [10:22 AM]: Quick Q - the PRD says fraud accuracy > 99.2% but the ML team said they can only hit 98.8% on the new model. Should we adjust the threshold?

Alex Chen [10:35 AM]: Yeah let's lower it to 98.5% for now and revisit in Q4. The model will improve.

Morgan Davis [10:41 AM]: Wait, compliance requires 99% minimum for PCI-DSS Level 1. We can't go below that.

Jordan Lee [10:44 AM]: So we're stuck? The PRD says 99.2 but ML says 98.8 and compliance says 99.0 minimum.

Alex Chen [10:47 AM]: Let's just ship with 98.8 and not mention it in the release notes. We'll fix it quietly.

Riley Kim [11:02 AM]: That's not okay from a governance standpoint. We need to flag this as a blocker.""",
            "parsed_content": {"participants": ["Jordan Lee", "Alex Chen", "Morgan Davis", "Riley Kim"]},
        },
        {
            "id": _uuid(), "artifact_type": "api_spec", "title": "Payments API v3 OpenAPI Spec",
            "status": "indexed",
            "raw_content": """openapi: 3.0.0
info:
  title: Payments API v3
  version: 3.0.0-beta

paths:
  /v3/payments:
    post:
      summary: Create payment
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [amount, currency, merchant_id]
              properties:
                amount: {type: integer, description: "Amount in minor units"}
                currency: {type: string, description: "ISO 4217 currency code"}
                merchant_id: {type: string}
                settlement_tier: {type: string, enum: [instant, standard], description: "All tiers now support instant"}
      responses:
        '200':
          description: Payment created

  /v3/refunds:
    post:
      summary: Create refund
      description: Refunds are processed within 48 hours (updated SLA)
      requestBody:
        content:
          application/json:
            schema:
              type: object
              required: [payment_id, amount]
              properties:
                payment_id: {type: string}
                amount: {type: integer}""",
            "parsed_content": {"endpoints": ["/v3/payments", "/v3/refunds"]},
        },
        {
            "id": _uuid(), "artifact_type": "code_change", "title": "PR #887: Settlement tier logic",
            "status": "indexed",
            "raw_content": """PR #887: Remove tier restriction on instant settlement
Author: Jordan Lee
Files changed: settlement_service.py, merchant_config.py, README.md

Diff summary:
- Removed `if merchant.tier == 'premium'` check from instant_settle()
- All merchants now eligible for instant settlement regardless of tier
- Updated merchant_config default: settlement_mode = 'instant'
- No documentation update made to PRD or product wiki
- Tests updated to reflect new behavior but acceptance criteria not updated

Merged: Sept 15, 23:47""",
            "parsed_content": {"pr_number": "887", "files_changed": 3},
        },
        {
            "id": _uuid(), "artifact_type": "test_case", "title": "Payment processing test suite",
            "status": "indexed",
            "raw_content": """Test Suite: Payments v3 Core
Last run: Sept 16

TC-001: Payment processing latency
  Status: PASS | p99: 187ms

TC-002: Multi-currency support (47 currencies tested)
  Status: PARTIAL - 3 currencies (IRR, MMK, SYP) not implemented

TC-003: Fraud detection accuracy
  Status: FAIL | Actual: 98.8% | Required: 99.2%

TC-004: Instant settlement - Premium tier
  Status: PASS

TC-005: Instant settlement - Basic tier
  Status: NOT WRITTEN - feature added in PR #887 but no tests

TC-006: Refund processing time
  Status: PASS | Actual: 31 hours | SLA: 24 hours [WARN: borderline]

TC-007: Webhook delivery
  Status: PASS""",
            "parsed_content": {"total": 7, "passing": 4, "failing": 1, "missing": 1},
        },
        {
            "id": _uuid(), "artifact_type": "release_note", "title": "Payments v3 Release Notes Draft",
            "status": "indexed",
            "raw_content": """# Payments Platform v3 - Release Notes

## New Features
- Multi-currency support for 50 currencies
- Real-time fraud detection (accuracy: 99.2%)
- Instant settlement for Premium merchants
- Webhook notifications for all payment events

## Performance
- Payment processing: < 200ms p99

## Bug Fixes
- Fixed edge case in refund calculation for partial captures

## Known Issues
- None""",
            "parsed_content": {"version": "3.0.0"},
        },
    ],
    "a1b2c3d4-0002-0002-0002-000000000002": [
        {
            "id": _uuid(), "artifact_type": "prd", "title": "Auth & Identity Service PRD",
            "status": "indexed",
            "raw_content": """# Auth & Identity Service - PRD

## Objective
Replace legacy auth system with enterprise-grade SSO, MFA, and RBAC to support enterprise customers and SOC 2 Type II compliance.

## Requirements
REQ-AUTH-001: Support SAML 2.0 and OIDC protocols for SSO.
REQ-AUTH-002: MFA SHALL be enforced for all admin-role users.
REQ-AUTH-003: MFA SHALL be optional (user-configurable) for non-admin roles.
REQ-AUTH-004: Session tokens SHALL expire after 8 hours of inactivity.
REQ-AUTH-005: Failed login attempts SHALL be rate-limited to 5 per minute per IP.
REQ-AUTH-006: The system SHALL maintain a full audit log of all auth events.
REQ-AUTH-007: Role changes SHALL require approval from an engineering_manager or admin.
REQ-AUTH-008: The system SHALL support a minimum of 10,000 concurrent sessions.""",
            "parsed_content": {"requirements": 8},
        },
        {
            "id": _uuid(), "artifact_type": "ticket", "title": "AUTH-204: MFA bypass for service accounts",
            "status": "indexed",
            "raw_content": """TICKET: AUTH-204
Title: Add MFA bypass flag for service accounts
Assignee: Jordan Lee
Status: Done

Description:
Service accounts used in CI/CD pipelines cannot use MFA. Add a bypass flag that disables MFA enforcement for accounts tagged as service_account type.

No additional approval needed - Taylor (admin) verbally approved.
No documentation update required per Jordan's judgment.

Implementation: Added `skip_mfa: bool` field to User model. When true, MFA check is skipped entirely regardless of role.""",
            "parsed_content": {"ticket_id": "AUTH-204"},
        },
        {
            "id": _uuid(), "artifact_type": "discussion", "title": "Teams: Session timeout debate",
            "status": "indexed",
            "raw_content": """Teams channel: #auth-redesign, Sept 10

Alex Chen: PRD says 8 hours session timeout. But enterprise customers are complaining - their users get logged out during long meetings. Can we make it 24 hours?

Jordan Lee: Let's just make it configurable per tenant. Default 8h, enterprise can set up to 72h.

Morgan Davis: 72 hours seems excessive from a security standpoint. What does compliance say?

Riley Kim: I checked with legal - anything over 24h requires explicit security exception sign-off.

Alex Chen: Let's just implement 24h default and not document the tenant config option for now.

Jordan Lee: Done - I've already shipped 24h default in the main branch. The tenant config option lets admins set any value from 1h to 168h (7 days).""",
            "parsed_content": {"participants": ["Alex Chen", "Jordan Lee", "Morgan Davis", "Riley Kim"]},
        },
    ],
    "a1b2c3d4-0003-0003-0003-000000000003": [
        {
            "id": _uuid(), "artifact_type": "prd", "title": "Notification Engine PRD",
            "status": "indexed",
            "raw_content": """# Notification Engine - PRD

## Overview
Unified multi-channel notification delivery with templating, user preferences, and delivery scheduling.

## Requirements
REQ-NOTIF-001: Support email, SMS, push, and in-app notification channels.
REQ-NOTIF-002: Users SHALL be able to set per-channel notification preferences.
REQ-NOTIF-003: Notifications SHALL support Jinja2-style templating.
REQ-NOTIF-004: Scheduled notifications SHALL be delivered within 60 seconds of the scheduled time.
REQ-NOTIF-005: The system SHALL retry failed deliveries up to 3 times with exponential backoff.
REQ-NOTIF-006: Delivery receipts SHALL be stored for 90 days.
REQ-NOTIF-007: The system SHALL support bulk send for up to 100,000 recipients per campaign.""",
            "parsed_content": {"requirements": 7},
        },
        {
            "id": _uuid(), "artifact_type": "test_case", "title": "Notification Engine test suite",
            "status": "indexed",
            "raw_content": """Test Suite: Notification Engine
Last run: Sept 17

TC-NOTIF-001: Email delivery - PASS
TC-NOTIF-002: SMS delivery - PASS
TC-NOTIF-003: Push notifications - PASS
TC-NOTIF-004: In-app notifications - PASS
TC-NOTIF-005: User preference management - PASS
TC-NOTIF-006: Template rendering (Jinja2) - PASS
TC-NOTIF-007: Scheduled delivery accuracy - PASS (avg: 12s)
TC-NOTIF-008: Retry logic - PASS
TC-NOTIF-009: Bulk send (100k recipients) - PASS (3m 42s)
TC-NOTIF-010: Delivery receipt storage - PASS

Coverage: 100% of documented requirements""",
            "parsed_content": {"total": 10, "passing": 10},
        },
    ],
}

DRIFT_ISSUES = {
    "a1b2c3d4-0001-0001-0001-000000000001": [
        {
            "id": _uuid(),
            "title": "Instant settlement scope contradicts PRD",
            "description": "PRD (REQ-004) restricts instant settlement to Premium tier merchants. Ticket PAY-1042 and PR #887 expand this to all tiers without a PRD update. The API spec also reflects the expanded scope ('All tiers now support instant') but release notes still state 'Premium merchants only'.",
            "category": "contradictory_requirement",
            "severity": "critical",
            "status": "open",
            "confidence": 0.97,
            "evidence": {
                "prd_statement": "Instant settlement SHALL be available to merchants on the Premium tier only. (REQ-004)",
                "ticket_statement": "instant settlement should be rolled out to ALL merchant tiers, not just Premium",
                "code_statement": "Removed if merchant.tier == 'premium' check from instant_settle()",
                "api_statement": "All tiers now support instant",
                "release_note_statement": "Instant settlement for Premium merchants",
            },
            "suggested_action": "Resolve the tier scope conflict: update PRD and release notes to reflect all-tier instant settlement, OR revert PR #887 to restore Premium-only restriction. Either way, requires PM and engineering sign-off.",
            "linked_artifact_ids": [],
            "reasoning": "Four artifacts contradict each other on a key business rule. The code has already shipped the expanded behavior but the PRD and release notes have not been updated.",
            "agent_name": "ContradictionDetectionAgent",
        },
        {
            "id": _uuid(),
            "title": "Fraud accuracy threshold contradicts PRD, ticket, compliance, and release notes",
            "description": "PRD requires 99.2% fraud accuracy. ML team achieved 98.8%. Compliance requires 99.0% minimum (PCI-DSS). Slack discussion shows a proposal to ship at 98.8% without documenting. Release notes falsely state 99.2%.",
            "category": "contradictory_requirement",
            "severity": "critical",
            "status": "open",
            "confidence": 0.99,
            "evidence": {
                "prd_statement": "Fraud detection accuracy > 99.2% (REQ-003)",
                "test_result": "TC-003: FAIL | Actual: 98.8%",
                "compliance_statement": "compliance requires 99% minimum for PCI-DSS Level 1",
                "release_note_claim": "Real-time fraud detection (accuracy: 99.2%)",
                "discussion": "Let's just ship with 98.8 and not mention it in the release notes",
            },
            "suggested_action": "BLOCK release. Fraud accuracy does not meet PRD, compliance, or stated release note figures. Requires ML team resolution or formal exception from compliance.",
            "linked_artifact_ids": [],
            "reasoning": "Test evidence contradicts PRD requirement, compliance floor, and published release note. Release note contains a factual inaccuracy about a safety-critical metric.",
            "agent_name": "ContradictionDetectionAgent",
        },
        {
            "id": _uuid(),
            "title": "Refund SLA discrepancy: PRD says 24h, API spec says 48h",
            "description": "REQ-005 states refunds must be processed within 24 hours. The API spec description states 'Refunds are processed within 48 hours (updated SLA)'. Test TC-006 shows actual time of 31 hours — passing the 48h SLA but failing the 24h PRD requirement.",
            "category": "contradictory_requirement",
            "severity": "high",
            "status": "open",
            "confidence": 0.94,
            "evidence": {
                "prd_statement": "The refund API SHALL process refunds within 24 hours. (REQ-005)",
                "api_statement": "Refunds are processed within 48 hours (updated SLA)",
                "test_result": "TC-006: PASS | Actual: 31 hours | SLA: 24 hours [WARN: borderline]",
            },
            "suggested_action": "Determine authoritative SLA. If 48h is the accepted change, update PRD and ensure test TC-006 uses 48h threshold. If 24h is still required, fix the API spec and investigate the 31h actual time.",
            "linked_artifact_ids": [],
            "reasoning": "PRD and API spec disagree on a contractual SLA. Test is evaluating against neither — using 24h threshold but actual time of 31h is marked WARN rather than FAIL.",
            "agent_name": "ContradictionDetectionAgent",
        },
        {
            "id": _uuid(),
            "title": "Instant settlement behavior (PR #887) not documented",
            "description": "PR #887 changed instant settlement from Premium-only to all-tier without updating PRD, product wiki, or internal documentation. This is a significant behavioral change shipped without documentation.",
            "category": "undocumented_change",
            "severity": "high",
            "status": "open",
            "confidence": 0.96,
            "evidence": {
                "code_change": "No documentation update made to PRD or product wiki",
                "pr_note": "Merged: Sept 15, 23:47 — documentation not updated",
            },
            "suggested_action": "Update PRD, API documentation, and release notes to reflect the all-tier instant settlement change, or create a follow-up ticket for documentation debt.",
            "linked_artifact_ids": [],
            "reasoning": "Code diff explicitly notes no documentation update was made for a user-facing behavioral change.",
            "agent_name": "DocCodeDriftAgent",
        },
        {
            "id": _uuid(),
            "title": "Missing tests for all-tier instant settlement (PR #887)",
            "description": "PR #887 enabled instant settlement for Basic and Standard tiers but TC-005 ('Instant settlement - Basic tier') is listed as NOT WRITTEN. Only the Premium tier test (TC-004) was inherited.",
            "category": "missing_test",
            "severity": "high",
            "status": "open",
            "confidence": 0.98,
            "evidence": {
                "code_change": "All merchants now eligible for instant settlement",
                "test_status": "TC-005: NOT WRITTEN - feature added in PR #887 but no tests",
            },
            "suggested_action": "Write test cases for Basic and Standard tier instant settlement before release.",
            "linked_artifact_ids": [],
            "reasoning": "New behavior added in code with no corresponding test coverage.",
            "agent_name": "TestGapAgent",
        },
        {
            "id": _uuid(),
            "title": "Currency coverage gap: 47 of 50 currencies tested",
            "description": "REQ-002 requires 50+ currency support. Tests show only 47 currencies implemented — IRR, MMK, and SYP are missing.",
            "category": "missing_acceptance_criteria",
            "severity": "medium",
            "status": "open",
            "confidence": 0.93,
            "evidence": {
                "prd_requirement": "Support a minimum of 50 currencies (REQ-002)",
                "test_result": "TC-002: PARTIAL - 3 currencies (IRR, MMK, SYP) not implemented",
            },
            "suggested_action": "Implement IRR, MMK, and SYP currency support before marking REQ-002 as satisfied.",
            "linked_artifact_ids": [],
            "reasoning": "Test evidence shows 3 required currencies are unimplemented.",
            "agent_name": "TestGapAgent",
        },
        {
            "id": _uuid(),
            "title": "Release notes state 99.2% fraud accuracy — factually incorrect",
            "description": "Release notes claim fraud detection accuracy of 99.2%, which is the PRD target. Actual measured accuracy per TC-003 is 98.8%. Publishing false accuracy figures for a fraud detection system is a compliance and trust risk.",
            "category": "release_mismatch",
            "severity": "critical",
            "status": "open",
            "confidence": 0.99,
            "evidence": {
                "release_note": "Real-time fraud detection (accuracy: 99.2%)",
                "test_result": "TC-003: FAIL | Actual: 98.8%",
            },
            "suggested_action": "Correct release notes immediately. Do not publish inaccurate technical specifications.",
            "linked_artifact_ids": [],
            "reasoning": "Direct contradiction between published release notes and test evidence.",
            "agent_name": "ReleaseRiskAgent",
        },
        {
            "id": _uuid(),
            "title": "Fraud threshold decision undocumented and informally escalated",
            "description": "Slack discussion (Sept 14) shows a proposal to ship below PRD and compliance thresholds. Riley Kim flagged this as requiring escalation but no follow-up ticket was created and the decision was not formally recorded.",
            "category": "unclear_ownership",
            "severity": "high",
            "status": "open",
            "confidence": 0.88,
            "evidence": {
                "discussion": "Riley Kim: That's not okay from a governance standpoint. We need to flag this as a blocker.",
                "follow_up": "No ticket or decision record found",
            },
            "suggested_action": "Create a formal decision record for the fraud threshold. Assign an owner (PM or engineering manager) to resolve before release.",
            "linked_artifact_ids": [],
            "reasoning": "Critical compliance decision was discussed informally with no owner assigned and no resolution recorded.",
            "agent_name": "AmbiguityDetectionAgent",
        },
    ],
    "a1b2c3d4-0002-0002-0002-000000000002": [
        {
            "id": _uuid(),
            "title": "Session timeout contradicts PRD: shipped as 24h, PRD requires 8h",
            "description": "REQ-AUTH-004 specifies 8-hour session timeout. Discussion shows this was changed to 24h (and tenant-configurable up to 168h/7 days) and shipped without PRD update.",
            "category": "contradictory_requirement",
            "severity": "critical",
            "status": "open",
            "confidence": 0.96,
            "evidence": {
                "prd_statement": "Session tokens SHALL expire after 8 hours of inactivity. (REQ-AUTH-004)",
                "shipped_behavior": "24h default with tenant config up to 168h",
                "compliance_note": "anything over 24h requires explicit security exception sign-off",
            },
            "suggested_action": "Update PRD to reflect 24h default, obtain security exception sign-off for >24h tenant config, document the configurable range.",
            "linked_artifact_ids": [],
            "reasoning": "Shipped session timeout is 3x the PRD requirement. Extended tenant config may require compliance sign-off.",
            "agent_name": "ContradictionDetectionAgent",
        },
        {
            "id": _uuid(),
            "title": "MFA bypass for service accounts undocumented and unapproved",
            "description": "REQ-AUTH-002 mandates MFA for all admin roles. AUTH-204 added a skip_mfa bypass flag without formal approval or documentation. The verbal approval from Taylor (admin) is not a documented exception.",
            "category": "undocumented_change",
            "severity": "critical",
            "status": "open",
            "confidence": 0.97,
            "evidence": {
                "prd_requirement": "MFA SHALL be enforced for all admin-role users (REQ-AUTH-002)",
                "implementation": "Added skip_mfa: bool field. When true, MFA check is skipped entirely regardless of role.",
                "approval": "Taylor (admin) verbally approved",
                "ticket_note": "No documentation update required per Jordan's judgment",
            },
            "suggested_action": "Create formal security exception for service account MFA bypass. Document which accounts are eligible. Ensure this is captured in security architecture docs and SOC 2 evidence.",
            "linked_artifact_ids": [],
            "reasoning": "Security control (MFA enforcement) was bypassed without documented authorization, creating a potential SOC 2 compliance gap.",
            "agent_name": "DocCodeDriftAgent",
        },
        {
            "id": _uuid(),
            "title": "Tenant session config (1h-168h) not documented anywhere",
            "description": "Tenant session timeout configuration (1h to 168h range) was implemented and shipped but not mentioned in PRD, API spec, release notes, or any documentation.",
            "category": "undocumented_change",
            "severity": "high",
            "status": "open",
            "confidence": 0.91,
            "evidence": {
                "discussion": "tenant config option lets admins set any value from 1h to 168h (7 days)",
                "documentation": "No reference found in PRD, API spec, or release notes",
            },
            "suggested_action": "Add tenant session configuration to API spec, admin documentation, and release notes.",
            "linked_artifact_ids": [],
            "reasoning": "Tenant-configurable session timeout was discussed informally and shipped without any documentation.",
            "agent_name": "DocCodeDriftAgent",
        },
    ],
    "a1b2c3d4-0003-0003-0003-000000000003": [
        {
            "id": _uuid(),
            "title": "REQ-NOTIF-006: Delivery receipt retention period ambiguous",
            "description": "REQ-NOTIF-006 states receipts SHALL be stored for 90 days but does not specify whether this is calendar days, business days, or rolling window. Tests pass but acceptance criteria are underspecified.",
            "category": "ambiguous_requirement",
            "severity": "low",
            "status": "open",
            "confidence": 0.82,
            "evidence": {
                "prd_statement": "Delivery receipts SHALL be stored for 90 days (REQ-NOTIF-006)",
                "ambiguity": "No specification of calendar vs business days, no storage format spec, no deletion audit requirement",
            },
            "suggested_action": "Clarify REQ-NOTIF-006: specify calendar days, define retention window trigger (delivery time vs creation time), and add audit logging requirement for deletion.",
            "linked_artifact_ids": [],
            "reasoning": "Requirement uses vague temporal language that could lead to implementation disagreements.",
            "agent_name": "AmbiguityDetectionAgent",
        },
    ],
}

TWIN_GRAPHS = {
    "a1b2c3d4-0001-0001-0001-000000000001": {
        "nodes": [
            {"id": "n1", "node_type": "feature", "label": "Instant Settlement", "confidence": 1.0, "x": 200, "y": 100},
            {"id": "n2", "node_type": "requirement", "label": "REQ-004: Premium-only settlement", "confidence": 1.0, "x": 100, "y": 250},
            {"id": "n3", "node_type": "requirement", "label": "REQ-003: Fraud accuracy 99.2%", "confidence": 1.0, "x": 400, "y": 100},
            {"id": "n4", "node_type": "implementation_change", "label": "PR #887: All-tier settlement", "confidence": 1.0, "x": 200, "y": 400},
            {"id": "n5", "node_type": "api_contract", "label": "POST /v3/payments (all tiers)", "confidence": 1.0, "x": 350, "y": 280},
            {"id": "n6", "node_type": "test_artifact", "label": "TC-003: Fraud accuracy (FAIL)", "confidence": 1.0, "x": 550, "y": 200},
            {"id": "n7", "node_type": "test_artifact", "label": "TC-005: Basic tier settlement (MISSING)", "confidence": 1.0, "x": 100, "y": 450},
            {"id": "n8", "node_type": "release_issue", "label": "Release note: 99.2% claim", "confidence": 1.0, "x": 600, "y": 100},
            {"id": "n9", "node_type": "requirement", "label": "REQ-002: 50 currencies", "confidence": 1.0, "x": 550, "y": 380},
            {"id": "n10", "node_type": "constraint", "label": "PCI-DSS: 99% fraud floor", "confidence": 0.95, "x": 400, "y": 50},
        ],
        "edges": [
            {"id": "e1", "source_node_id": "n4", "target_node_id": "n2", "edge_type": "contradicts", "confidence": 0.97},
            {"id": "e2", "source_node_id": "n4", "target_node_id": "n5", "edge_type": "implements", "confidence": 0.9},
            {"id": "e3", "source_node_id": "n7", "target_node_id": "n4", "edge_type": "tests", "confidence": 0.98},
            {"id": "e4", "source_node_id": "n6", "target_node_id": "n3", "edge_type": "contradicts", "confidence": 0.99},
            {"id": "e5", "source_node_id": "n8", "target_node_id": "n3", "edge_type": "contradicts", "confidence": 0.99},
            {"id": "e6", "source_node_id": "n10", "target_node_id": "n3", "edge_type": "contradicts", "confidence": 0.95},
            {"id": "e7", "source_node_id": "n1", "target_node_id": "n2", "edge_type": "depends_on", "confidence": 1.0},
            {"id": "e8", "source_node_id": "n1", "target_node_id": "n4", "edge_type": "introduced_in", "confidence": 0.9},
        ],
    },
    "a1b2c3d4-0002-0002-0002-000000000002": {
        "nodes": [
            {"id": "n1", "node_type": "feature", "label": "MFA Enforcement", "confidence": 1.0, "x": 200, "y": 100},
            {"id": "n2", "node_type": "requirement", "label": "REQ-AUTH-002: MFA for all admins", "confidence": 1.0, "x": 100, "y": 250},
            {"id": "n3", "node_type": "implementation_change", "label": "AUTH-204: skip_mfa bypass", "confidence": 1.0, "x": 300, "y": 300},
            {"id": "n4", "node_type": "requirement", "label": "REQ-AUTH-004: 8h session timeout", "confidence": 1.0, "x": 500, "y": 100},
            {"id": "n5", "node_type": "implementation_change", "label": "Session: 24h default + 168h config", "confidence": 1.0, "x": 500, "y": 280},
            {"id": "n6", "node_type": "constraint", "label": "Security: >24h needs exception", "confidence": 0.9, "x": 650, "y": 180},
        ],
        "edges": [
            {"id": "e1", "source_node_id": "n3", "target_node_id": "n2", "edge_type": "contradicts", "confidence": 0.97},
            {"id": "e2", "source_node_id": "n5", "target_node_id": "n4", "edge_type": "contradicts", "confidence": 0.96},
            {"id": "e3", "source_node_id": "n5", "target_node_id": "n6", "edge_type": "contradicts", "confidence": 0.9},
            {"id": "e4", "source_node_id": "n1", "target_node_id": "n2", "edge_type": "implements", "confidence": 1.0},
        ],
    },
    "a1b2c3d4-0003-0003-0003-000000000003": {
        "nodes": [
            {"id": "n1", "node_type": "feature", "label": "Notification Delivery", "confidence": 1.0, "x": 200, "y": 100},
            {"id": "n2", "node_type": "requirement", "label": "REQ-NOTIF-006: 90-day receipts", "confidence": 1.0, "x": 200, "y": 280},
            {"id": "n3", "node_type": "test_artifact", "label": "TC-NOTIF-010: Receipt storage (PASS)", "confidence": 1.0, "x": 400, "y": 280},
            {"id": "n4", "node_type": "requirement", "label": "REQ-NOTIF-007: 100k bulk send", "confidence": 1.0, "x": 400, "y": 100},
        ],
        "edges": [
            {"id": "e1", "source_node_id": "n3", "target_node_id": "n2", "edge_type": "tests", "confidence": 0.82},
            {"id": "e2", "source_node_id": "n1", "target_node_id": "n4", "edge_type": "implements", "confidence": 1.0},
        ],
    },
}

RELEASE_READINESS = {
    "a1b2c3d4-0001-0001-0001-000000000001": {
        "score": 32.0,
        "grade": "F",
        "unresolved_critical": 3,
        "unresolved_high": 4,
        "missing_tests": 1,
        "missing_docs": 2,
        "api_mismatches": 2,
        "scope_drift_count": 3,
        "executive_summary": "Payments Platform v3 is NOT ready for release. Three critical issues require resolution: (1) fraud accuracy does not meet PRD or PCI-DSS requirements and release notes contain a factual inaccuracy on this metric, (2) instant settlement scope is contradictory across PRD, code, API spec, and release notes, (3) refund SLA is inconsistent between PRD and API contract. Release should be blocked until these are resolved.",
        "risk_items": [
            {"title": "Fraud accuracy below compliance floor", "severity": "critical", "blocker": True},
            {"title": "Release notes contain false accuracy claim", "severity": "critical", "blocker": True},
            {"title": "Instant settlement scope undefined across artifacts", "severity": "critical", "blocker": True},
            {"title": "Missing tests for all-tier instant settlement", "severity": "high", "blocker": False},
            {"title": "Refund SLA contradiction (PRD vs API spec)", "severity": "high", "blocker": False},
        ],
    },
    "a1b2c3d4-0002-0002-0002-000000000002": {
        "score": 41.0,
        "grade": "D",
        "unresolved_critical": 2,
        "unresolved_high": 1,
        "missing_tests": 0,
        "missing_docs": 2,
        "api_mismatches": 1,
        "scope_drift_count": 2,
        "executive_summary": "Auth & Identity Service has significant documentation and compliance gaps. MFA bypass was shipped without formal authorization record, creating potential SOC 2 audit exposure. Session timeout is 3x the PRD requirement with undocumented tenant configuration. Both issues require remediation before enterprise customer rollout.",
        "risk_items": [
            {"title": "MFA bypass without formal security exception", "severity": "critical", "blocker": True},
            {"title": "Session timeout exceeds PRD requirement", "severity": "critical", "blocker": True},
            {"title": "Undocumented tenant session configuration", "severity": "high", "blocker": False},
        ],
    },
    "a1b2c3d4-0003-0003-0003-000000000003": {
        "score": 87.0,
        "grade": "B+",
        "unresolved_critical": 0,
        "unresolved_high": 0,
        "missing_tests": 0,
        "missing_docs": 0,
        "api_mismatches": 0,
        "scope_drift_count": 0,
        "executive_summary": "Notification Engine is in good shape for release. All requirements are implemented and tested with full coverage. One low-severity ambiguity exists in REQ-NOTIF-006 (retention period definition) that should be clarified in the next sprint but does not block release.",
        "risk_items": [
            {"title": "REQ-NOTIF-006 retention period underspecified", "severity": "low", "blocker": False},
        ],
    },
}

def get_mock_projects():
    return PROJECTS

def get_mock_artifacts(project_id: str):
    return ARTIFACTS.get(project_id, [])

def get_mock_issues(project_id: str):
    return DRIFT_ISSUES.get(project_id, [])

def get_mock_twin(project_id: str):
    return TWIN_GRAPHS.get(project_id, {"nodes": [], "edges": []})

def get_mock_release_readiness(project_id: str):
    return RELEASE_READINESS.get(project_id, {
        "score": 50.0, "grade": "C", "unresolved_critical": 0, "unresolved_high": 0,
        "missing_tests": 0, "missing_docs": 0, "api_mismatches": 0, "scope_drift_count": 0,
        "executive_summary": "No analysis available yet.", "risk_items": []
    })

ADMIN_METRICS = {
    "total_projects": 3,
    "total_artifacts": 28,
    "total_issues": 12,
    "issues_by_category": {
        "contradictory_requirement": 5,
        "undocumented_change": 4,
        "missing_test": 1,
        "ambiguous_requirement": 1,
        "release_mismatch": 1,
    },
    "issues_by_severity": {
        "critical": 5,
        "high": 5,
        "medium": 1,
        "low": 1,
    },
    "avg_release_readiness": 53.3,
    "model_runs": 47,
    "avg_latency_ms": 124.0,
    "drift_trend": [
        {"month": "Jul", "issues": 4},
        {"month": "Aug", "issues": 7},
        {"month": "Sep", "issues": 12},
    ],
    "readiness_distribution": [
        {"project": "Payments v3", "score": 32},
        {"project": "Auth Service", "score": 41},
        {"project": "Notifications", "score": 87},
    ],
}

def get_admin_metrics():
    return ADMIN_METRICS
