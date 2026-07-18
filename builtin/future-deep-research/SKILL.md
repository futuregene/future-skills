---
name: future-deep-research
version: 2.5.1
description: >
  End-to-end deep research on user-specified topics. Automatically orchestrates multi-source data collection (web search, academic papers, local documents),
  supports user-provided materials (PDF/Word/URL/paper IDs/notes/CSV), ensures information reliability through cross-validation and citation verification,
  and outputs a complete Markdown (optional PDF) research report.
  Use when the user asks for deep research, literature review, industry analysis, technology research, competitive analysis, or writing research reports.
metadata:
  requires:
    bins: ["future"]
  orchestrates:
    - future-web
    - future-paper
    - future-document
    - future-browser
    - future-image
category: methodology
allowed-tools: Bash(future:*)
---

# Deep-Research Skill v2.0

End-to-end deep research skill — think like a human researcher: Plan → Collect → Verify → Synthesize

---

## 1. Resource Summary

| Skill | Capability | Role in Research |
|------|------------|------------------|
| **`future-web`** | `web_search` / `fetch_url` | Phase 1 web search + Phase 2 page deep-reading |
| **`future-paper`** | `search_paper` / `get_paper` | Phase 1/2 academic paper search and full-text retrieval |
| **`future-document`** | `parse_doc` | Phase 0 user-provided PDF/Word document parsing |
| **`future-browser`** | `browser_*` | Phase 1 **fetch fallback**: auto-retry with browser when fetch_url returns empty |
| **`future-image`** | image_generation / analysis | Phase 5 optional image generation |

---

## 2. Research Strategy Matrix

After receiving the user's request, the AI **MUST proactively offer three strategies for the user to choose from**:

| Dimension | Strategy A: Quick Scan | Strategy B: Broad Research | Strategy C: Deep Analysis |
|:----:|:---------------------:|:-------------------------:|:--------------------------:|
| Time | ~3 min | ~8 min | ~15-20 min |
| Search volume | 3-5 keywords | 6-10 keywords | 10-20 keywords |
| Page reading | Abstracts / key paragraphs only | Tier 1 full text | Tier 1+2 full text |
| Academic papers | Not retrieved | Search abstracts | Search + full text retrieval |
| Python analysis | ❌ | ❌ | ✅ |
| Cross-validation | Basic | Medium | Deep + citation verification |
| Use case | Quick understanding / fact-checking | Industry research / competitive overview | Academic review / technical deep-dive |

---

## 3. Research Workflow (6 Phases)

### Phase 0: Interactive Requirements Collection + Material Import

#### Step 0.1: Receive Initial Request + AI Follow-up Questions

```
🧑 User states a topic
  │
  ▼
🤖 AI proactively asks (choose questions as needed):
  ├─ 📐 Research Strategy
  │   ├─ "Strategy A Quick ~3min / B Broad ~8min / C Deep ~15min (with data analysis)?"
  │   └─ "Any time range constraints?"
  │
  ├─ 🌐 Information Sources
  │   ├─ "Focus more on academic papers, industry reports, or both?"
  │   ├─ "Source language preference? Default is English search (unless the topic itself is better suited to Chinese, such as China-specific policies, Chinese community discussions)"
  │
  ├─ 📝 Output Language
  │   └─ "Report output language? Default is Chinese (unless the user's question was asked in English, then default to English)"
  │
  ├─ 📊 Quantitative Analysis (required for Strategy C)
  │   └─ "Need data analysis? Do you have data files?"
  │
  ├─ 🎯 Focus Areas
  │   └─ "Any sub-topics or angles you want to focus on?"
  │
  └─ 🔄 Intervention Preferences
      └─ "During the research process, do you prefer: fully automatic / phase-by-phase reporting / intervene at key checkpoints?"
```

#### Step 0.2: Accept User-Provided Materials (any combination)

| Material Type | User Provides | AI Processes |
|---------------|---------------|--------------|
| 📑 PDF/Word docs | Local file path | `future tools call parse_doc ` |
| 🔗 Web URLs | One or more URLs | `future tools call fetch_url --url "..." ` |
| 📄 Paper IDs | DOI / PMID / ArXiv ID | `future tools call get_paper --paper_id "DOI:..." ` |
| 📝 Notes/outlines | Paste text directly | Incorporate directly into research foundation |
| 📊 CSV/Excel data | Local file path | For Phase 2b analysis |
| 🖼️ Screenshots/images | Local file path | For Phase 2d analysis |
| 📚 Batch papers | Multiple IDs/DOI list | Retrieve one by one |

#### Step 0.2.5: Pre-Outline Reconnaissance 🔎 (🚨 MUST execute before generating the outline)

> **Core principle: Never fabricate an outline from thin air without understanding the topic. Real researchers always do a quick literature scan before planning.**

```
Goal: Spend 3-5 minutes searching + crawling top URLs to understand the real information landscape of the topic

─── 0.2.5a: Seed Search ───

  Step 1: Search in parallel with 2-4 broad keywords based on the user's confirmed language needs
    future tools call web_search --query "<topic> overview | landscape | trends" --count 8
    future tools call web_search --query "<topic> comparison | analysis | review" --count 8

  Step 2: Rapidly filter from search result snippets:
    ├─ 🌊 Which words/concepts/company names appear repeatedly?
    ├─ 📅 How recent are the latest developments? (judge topic heat)
    ├─ ⚔️ Are there obvious controversies/opposing camps?
    ├─ 🏷️ What sub-fields exist that you didn't know about beforehand?
    └─ 📊 Are there obvious quantitative data sources?

  Step 3: Supplement with 1-2 "anchor queries" as needed
    ├─ Found authoritative overview/summary pages → supplement search: "<topic> comprehensive guide"
    └─ Found controversy points → supplement search: "<controversy keyword> debate | controversy"

─── 0.2.5a2: Anchor URL Quick Crawl (🚨 v2.3 new — how can you know what's really there without reading content?) ───

  Step 4: Pick 2-5 of the most valuable URLs from search results for crawling
    Selection criteria (by priority):
      ├─ 🥇 Authoritative overview/summary pages (official pricing pages, industry reports, arXiv reviews)
      ├─ 🥈 In-depth articles from well-known tech media (TechCrunch, Ars Technica, etc.)
      ├─ 🥉 High-quality tech blogs (those with data/architecture diagrams/comparison tables)
      └─ Skip: forum posts, pure news snippets, SEO farms, duplicate content

    For each selected URL, perform a quick crawl:
      future tools call fetch_url --url "<pick>"

  Step 5: After crawling, perform "quick content scanning" (not deep reading, but scanning structure):
    For each crawl result, quickly scan for these signals:
      ├─ 📑 Does the article have a table of contents / sub-headings? (→ well-structured, good anchor source)
      ├─ 📊 Does it have tables/data/comparisons? (→ high data density)
      ├─ 📅 Publication date? (→ judge timeliness)
      ├─ 🔗 What other authoritative sources does it cite? (→ can do secondary jumps)
      └─ ⚠️ Is the content consistent with what you expected from the snippet? (→ if not, ask why)

    After crawling, check content adequacy (lightweight version, not as strict as Phase 1):
      ├─ content is empty → skip this URL
      ├─ content < 500 chars → mark "⚠️ short content, limited information"
      ├─ content > 5000 chars → mark "📚 long article, high information density"
      └─ above all pass → ✅ include in reconnaissance materials

  🕐 Crawl quantity control:
    ├─ Strategy A: crawl 2 URLs (quick)
    ├─ Strategy B: crawl 3-4 URLs
    └─ Strategy C: crawl 4-5 URLs (including URLs from supplementary searches)

─── 0.2.5b: Output Reconnaissance Brief ───

  📡 Pre-Outline Reconnaissance Brief: <topic>

  Search snapshot (search result snippets from 2-4 keywords):
    ├─ 🏷️ Recurring concepts/companies/terms: [...]
    ├─ 📅 Content recency range: [year range, latest is when]
    └─ ⚔️ Potential controversies/opposing camps: [yes / no / description]

  Crawl insights (extracted from 2-5 crawled URLs):
    ├─ 📑 Anchor source 1: [title] — [article type: review/report/blog post] | [date]
    │   └─ 🔑 Key finding: [1-2 key points extracted from crawled content]
    ├─ 📑 Anchor source 2: [title] — [type] | [date]
    │   └─ 🔑 Key finding: [...]
    └─ 📑 Anchor source N: [...]

  📡 Synthesis:
    ├─ 🏷️ Discovered real sub-topics: [list — confirmed from crawled content, not guessed]
    ├─ 📊 Data density: [high / medium / low — judged by tables/data/comparisons found in crawls]
    ├─ 🌐 Language coverage: [Chinese/English each have X high-quality results]
    └─ ⚠️ Information blind spots: [which sub-topics/angles are not covered in crawls?]

  ✨ Key finding (1-3 sentences): [the most surprising/valuable finding from crawled content]
```

**⚠️ Rules**:
- Pre-outline reconnaissance **cannot be skipped**; Strategy A must also execute it (reduce keywords to 2, crawls to 2 URLs)
- If crawl findings seriously contradict search snippet expectations → **trust the crawled content**
- If a direction has zero URL coverage in crawls → mark it in the 📡 brief as "⚠️ Information blind spot"

#### Step 0.3: Output Research Plan for User Confirmation (driven by crawl results)

> **v2.3 improvement**: The outline is generated based on Step 0.2.5 crawl content; key findings directly cite crawled anchor sources.

```
📡 Pre-Outline Reconnaissance Brief: <topic>
  [Briefly repeat Step 0.2.5b's search snapshot + crawl insights here — let user see the data foundation for the outline]

📋 Research Plan: <topic>

Research Strategy: Strategy B (Broad Research)

Core Questions (aligned with crawl-confirmed sub-topics):
  - Q1: ...  ← Each Q must correspond to a real sub-topic discovered in crawls
  - Q2: ...
  - Q3: ... (if crawls found controversies → must include a controversy-related Q)

Preliminary Outline (shaped by crawl results, not a fixed template):
  Based on sub-topics that actually exist in crawled content, structure chapters as needed:
  ├─ Background & Context (required)
  ├─ Core Findings — [[split by crawl-confirmed sub-topics, 1 sub-topic = 1 subsection]]
  ├─ Controversies & Divergence (required if crawls found controversies; otherwise mark "No significant controversies found in crawls")
  ├─ Data & Quantitative Analysis (required if crawls found high data density; otherwise optional)
  ├─ Trends & Outlook (required)
  └─ Conclusions & Recommendations (required)

  ⚠️ "Outline flexibility statement": This outline is based on quick reconnaissance crawl content. Phases 1 and 1.5 may adjust it.

Incorporated Materials:
  - Anchor sources crawled in Step 0.2.5: [list titles + URLs]
  - /path/to/doc.pdf (12 pages, parsed ✅)
  - DOI:10.xxxx/yyyy (abstract retrieved ✅)

Search Keywords (validated by reconnaissance, not fabricated from thin air):
  Chinese: [terms that actually produced good results in reconnaissance]
  English: [terms that actually produced good results in reconnaissance]

User Intervention Mode: Phase-by-phase reporting
Estimated Time: ~8 minutes
Deliverable: deep-research-<topic>-<date>.md

Confirm execution? Or want to adjust something?
```

---

### Phase 1: Citation Exploration (Quick Scan + Iterative Backfill) 🔍

> **Benchmarking Perplexity** — fast, broad coverage, building the source pool
>
> **Core improvements**: auto backfill when content is insufficient; search query construction guide

```
Goal: Rapidly locate high-quality information sources, ensure each sub-topic has sufficient content coverage

─── 1a: Search Query Construction Guide (v2.1 new) ───

  Rules for constructing effective search queries:
    ├─ Prefer "topic + year" → "LLM pricing 2025" (not "LLM pricing")
    ├─ Wrap proper nouns in quotes → "prompt caching" "speculative decoding"
    ├─ Chinese vs English search strategy differences:
    │   ├─ Chinese: prefer "practical guide" "report" → captures blog posts/Zhihu/CSDN
    │   └─ English: prefer "comparison" "analysis" "review" → captures technical analysis/reports
    ├─ Avoid overly broad → "AI" is ineffective, "LLM token cost optimization 2025" is effective
    └─ Strategy C: 10-20 keywords should cover {topic} × {dimension} × {language} Cartesian product
        └─ e.g., {pricing, optimization techniques, economic models, controversies, trends} × {CN, EN} = 10

─── 1b: First Search and Tiering ───

  Step 1: Multi-keyword parallel search (Chinese + English)
    future tools call web_search --query "<keyword>" --count 10
    future tools call search_paper --queries '["..."]'

  Step 2: Rapid source tiering (🚨 v2.1 new three-tier scoring dimensions)
    Base Tier ranking:
    - 🥇 Tier 1: Directly relevant + authoritative (official/academic/well-known media)
    - 🥈 Tier 2: Relevant but non-authoritative (blogs/forums/self-media)
    - 🥉 Tier 3: Indirectly relevant
    
    Additional quality signals (don't change Tier, affect deep-reading priority):
    - 📅 Timeliness: <3 months / 3-12 months / >1 year
    - 🔬 Data density: High (many charts/data) / Medium / Low (pure opinion)
    - ⚖️ Stance: Neutral / Has clear slant but doesn't affect facts / Potentially biased

  Step 3: First crawl of Tier 1 sources
    Iterate through each Tier 1 URL, execute:
      future tools call fetch_url --url "..."
    After each crawl result, perform "content adequacy check":
      - content is empty?                 → mark ❌ empty content
      - content length < 200 chars?       → mark ⚠️ content too short
      - content unrelated to search topic? → mark ⚠️ low relevance
      - content contains truncation markers? → mark ⚠️ content truncated
        Truncation marker detection: '</current_article_content>' | '... (truncated)' | '[content truncated]'
        Truncation handling: if truncation cuts off core data/conclusions → browser backfill; if only tailing recommendations/copyright truncated → ✅ adequate
      - All above pass                   → mark ✅ content adequate

  Step 4: Fetch Fallback (for ❌ and ⚠️ URLs)
    For empty/too-short URLs, retry with browser degradation:
      future tools call browser --command "start" --url "..."
      future tools call browser --command "snapshot" --limit 100
      future tools call browser --command "screenshot" --fullPage true --path "./page.png"
    After browser crawl, check content adequacy again:
      - content adequate → mark ✅
      - still insufficient   → completely abandon this URL

─── 1b: Iterative Backfill When Content Is Insufficient ───

  Check content coverage for all current sub-topics:
    Scenario A: Sub-topic has ✅ adequately-sourced count ≥ 2      → sub-topic meets threshold, proceed to Phase 2
    Scenario B: Sub-topic has ✅ adequately-sourced count < 2      → needs backfill
    Scenario C: All sources are ❌ (all degradation failed)        → needs fresh search

  Backfill strategies (by priority):
    
    Strategy 1️⃣: Extract more URLs from Tier 2 sources and crawl
      Condition: Tier 2 still has untried URLs
      Action:
        future tools call fetch_url --url "<Tier2 URL>"
      Check content adequacy → ✅ include / ❌ abandon→continue next Tier 2

    Strategy 2️⃣: Change keywords and re-search (refine/synonym/related terms)
      Condition: Tier 2 is also exhausted but still insufficient
      Action:
        future tools call web_search --query "<new keyword>" --count 10
      New results go through same tiering→crawl→check process

    Strategy 3️⃣: Expand search scope (academic/English/other languages)
      Condition: Chinese results insufficient, supplement with English search
      Action:
        future tools call web_search --query "<English keyword>" --count 10
        future tools call search_paper --queries '["<English query>"]'

  After each backfill, re-check content adequacy until:
    - ✅ Each sub-topic has ≥ 2 adequate sources  → proceed to Phase 2
    - ⚠️ All attempts exhausted but still can't meet threshold → mark "this sub-topic has limited information", proceed to Phase 2

─── 1c: Source Quality Statistics and Output ───

  Output "Source Candidate Pool and Crawl Statistics":
    ├─ ✅ Content adequate: X (Tier1: X, Tier2: X)
    ├─ ⚠️ Content too short (still insufficient after browser degradation): X
    ├─ ❌ Completely unreachable: X
    ├─ 🔄 Backfill rounds: X rounds
    └─ 📊 Sub-topic coverage: All met / partially limited / needs focused attention
```

### Phase 1.5: Dynamic Outline Calibration 🔄 (🚨 v2.2 new)

> **Competitor benchmarking**: Anthropic lead agent periodically evaluates whether search trajectory aligns with original query; OpenAI/Gemini support mid-flight re-planning. Pipeline-type systems' biggest weakness is that the outline, once fixed, cannot be adjusted.

```
Goal: If actual sub-topics discovered in Phase 1 deviate significantly, adjust the report outline

Trigger condition: Deviation between Phase 1 actual discovered sub-topics and Phase 0.3 outline >30%

Action:
  1. Compare "Phase 0.2.5 reconnaissance brief sub-topics" vs "Phase 1 actually discovered new sub-topics"
  2. If significant deviation:
     ├─ Output adjusted outline (mark "🔧 The following chapters have been adjusted based on Phase 1 findings")
     └─ Note which chapters were added/deleted/merged
  3. Phase 5 report structure follows the adjusted outline (not the Phase 0.3 original outline)

  ⚠️ Rules:
    - Deviation <30%: no adjustment needed, proceed directly to Phase 2
    - Deviation 30-50%: auto-adjust + one-line notification
    - Deviation >50%: ask user for confirmation
```

### Phase 2: Deep Reading + Data Analysis 🧠

> **Benchmarking OpenAI Deep Research + Manus** — source-by-source deep reading, code analysis

```
Goal: Conduct source-by-source deep reading of ✅ adequate sources obtained, extract structured information

  2a: Source-by-Source Deep Reading (🚨 v2.1 new structured extraction template)
    For each source marked ✅ in Phase 1, re-fetch full text:
      future tools call fetch_url --url "..."
    ⚠️ Same fetch fallback rules apply: empty content → retry with browser
    ⚠️ Same backfill rules apply: if deep reading finds insufficient content → go back to Phase 1b backfill

    For each source, record below (internal notes, not output to user):
      📄 Source Extraction Card:
        ├─ Title/URL/Date/Tier
        ├─ 🔑 Core Argument (1-2 sentences)
        ├─ 📊 Key Data Points (itemized, each annotated with exact paragraph)
        ├─ 💬 Directly Quotable Original Paragraphs (1-3 paragraphs)
        ├─ ⚠️ Method/Stance Limitations (limitations or biases of this source)
        └─ 🔗 Relationship with other sources (contradicts/consistent with/supplements)

  2a': Multi-Source Deduplication Protocol (v2.1 new)
    When multiple sources report the same fact:
      ├─ Choose citation source by priority: Tier1 > newer > more precise data
      ├─ In report, annotate: "This data is confirmed by N independent sources [primary citation source, URL]"
      └─ Don't repetitively list each source — use count to indicate consensus strength, reduce redundancy

  2b: Quantitative Data Analysis (Strategy C + when user has data)
    ├─ Use Python for:
    │   ├─ Extracting table data from web pages/PDFs
    │   ├─ Numerical computation and statistical analysis
    │   ├─ Trend charts/comparison chart generation
    │   └─ Custom data modeling
    └─ Analysis results + visualizations

  2c: Academic Deep Dive
    ├─ future tools call get_paper --paper_id "..."
    └─ Extract: methods, results, limitations

  2d: Multimedia Supplement (Strategy C + as needed)
    └─ Image analysis: OCR/chart comprehension via future-image

Output: "Deep Reading Notes" — core findings + precise citations + 🔴 suspicious items list
```

### Phase 3: Cross-Validation + Citation Verification 🔬

> **Core differentiating feature** — benchmarking Gemini's four-layer verification + citation hallucination detection

```
Goal: Ensure information reliability, detect citation hallucinations

  3a: Cross-Source Fact Verification
    ├─ Compare each "key fact" across multiple sources
    ├─ Consistent → ✅ High confidence (annotate "confirmed by X independent sources")
    ├─ Minor differences → ⚠️ Note (annotate difference range, e.g., "$0.28 vs $0.30/M")
    └─ Contradiction → 🔴 Controversy point (list each side's view and respective sources)

  3b: Citation Hallucination Detection (🚨 Core differentiating feature)
    ├─ Check each citation:
    │   ├─ Is the URL accessible
    │   ├─ Does the source actually contain the cited content
    │   └─ Is there quoting out of context or distortion of original meaning
    └─ ⚠️ Suspicious ones retry confirmation with browser

  3c: Confidence-Level Comprehensive Annotation
    └─ Source count + authority + consistency → 🔴 High / 🟡 Medium / ⚪ Low

Output: "Verification Report" — confidence annotations embedded in final report
  ✅ Verified: X items | ⚠️ Needs attention: X items | 🔴 Controversial: X items | 🚨 Suspicious citations: X items
```

### Phase 4: Iterative Optimization (Optional) 🔄

> When user selects "phase-by-phase reporting" or "checkpoint intervention" mode, report progress after each Phase

```
Trigger conditions:
  ├─ User selected "phase-by-phase reporting" or "checkpoint intervention" mode → auto-brief at Phase end
  ├─ Major controversy found requiring user decision
  ├─ A direction has insufficient information
  └─ User proactively says "look deeper into XXX"

User actions:
  ├─ "Dig deeper into this part about XXX"
  ├─ "Change search keyword to YYY"
  ├─ "This set of data conflicts; I'm leaning towards side A's view"
  └─ "This direction is enough, skip and continue"
```

### Phase Progress Heartbeats (v2.1 new) 💓

> **AI MUST output one line of progress after each Phase completes.**
> This prevents the research process from becoming a "black box" — user staring at blank waiting without knowing what's happening.

```
Progress heartbeat format (one line after each Phase ends):

✅ Phase 0 complete | Pre-outline reconnaissance found X sub-topics | Outline confirmed
🚀 Phase 1 starting | Searching X keywords...
✅ Phase 1 complete | Captured Y sources (T1: a, T2: b, T3: c) | 🔄 Backfill Z rounds
🚀 Phase 2 starting | Source-by-source deep reading...
✅ Phase 2 complete | Deep-read N sources | Extracted M key data points
🚀 Phase 3 starting | Cross-validating...
✅ Phase 3 complete | Verified P facts | Found Q items needing attention | R controversies
🚀 Phase 5 starting | Generating report...
✅ Phase 5 complete | Report saved: deep-research-<topic>-<date>.md
```

**⚠️ Rules**:
- Each line includes brief statistics
- **Never skip** — this is the minimum level of user-visible progress

### Phase 5: Comprehensive Report Generation + Gap Marking ✍️

> **v2.4 core principle: The report is an "analytical story", not a pile of data tables.**
> Readers should be able to read it smoothly like an in-depth analytical article, not be forced to parse one table and bullet list after another.

```
Goal: Synthesize all results, generate a complete, narratively compelling, traceable analytical report

─── 5.0: Report Writing Style Guide (🚨 v2.4 new) ───

  Core requirement: Every chapter should read as narrative analysis, not data dumps.

  ❌ Forbidden patterns:
    ├─ 3+ consecutive tables without transitions between them
    ├─ Chapters starting with tables or bullet points (must introduce with a narrative paragraph first)
    ├─ "Data silos": listing numbers without explaining meaning or establishing connections
    ├─ "Naked data" paragraphs without context
    └─ Entire report of bullet-to-bullet jumps, lacking a narrative thread

  ✅ Required structure pattern for every chapter:

    [Narrative opening] 2-4 sentences in natural language summarizing what this chapter covers and why it matters.
        ↓
    [Developed analysis] Coherent paragraphs developing the argument. Data embedded in narrative —
        e.g., ❌ "Price: GPT-5.2 $1.75/M, Claude $5/M, DeepSeek $0.28/M"
             ✅ "The price gap is striking. OpenAI's latest GPT-5.2 charges $1.75
                 per million input tokens, Anthropic's Claude Opus 4.6 follows at $5 —
                 while DeepSeek needs only $0.28, less than one-sixth of OpenAI's price."
        ↓
    [Supporting tables] Use tables only when precise comparison across multiple dimensions is needed, and tables must have explanatory text before and after:
        ├─ Before table: a paragraph explaining "what the table below shows, why look at this dimension"
        └─ After table: a paragraph distilling key insights ("From the table, the most notable gap is...")
        ↓
    [Transition sentence] 1-2 sentences at the end of each subsection naturally transitioning to the next

  📊 Table usage constraints:
    ├─ Each table ≤ 6 columns (if exceeds, split into multiple tables or use narrative instead)
    ├─ Each table ≤ 10 rows (if exceeds, show only top/bottom N and note "full data in appendix")
    ├─ Two tables must have ≥1 paragraph of narrative text between them
    └─ Table captions must be "analytical titles" not "descriptive titles"
        ├─ ❌ "Table 1: Vendor Pricing"
        └─ ✅ "The Pricing Gap: The same task can cost 6000× more depending on the vendor"

  📝 Bullet point usage constraints:
    ├─ Any bullet list must be introduced by an opening paragraph
    ├─ Avoid bare lists with more than 8 items — long lists should be grouped with sub-headings between groups
    ├─ Bullet point content must be complete sentences, not single nouns/phrases
    └─ If a list can be rewritten as a coherent paragraph → rewrite as a paragraph

  📖 Executive Summary Specifics:
    ├─ The executive summary should be a "mini report" readable independently
    ├─ Contains: core questions → key findings (1-2 sentences each) → main conclusions
    ├─ Does not rely on any tables — all data conveyed through narrative text
    └─ Length: 10-15% of total report word count

  🔗 Citation Integration Method:
    ├─ Citations embedded in narrative: not "prices differ greatly [1][2][3]",
    │   but "IntuitionLabs' 2025 comprehensive comparison [1] and Anthropic's
    │   official pricing documentation [2] both confirm this trend"
    └─ On first mention of a source, give enough context for the reader to assess authority

  🎯 Golden ratio (within each chapter):
    ├─ ~50% coherent narrative paragraphs (analysis, explanation, argumentation)
    ├─ ~25% charts/tables (data visualization supporting the narrative)
    ├─ ~25% bullet point lists (structured key points, not data dumping)
    └─ If lists + tables > narrative → this chapter fails and needs rewriting

─── 5.1: Report Structure ───

Report structure (v2.4 emphasis: structure serves narrative, not the reverse).

Required chapters (every report must include):
  ├─ 🔖 Meta Information (topic, date, strategy, source statistics)
  ├─ 📋 Executive Summary (with confidence overview)
  ├─ 📑 Table of Contents
  ├─ Conclusions & Recommendations
  ├─ 📚 References (categorized: web/papers/documents)
  └─ 📎 Appendix
      ├─ Citation Verification Report (🚨 all suspicious citations listed)
      ├─ Fetch Fallback Records
      └─ Research Methodology Notes

Conditional chapters (depends on sub-topics discovered in reconnaissance and content nature):
  ├─ Background & Context (required when topic needs historical context)
  ├─ Core Findings — [[split into multiple sub-chapters, each corresponding to a reconnaissance-discovered sub-topic]]
  │   └─ inline citations 🔗: each data point annotated with [source, URL] format
  ├─ Controversies & Divergence (only when reconnaissance actually found controversies; otherwise mark "No significant controversies found")
  ├─ Data & Quantitative Analysis (only when quantitative data exists)
  ├─ Known Unknowns & Research Limitations
  └─ Trends & Outlook

🔥 Report Naming Convention:
  ├─ All reports must include date → deep-research-<topic>-<YYYY-MM-DD>.md
  └─ Prevents overwriting old reports

Multi-format export:
  ├─ 📝 Markdown (default)
  └─ 📄 PDF (optional)

Output: deep-research-<topic>-<YYYY-MM-DD>.md
```

### Phase 5.1: LLM-as-Judge Report Self-Assessment 🧪 (🚨 v2.2 new)

> **Competitor benchmarking**: Anthropic uses a unified LLM-Judge scoring five dimensions (factual / citation / completeness / source / efficiency) for every research report. DeepHalluBench research confirms intermediate-step errors are invisible in end-to-end evaluation.

```
Goal: Self-assess the final report's quality, embed credibility signals

Action:
  Use LLM to score the final report on four dimensions (0-1 scale):
    - factual_accuracy: Are key data points supported by sources
    - citation_accuracy: Are citations real and accessible
    - completeness: Are sub-topics fully covered
    - source_quality: Source authority distribution

  Embed a one-line self-assessment at the start of the report's "Executive Summary":
    🟢 Pass / 🟡 Needs Attention / 🔴 Dubious

  Detailed scores embedded in executive summary meta info:
    Self-assessment total X.XX | Factual X.X / Citation X.X / Completeness X.X / Source X.X

  Rules:
    - Total ≥0.75 → 🟢 "This report self-assesses as passing"
    - Total 0.5-0.75 → 🟡 "This report has items requiring attention; please verify key data points"
    - Total <0.5 → 🔴 "This report has low confidence; manual review recommended"
    - Individual dimension <0.6 → annotate corresponding chapter with "⚠️ Low confidence [dimension]"

  Strategy differences:
    - Strategy A: skip self-assessment (quick scan doesn't need it)
    - Strategy B: score only (don't embed detailed breakdown)
    - Strategy C: full four-dimension scoring + embedding
```

### Phase 5.2: Citation Spot Check 🔍 (🚨 v2.2 new)

> **Competitor benchmarking**: Anthropic CitationAgent independently verifies every citation after report drafting. Perplexity's native grounded retrieval achieves 94.3% citation precision.

```
Goal: Ensure authenticity of key citations

Action:
  1. Extract 5 key citations from the report (sources of the most important data/facts)
  2. Verify each:
     - Is the URL accessible
     - Does the content actually contain the cited information
  3. Output spot check results:
     ✅ 5/5 passed
     ⚠️ X/5 passed (list failed citations and reasons)

  Rules:
    - Failure rate ≤20% (≤1 item) → ✅ normal
    - Failure rate 20-40% (2 items) → ⚠️ annotate in report
    - Failure rate >40% (≥3 items) → 🚨 alert user "Key citation verification failed; review recommended"

  Strategy differences:
    - Strategy A/B: skip
    - Strategy C: must execute
```

---

## 4. Dual Stopping Mechanism + Backfill Cap

```
         Phase 1 → Phase 2 → Phase 3 → Phase 4 ...
                          │
              ┌───────────┴────────────┐
              ▼                        ▼
    Coverage-Based Stopping       Budget-Based Stopping
    ┌────────────────────────┐  ┌──────────────────────┐
    │ • Each sub-topic ≥2    │  │ • Time cap            │
    │   adequate sources     │  │ • Search count cap    │
    │ • No new info emerging │  │ • Page fetch cap      │
    │ • Contradictions       │  │ • Reasoning iter cap  │
    │   resolved             │  │ • Backfill round cap  │
    │ • Confidence met       │  │   = 3 rounds          │
    │ • Backfill rounds ≥3   │  │                       │
    │   (prevent infinite)   │  │                       │
    └────────────────────────┘  └──────────────────────┘
              │                        │
              └──────────┬─────────────┘
                         ▼
               ✅ Normal completion → Phase 5 report generation
               ⚠️ Budget/backfill rounds reached → partial report + mark "this sub-topic has limited information"
```

---

## 5. Fetch Fallback + Content Backfill Strategy ⚠️

This is the core fallback plan for when `fetch_url` may return empty content or insufficient content.

### Content Adequacy Check Criteria

After each fetch, automatically perform the following checks:

| Check Item | Criterion | Result |
|-----------|-----------|:------:|
| content is empty string | `content == ""` | ❌ empty content |
| content length insufficient | `< 200 chars` | ⚠️ content too short |
| topic relevance | content unrelated to search target | ⚠️ low relevance |
| all above pass | - | ✅ content adequate |

### Fetch Loop Flow

```
Fetch a URL
    │
    ▼
Content adequacy check
    │
    ├─ ✅ content adequate → add to source pool, mark complete
    │
    ├─ ❌ empty content → degrade to browser retry
    │   │
    │   ▼
    │   browser crawl → re-check
    │   │
    │   ├─ ✅ content adequate → add to source pool
    │   └─ ❌ still empty → completely abandon, record
    │
    └─ ⚠️ too short/low relevance → browser degradation retry
        │
        ▼
        browser crawl → check
        │
        ├─ ✅ adequate → include
        └─ ⚠️ still insufficient → mark "low-quality source", record but don't use further
```

### Sub-Topic Backfill Loop

When a sub-topic has < 2 ✅ adequate sources, auto-enter backfill loop:

```
Check sub-topic content coverage
    │
    ├─ ✅ adequate sources ≥ 2 → meets threshold, proceed to next phase
    │
    └─ ❌ adequate sources < 2 → enter backfill
        │
        ├─ Strategy 1️⃣: try uncrawled URLs from Tier 2
        │   │   fetch_url → check → if adequate, include
        │   └─ if Tier 2 exhausted but still insufficient →
        │
        ├─ Strategy 2️⃣: backfill search with new keywords
        │   │   web_search(new_query) → tier → crawl → check
        │   └─ if still insufficient →
        │
        ├─ Strategy 3️⃣: switch to English/academic source backfill search
        │   │   web_search(en_query) / search_paper(...) → crawl → check
        │   └─ if still insufficient →
        │
        └─ ⚠️ all strategies exhausted → mark "this sub-topic has limited information"
```

### Fallback Execution Commands

```bash
# Step 1: Start or check browser
future tools call browser --command "start" --url "<target URL>"

# Step 2: Open page
future tools call browser --command "open" --url "<target URL>"

# Step 3: Wait for render, then get DOM snapshot
future tools call browser --command "snapshot" --limit 100

# Step 4: If full page content needed, screenshot and save
future tools call browser --command "screenshot" --fullPage true --path "./deep-research-page.png"

# Step 5: Check console errors
future tools call browser --command "console" --level "error"
```

### Fallback & Backfill Records

Record all fallback and backfill actions in the final report appendix:

```markdown
### ⚠️ Fetch Fallback & Backfill Records

#### Fallback Records
| URL | Tier | First Result | Fallback Method | Post-Fallback Result |
|-----|:----:|:------------:|:--------------:|:--------------------:|
| https://... | 1 | ❌ empty | browser | ✅ success |
| https://... | 1 | ⚠️ too short | browser | ✅ success |
| https://... | 1 | ❌ empty | browser | ❌ still failed |

#### Backfill Rounds
| Round | Trigger Reason | Backfill Strategy | New ✅ Sources | Status |
|:-----:|----------------|:-----------------:|:------------:|:------:|
| 1 | Sub-topic A only 1 source | Strategy 1: Tier2 | +2 | ✅ met threshold |
| 2 | Sub-topic B only 0 sources | Strategy 2: new keywords | +1 | ⚠️ still limited |
| 3 | Sub-topic B still insufficient | Strategy 3: English search | +1 | ⚠️ marked limited |
```

---

## 6. Competitor Benchmarking Reference

This skill's design references the strengths of the following competitors and optimizes against their weaknesses:

| Competitor | Strengths Adopted | Weaknesses Avoided |
|:----------:|------------------|-------------------|
| **OpenAI Deep Research** | Five-phase process, dual stopping, inline citations, code analysis | Slow, no mid-phase intervention → our three-strategy choice + Phase 4 iterative optimization |
| **Perplexity Sonar Pro** | Fast citation exploration, high citation density, source tiering | Weaker deep reasoning → our Phase 2 deep reading + Phase 3 deep verification |
| **Gemini Deep Research** | 100+ page reading, four-layer cross-validation pipeline | Low information density → our gap analysis + confidence annotation |
| **Manus** | Tool Use capability (code execution, file operations) | Unstable Instruction Following → our fixed report templates |
| **GPT Researcher** | Open-source customizable, multi-agent architecture, local docs | No dedicated reasoning model → guaranteed by underlying model capability |
| **LangChain Open Deep Research** | MCP support, multi-search providers, modular | No UX, must self-build → we provide complete orchestration instructions |
| **STORM (Stanford)** | Multi-perspective outline, citation completeness, pre-writing phase separation | Review-oriented only → we cover general research scenarios |

---

> Changelog moved to [CHANGELOG.md](./CHANGELOG.md)

---

## 7. Core Design Principles

| Principle | Description |
|:--------:|-------------|
| 🎯 **User-Led** | Three strategies selectable + multi-type material import + mid-phase intervention |
| 🧠 **Layered Research** | Discovery layer → Analysis layer → Quality layer, progressively layered |
| ✅ **Trustworthy** | Inline citations + citation verification + confidence annotation + gap marking |
| 🛡️ **Honest** | Mark "Known Unknowns"; suspicious citations; incomplete sections; low-confidence chapters |
| 🔍 **Reconnaissance Before Planning** | Phase 0.2.5 pre-outline reconnaissance: search + crawl 2-5 anchor URLs → outline originates from real content |
| 🔄 **Dynamic Outline** (v2.2) | Phase 1.5 adjusts outline based on real findings: pipeline is not rigid |
| 🧪 **Self-Assessment Loop** (v2.2) | Phase 5.1 LLM-as-Judge four-dimension scoring + 5.2 citation spot check |
| 📖 **Narrative-Driven** (v2.4) | Phase 5 writing style guide: report is an analytical story, not data dumping; golden ratio 50/25/25 |
| 📊 **Chart Constraints** (v2.4) | Tables ≤6 columns ≤10 rows, narrative paragraphs required before and after, captions must be analytical not descriptive |
| 📝 **Bullet Discipline** (v2.4) | Bullet points need introductory sentences, content must be complete sentences, long lists must be grouped |
| 💓 **Fully Visible** | One-line progress heartbeat with statistics per Phase, research process not a black box |
| ⚠️ **Robust** | fetch_url → browser fallback + truncation detection |
| 🔁 **Iterative Backfill** | Tier2→new keywords→English/academic progressive backfill, max 3 rounds |
| 🎯 **Content Adequacy Check** | Per fetch: empty ❌ / too short ⚠️ / truncated ⚠️ / adequate ✅ |
| 🔄 **Intervention-Friendly** | Phase 4 mid-course direction adjustment |
| 🌐 **Multi-Language** | Chinese-English mixed search |
| 📊 **Structured Extraction** | Phase 2 per-source "Source Extraction Card" format |
| 🔗 **Dedup Merging** | Multi-source confirmation → "N sources confirm"; no repetitive listing |
