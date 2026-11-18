---
name: alert-review
description: Runs Quality Gate 2 (grounding, anti-hallucination, logic audit, noise filter, human-in-the-loop hold) and the pre-send part of Quality Gate 3 (cooldown, channel, feedback hook) on a drafted alert or digest, returns one list of fixes with starter prompts, and records the human decision to approve, adjust or reject. Use when the user says "review the alert", "check the digest", "approve the held alert", or automatically after alert-draft.
---

# Alert review (Gate 2 + Gate 3 pre-send)

The gate recommends; the human decides. Nothing is sent because the gate passed, and nothing Critical is sent without a named human approving.

Read `frameworks/quality-gates.md`, `frameworks/governance.md`, the draft, its score and input JSON, and every record behind its Source IDs.

## 1. Check every row

For G2.1–G2.8 and G3.1–G3.2, give PASS or FAIL with a quote from the draft:

- **G2.1 / G2.2 grounding**: list every number, date, place, decree and claim. Each must appear in a cited record. One unsupported item is a FAIL; name it.
- **G2.3**: the drivers table matches the score JSON exactly.
- **G2.4 noise**: compare any social spike to the dossier's "Known noise" and the calendar (holidays, matches, viral events). If unchecked, FAIL.
- **G2.5**: single-vector alerts say so.
- **G2.6 / G2.7**: contradictory texts or S_final ≥ 85 → status must be HELD.
- **G2.8**: governance language and privacy: no PII, no precise locations tied to people, no stigmatising terms.
- **G3.1 cooldown**, **G3.2 channel** per the routing matrix.
- Playbook: actions quoted verbatim from an approved playbook, or clearly marked proposed.

## 2. One list

Each FAIL is one row: **Where** (section) · **Problem** (quote) · **Prompt** (a sentence the user can paste to fix it, e.g. "In alerts/held/2026-11-18-sahel-crit.md, remove the 40% price figure from 'What changed' or cite the record it comes from."). A grounding fail is fixed by citing or cutting, never by softening. Lead with the top three fixes.

Write `<draft>.review.md` next to the draft. Report in chat: verdict (READY / FIX / HELD), top fixes, eight lines at most.

## 3. Human decision

- **DRAFT, all pass**: ask "Approve for sending? 1 Approve · 2 Adjust · 3 Reject".
- **HELD**: record `held_since` UTC and `sla_due` (+30 minutes) in the frontmatter and on the board's holds table. Ask for the analyst's name and decision: Validate · Adjust score (with reason, then re-run `score-signal`) · Reject. Never approve on the analyst's behalf.

On approval: set `status: APPROVED`, `approved_by`, `approved_utc`, add the feedback line "Feedback: Accurate | False Positive | Irrelevant", move the file to `alerts/sent/`, and update the board.

## 4. Sending

Send only through a connected channel the user names (Slack, Teams, email, webhook connector) and only after approval. If no channel is connected, give the final text ready to paste and record `delivered: manual`. Record delivery result (G3.3); on a failed Critical delivery, propose the next channel.
