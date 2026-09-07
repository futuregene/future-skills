# Entry, Delegation and Return Contract

This is an instruction-level handoff, not a new CLI command or RPC. It works with
future-explore or another caller; it does not require the parent skill to be installed.

## Input contract

Use existing GOAL/brief files when provided; do not create a competing authorization
ledger. For standalone work, record the same fields in the task's research plan.

| Field | Required meaning |
|---|---|
| entry / deliverable / depth | standalone or delegated; report/methods/delta; A/B/C |
| questions / non-goals | User questions to preserve, decision to inform, excluded scope |
| authorization | Contract version, confirmed values and user instruction/approval references; distinguish proposals and pending fields |
| materials / prior work | Paths or identifiers, versions, known limitations and permitted processing |
| limits | This subtask's allocation, units, deadline and stop conditions; reserve time/resources for verification and writing |
| outputs | Workspace, report/brief format, return location and language |
| change boundary | Permitted adaptations; changes requiring caller/user approval |

Missing noncritical details can use stated defaults. Missing permissions, scope or
resource limits that affect execution need clarification before affected work begins.
Propose a finite allowance for standalone tasks when none exists. Existing authorized
limits need not be reconfirmed merely because a skill is invoked again.

## Inherit approval without bypassing it

- Accept explicit prior approval of unchanged scope, strategy, limits, model and
  deliverable. Record its reference and proceed; do not restart the strategy menu.
- A tentative plan from the caller is not user approval. Where authorization evidence
  is absent, ask for the missing decision rather than claiming inheritance.
- New findings may change the internal outline within approved scope. New objectives,
  broader data sharing, additional cost or a different deliverable require delta approval
  unless explicitly preauthorized. No arbitrary percentage-of-outline threshold applies.
- In delegated mode, return the pending decision to the orchestrator, which obtains
  any required user approval. Independent authorized work may continue within its allowance.
- Never allocate the parent's full budget to this subtask. The caller owns its global
  reservation ledger; report consumption and unsettled work so it can safely reconcile it.

## Reuse and incremental work

Read and verify the relevant existing source/claim records, not just the report title.
Check identity/version, evidence lineage, relevance, freshness and remaining questions.
Sufficient evidence may be reused without new searches. Record exactly what was checked
and which conclusions still apply. Old counts or a prior self-assessment do not establish adequacy.

For a delta, identify the base artifact and the questions/claims that changed. Search
only the gaps or freshness-sensitive facts, and invalidate affected conclusions if their
support changed. Return additions, corrections, unchanged-but-rechecked claims and
remaining gaps. A tiny update need not reproduce the whole report, but cannot claim to
have revalidated untouched material.

For a methods brief, agree the methods/constraints to compare, decision-critical claims,
required sources and allowable uncertainty. All briefed claims still follow evidence.md.
Use the full report contract when that is what the user requested; do not silently switch
formats to avoid a reference floor, verification step or requested analysis.

## Common return receipt

Return the following fields in an explicit section or caller-requested structured format.
Use actual artifact paths and record their version. No special JSON API is assumed.

| Field | Contents |
|---|---|
| contract | Accepted version, authorization basis and any approved changes |
| execution | ended or paused, with reason: coverage met, budget/retry limit, user stop, blocked, etc. |
| scope / depth / deliverable | Actual questions, A/B/C, report/methods/delta; disclose deviations |
| coverage | complete/partial against the agreed requirements, with unresolved questions |
| evidence | Supported, contradicted or unresolved key claims; provenance and verification limits; self-review vs independent review |
| artifacts | Report/brief, source cards and claim records, reuse/delta records as applicable |
| resources | Allocated units, used/estimated consumption, outstanding commitments, deadline status |
| next action | Specific gap or decision needed; no automatic spending or new subtask |

Completing a report does not close the parent's goal. A negative scientific conclusion
may satisfy the research question; an unresolved key claim may leave coverage partial
regardless of word count. The parent evaluates its own acceptance contract separately.
