#  Customer Support Knowledge Agent

A fully autonomous AI agent that handles first-line customer support fors micro-entrepreneur partner platform.

Built as a project demonstrating **autonomous AI agent design** using OpenClaw-style `.md` Claw instructions, tool use, structured workflows, and end-to-end task ownership.

---

## What This Agent Does

| Step | Action |
|------|--------|
| 1 | Receives a partner query (JSON input) |
| 2 | Runs **rule-based escalation check** (keywords + amount thresholds) |
| 3 | Loads the **FAQ knowledge base** from `knowledge_base/faqs.md` |
| 4 | Sends query + FAQs to **Claude** for understanding and answer drafting |
| 5 | Returns a structured response: category, confidence, draft reply |
| 6 | **Escalates** high-risk queries with a detailed handoff note |
| 7 | **Logs** every interaction to `logs/interactions.jsonl` and `logs/escalations.jsonl` |

---

## Project Structure

```
 customer-support-agent/
├── customer_support_agent.md    ← Claw instruction file (agent definition)
├── agent.py                     ← Autonomous agent code
├── knowledge_base/
│   └── faqs.md                  ← FAQ knowledge base (editable)
├── logs/
│   ├── interactions.jsonl       ← All interaction logs (auto-created)
│   └── escalations.jsonl        ← Escalation logs (auto-created)
└── README.md                    ← This file
```

---

## Setup

### 1. Clone / download this project

```bash
git clone <your-repo-url>
cd eko-customer-support-agent
```

### 2. Install dependencies

```bash
pip install googlegemini
```

### 3. Set your Gemini API key

```bash
export GEMINI_API_KEY="sk-ant-..."
```

Get a key at: https://aistudio.google.com/app/api-keys?project=gen-lang-client-0903089319

### 4. Run the demo

```bash
python agent.py
```

This runs 4 sample queries and shows the agent's responses in your terminal.

---

## Sample Output

```

[Agent] Processing Query: Q001
[Agent] Partner: FIN_P_7823
[Agent] Query: My money transfer failed but ₹3,000 was deducted...
-----------------------------------------
[Agent] ✓ Knowledge base loaded (3842 chars)
[Agent] 🤖 Sending to GEMINI AI for analysis...

[Agent] ✅ Status: RESOLVED
[Agent] Category: transaction
[Agent] Confidence: 92%
[Agent] FAQ Matched: Failed transaction auto-reversal policy

[Draft Reply]:
Hi! I understand your concern — a failed transaction with a deducted 
amount is stressful. The good news is that failed transactions are 
automatically reversed within 2–4 hours...
```

---

## Using the Agent in Your Code

```python
from agent import run_agent

query = {
    "query_id": "Q005",
    "partner_id": "FIN_P_1234",
    "query_text": "How do I apply for a micro-loan for my customer?",
    "channel": "app"
}

result = run_agent(query)
print(result["draft_reply"])
```

---

## Escalation Rules

The agent escalates automatically when:
- Transaction dispute **> ₹10,000**
- Query contains keywords: **fraud, RBI, legal, police, court, suspended**
- Aadhaar misuse or data privacy concerns mentioned

Escalated queries include a full **handoff note** for the human agent.

---

## Extending This Agent

| Extension | How |
|-----------|-----|
| Add new FAQs | Edit `knowledge_base/faqs.md` |
| Connect to WhatsApp | Use OpenClaw's WhatsApp plugin + route messages to `run_agent()` |
| Add to OpenClaw | Import `customer_support_agent.md` as a Claw via ClawHub |
| Multi-language | Modify system prompt to detect and match partner's language |
| Live DB lookup | Add a tool that queries transaction status via Eko's API |

---

## The Claw File

`customer_support_agent.md` is the **Claw instruction file** — a structured `.md` document that defines the agent's identity, workflow, tools, escalation rules, and input/output format. This is the format used in OpenClaw and similar autonomous agent frameworks to define agent behaviour declaratively.

---

## Author

Built for Internship application — demonstrating autonomous AI agent design with real workflow ownership, structured instructions, tool use, and escalation logic.
