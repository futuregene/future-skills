# Ensemble templates

Optional detail for §7 of `SKILL.md`: copy-paste scaffolding for a cross-model
ensemble (one brief, different models, blind judging, synthesis). Placeholders:
`G` goal id, `M_A`/`M_B`/`M_C` model ids from `future models`, `J` judge model,
`S` synthesis model. Read the registry rather than trusting model names written
here — a registry entry can disappear between runs.

## Layout

```text
ensemble/
  brief.md          frozen by the supervisor, never edited by a candidate
  a/                candidate A: inputs copied in, output + notes out
  b/                candidate B
  c/                candidate C
  judge/packet.md   anonymised C1..Cn + checklist
  judge/scores.md   per-criterion scores with evidence
  final/            the synthesized deliverable
  provenance.md     roster, checks, judged scores, grafts
```

Every candidate directory is that task's whole `--required-write-scope`. Keep
`brief.md` and `judge/` out of every candidate's scope; a candidate that reads
`judge/` has seen the comparison it is being scored on.

## brief.md

```markdown
# Brief: <deliverable> (ensemble v1, frozen <date>)

## Objective
<one paragraph: what the artifact must do, for whom>

## Deliverable
- Path: ensemble/<x>/<file> (candidate dir differs; structure must match)
- Format: <language, length, sections, required metadata>
- Inputs: <files copied into each candidate dir; no network, no new sources>

## Constraints
- <must / must not, dependencies allowed, budget, licence>

## Acceptance checks (frozen — used to compare candidates and the final merge)
1. <deterministic check: command + expected result>
2. <structural/content check: exact thing a reviewer greps for>
3. <judged criterion: what "good" means, scored 1-5>

## Declared deviations
- <e.g. M_C has no image input, so its task text carries the caption instead>
```

Freeze it before the first dispatch. If the brief changes mid-flight, that is
ensemble v2: rerun every candidate, do not compare old and new outputs.

## Candidate task text

```text
Candidate <X>: read ensemble/brief.md and produce ensemble/<x>/<file> plus
ensemble/<x>/notes.md (approach, assumptions, what you are unsure about).
Write ONLY under ensemble/<x>/. Do not read or edit ensemble/a|b|c/ (other than
your own) or ensemble/brief.md. Do not ask another candidate or the supervisor
for the answer. Report the exact commands you ran to check your output.
```

Dispatch with the candidate's model and an equal budget:

```bash
future goal run --goal G --agent-id cand-a --model M_A --thinking-level high --max-turns 1
```

One `--agent-id` per candidate, one todo per candidate with
`--required-write-scope ensemble/<x>/` and `--verify <frozen check for that dir>`,
so a candidate cannot claim or touch another's work.

## Judging packet

```markdown
# Judging packet (blind)
Brief and acceptance checks: <inline the frozen brief>
Candidates: C1, C2, C3 — model identities withheld, order shuffled.

For each candidate and each acceptance criterion:
- score 1-5, plus the evidence line you based it on
- what is uniquely right here (something only this candidate got)
- what fails uniquely here (a mistake only this candidate made)
Then: which candidate is the best base for a merged deliverable, and the three
grafts the merge should take, each named as "<candidate>: <element> -> <target>".
Do not average; do not prefer a candidate for style if it fails a hard check.
```

A judge that was itself a candidate is a conflict of interest: prefer a model
outside the roster, or at minimum exclude the judge's own output from the packet
it scores and say so in `provenance.md`.

## provenance.md

```markdown
| Candidate | Model | Thinking | Run/session | Path | Frozen checks | Judged score | Unique strength | Unique failure |
|---|---|---|---|---|---|---|---|---|
| C1 | ... | high | run ... | ensemble/a/ | 3/3 pass | 18/25 | ... | ... |
| C2 | ... | high | run ... | ensemble/b/ | 2/3 (check 2 fails: ...) | 15/25 | ... | ... |
| C3 | ... | high | run ... | ensemble/c/ | 3/3 pass | 17/25 | ... | ... |

Base: C1. Judge: <model>, blind packet ensemble/judge/packet.md, scores ensemble/judge/scores.md.
Grafts:
- C3: <element> -> final/<file> (reason, re-ran <check>)
- C2: rejected — <element> contradicts the brief constraint "<...>"
Synthesis result: frozen checks 3/3 / judged 21/25 vs best candidate 18/25.
Ship decision: <synthesis | best candidate C1>, because <evidence>.
```

## Roster heuristics

- Two candidates is the minimum that can disagree; three covers roughly a
  code-specialist, a long-context reasoner and a writing/editing model. Beyond
  four, marginal gain rarely repays the cost.
- Pick for the deliverable: implementation → code-specialised models; analysis
  or planning → long-context reasoning; prose/editing → models whose samples read
  well. Read each entry's context window before assigning a long input.
- Same family twice (or the same model with two temperatures) is a variance
  check, not an ensemble — useful, but fund it as one and say so.
- Equalise thinking level, turn budget and tool permissions. Diversity should
  come from the model, not from one candidate quietly getting more turns.
- Budget the whole thing up front: N candidates + judge + synthesis + verify, and
  a second round only if the first shows complementary strengths worth merging.

## Failure checklist before reporting an ensemble result

- [ ] One frozen brief; every candidate's task text points at it; deviations listed.
- [ ] Roster recorded with a reason per model; families not duplicated silently.
- [ ] Each candidate stayed inside its own scope and never saw another candidate.
- [ ] Judge saw anonymised outputs, the frozen checks, and produced per-criterion
      evidence — not one holistic verdict.
- [ ] Synthesis re-ran every deterministic check; grafts named with source candidate.
- [ ] Final artifact compared against the best single candidate, and the ship
      decision follows that comparison instead of assuming the merge won.
- [ ] Per-candidate delivery records and provenance written; candidate dirs kept
      as reproduction evidence until verification.
