# 🎙️ Live Demo & Presentation Guide: AI Ops / Enterprise Agentic SDLC

**Target Audience:** Enterprise Engineering Leads, Cloud Architects, SecOps, and Leadership  
**Demo Duration:** ~12–15 Minutes  
**Reference Deck:** [AI Ops: Enterprise Agentic SDLC & Pipeline Architecture](https://docs.google.com/presentation/d/16b8WR3isx8fQF5c25VrqSDNMKsLjBxnCCIYWujgqNaQ/edit?slide=id.p5#slide=id.p5)  
**Reference SDLC Document:** [Agentic SDLC Best Practices](https://docs.google.com/document/d/1jXDLAkuF4r-XtKA67m3UwQ8S3lGyFaV4VvhohMtTwf4/edit)  
**Reference Architecture:** AI Ops Gitflow Diagram (`image.png`)

---

## 🗺️ High-Level Story Arc & Architecture Mapping

This demonstration brings the **Architecture Diagram** to life by showing how enterprise agents move from local ideation to production under strict governance:

```
[ IDE & Quality Tools ]       [ Dev Branch ]                      [ Security Guardrails ]
   Antigravity IDE     ───►  Author Code                           Wiz Security Scanners
   Quality Checks            Developer Unit Tests ──┐              Central Security Policy
                                                    │                        │
                                Automated Quality Checks ◄───────────────────┤ (Governance)
                                                    │                        │
                                Integration Tests ──┴──► Merge Approved     │
                                                              │              │
                                                        [ Main Branch ]      │
                                                        Main Branch Build    │
                                                              │              │
                                                    Deployment Pipeline ◄────┘
                                                     - CodeMender & Wiz Gate
                                                     - Agent CLI Packaging
                                                     - Blocking Gate
                                                              │
                                                        Final Deploy ──► GCP
```

---

## ⏱️ Step-by-Step Live Demonstration Script

### **Act I: Developer Environment & Scaffolding (Slides 3 & 4 | ~3 Mins)**
*Corresponds to Diagram: "IDE and Developer-Owned Quality Tools" & "Dev Branch (Author Code)"*

1. **Presenter Talk Track:**
   > *"In modern enterprise AI development, we cannot allow uncontained agents to execute arbitrary code or manage static API secrets on developer machines. Instead, we use Cloud Workstations and Antigravity scaffolding. Prompts and tools are treated as version-controlled code."*

2. **Terminal Walkthrough:**
   ```bash
   # 1. Feature branch creation (Standard Gitflow)
   git checkout -b feat/concierge-mcp-update

   # 2. Inspect Prompts-as-Code and Agent Configuration
   cat agent.yaml
   head -n 30 app/agent.py
   ```

3. **Key Highlight:**
   - Point out that system instructions, tool definitions, and memory configurations are version-controlled in Git, adhering to **SDLC Practice #4: Treat Prompts as Code**.

---

### **Act II: Local Iteration & CodeMender HITL Review (Slide 4 | ~4 Mins)**
*Corresponds to Diagram: "Developer-Authored Quality Checks" & "CodeMender Security Review"*

1. **Presenter Talk Track:**
   > *"Before pushing to remote, developers run local verification. Here, we demonstrate Google CodeMender: an autonomous security agent that detects vulnerabilities in agent tools (like SQL injection in our BigQuery MCP connector), verifies exploitability in a sandbox, synthesizes a fix, and prompts the human for sign-off."*

2. **Terminal Walkthrough:**
   ```bash
   # Run the interactive CodeMender Human-in-the-Loop review demo
   ./agent review
   ```
   *(Or run non-interactively if pressed for time: `python3 scripts/codemender.py demo --non-interactive`)*

3. **What the Audience Sees on Screen:**
   - **Step 1 (Scan):** CodeMender detects `[CM-SEC-001]` raw dynamic query execution in `app/tools.py`.
   - **Step 2 (Verify):** CodeMender runs a sandbox PoC payload (`'; DROP TABLE venues; --`) confirming vulnerability.
   - **Step 3 (Patch):** Autonomous patch synthesis adding `is_safe_readonly_query(query)` AST validation.
   - **Step 4 (HITL Gate):** Developer reviews diff and signs off.
   - **Step 5 (Tests):** Automatic execution of unit tests (`tests/unit`) confirming zero regression.

---

### **Act III: Pull Request, Wiz Scanners & CI Golden Evals (Slide 5 | ~4 Mins)**
*Corresponds to Diagram: "Security Guardrails", "Automated Quality Check", & "Integration Tests"*

1. **Presenter Talk Track:**
   > *"Once pushed, the GitHub Actions CI pipeline triggers. As outlined in the SDLC document, 'Agent confidence completes nothing; only deterministic test evidence in CI logs matters.' In this stage, Wiz SAST/SCA scanners audit policy compliance, while our Golden Evaluation suites run against curated benchmarks."*

2. **Terminal Walkthrough & CI Inspection:**
   ```bash
   # Run the unit test suite locally
   python3 -m unittest discover -s tests/unit

   # Run integration tests
   python3 -m unittest discover -s tests/integration

   # Inspect Golden Evaluation configuration & evalsets
   cat tests/eval/eval_config.json
   ls tests/eval/evalsets/
   ```

3. **What to Show in GitHub Actions (`.github/workflows/ci.yml`):**
   - **Wiz Security Scanners (SAST/SCA):** Central policy check verifying zero high/critical vulnerabilities.
   - **Advisory CodeMender Gate:** Automatic generation of interactive PR comments and step summaries.
   - **Golden Response Evaluation:** Running LLM-as-a-judge rubrics for `relevance` and `helpfulness` against golden baselines (`simulated_session.evalset.json`, `demo_vibe_check.evalset.json`).

---

### **Act IV: Main Branch Merge, Blocking Gate & Deployment (Slide 6 & 7 | ~3 Mins)**
*Corresponds to Diagram: "Merge Approved" ➔ "Main Branch Build" ➔ "Deployment Pipeline" ➔ "GCP"*

1. **Presenter Talk Track:**
   > *"When the PR is approved by the human lead and merged into `main`, the CD pipeline activates. Here, the CodeMender and Wiz gates switch from Advisory to a Strict Blocking Gate (`--fail-on-findings`). If any security issue or policy violation exists, the pipeline halts. Once cleared, Agent CLI packages the manifest and releases the microservice to Vertex AI Reasoning Engine on GCP."*

2. **Terminal Walkthrough:**
   ```bash
   # Test the strict blocking gate
   python3 scripts/codemender.py find --fail-on-findings

   # Inspect deployment manifest for Vertex AI Reasoning Engine
   cat agent.yaml
   cat deploy.py
   ```

---

### **Act V: Live Agent Execution & 'Vibe Check' Demo (~2 Mins)**
*Corresponds to the live customer experience on GCP*

1. **Presenter Talk Track:**
   > *"Finally, let's look at the running agent. The agent uses a ReAct loop over BigQuery to help users discover coffee shops, casual bars, and live jazz across Minneapolis, checking real operating hours and showtimes in real-time."*

2. **Terminal Walkthrough:**
   ```bash
   # Run the live interactive session simulation
   ./agent simulate
   ```
   *(Press [Enter] at each prompt to step through the turns, or pass `--auto` for automated streaming playback)*

3. **Live Demonstration Flow:**
   - **Turn 1 (Morning Coffee):** Agent queries `venues` & `operating_hours`, recommends Spyhouse (6:00 AM) and Dogwood Coffee.
   - **Turn 2 (Live Music):** User asks for live music on Thursday night; Agent queries `events` JOIN `venues`, finding live Hip-Hop & Brass Jam at The Icehouse.
   - **Turn 3 (Hours Verification):** Agent queries venue closing time (midnight), confirming the user can attend without rushing.

---

## 📋 Quick Reference: Terminal Cheat-Sheet

| Action | Command | Purpose |
| :--- | :--- | :--- |
| **Simulate Agent Session** | `./agent simulate` *(or `--auto`)* | Live multi-turn ReAct loop demo with BigQuery queries |
| **CodeMender Security Review** | `./agent review` | Interactive HITL vulnerability detection, PoC & patch demo |
| **CodeMender CI Scan** | `python3 scripts/codemender.py find` | Scan tools for SQL injection & MCP safety |
| **Strict Blocking Gate** | `python3 scripts/codemender.py find --fail-on-findings` | Gate enforced on `main` branch before deployment |
| **Run Unit Tests** | `python3 -m unittest discover -s tests/unit` | Fast local verification of agent & CodeMender logic |
| **Run Integration Tests** | `python3 -m unittest discover -s tests/integration` | App runtime verification |
| **Run Eval Suites** | `./agent test` | LLM-as-a-judge golden evaluation suites |
| **Inspect Manifest** | `cat agent.yaml` | Standard Agent CLI deployment specification |
