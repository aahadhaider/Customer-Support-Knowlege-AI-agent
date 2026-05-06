import time
import json
import os
import re
from datetime import datetime
from pathlib import Path
import google.generativeai as genai




# CONFIG

KNOWLEDGE_BASE_DIR = Path(__file__).parent / "knowledge_base"
LOGS_DIR = Path(__file__).parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)
INTERACTIONS_LOG = LOGS_DIR / "interactions.jsonl"
ESCALATIONS_LOG  = LOGS_DIR / "escalations.jsonl"

ESCALATION_KEYWORDS = [
    "fraud", "complaint", "police", "rbi", "legal", "court",
    "suspended", "aadhaar misuse", "data privacy", "cheated",
    "stolen", "fake", "scam"
]

client = genai.configure(api_key="AIzaSyBaIY2vMzjse3QxLo8nqYI9qYd_EXwhqRQ")  


# TOOL: Read Knowledge Base

def read_knowledge_base() -> str:
    """Load all FAQ markdown files from knowledge_base/."""
    docs = []
    for faq_file in KNOWLEDGE_BASE_DIR.glob("*.md"):
        docs.append(faq_file.read_text(encoding="utf-8"))
    return "\n\n---\n\n".join(docs) if docs else "No knowledge base found."



# TOOL: Check Escalation Triggers

def check_escalation(query_text: str, amount: float = 0) -> dict:
    """
    Rule-based pre-check before sending to LLM.
    Returns escalation decision + reason.
    """
    text_lower = query_text.lower()

    # Keyword check
    for kw in ESCALATION_KEYWORDS:
        if kw in text_lower:
            return {
                "required": True,
                "reason": f"Escalation keyword detected: '{kw}'",
                "priority": "high"
            }

    # Amount check (simple heuristic — look for ₹ followed by number)
    amounts = re.findall(r'[₹rs\.]+\s*([0-9,]+)', text_lower)
    for amt_str in amounts:
        try:
            amt = float(amt_str.replace(",", ""))
            if amt > 10000:
                return {
                    "required": True,
                    "reason": f"Transaction dispute amount ₹{amt:,.0f} exceeds ₹10,000 threshold",
                    "priority": "high"
                }
        except ValueError:
            pass

    return {"required": False, "reason": None, "priority": None}



# TOOL: Log Interaction

def log_interaction(record: dict, is_escalation: bool = False):
    """Append interaction to JSONL log file."""
    log_file = ESCALATIONS_LOG if is_escalation else INTERACTIONS_LOG
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


# CORE: Process Query via Gemini

def process_query_with_llm(query: dict, knowledge_base: str, escalation_info: dict) -> dict:
    """
    Send query + FAQs to google gemini. Ask for structured JSON response.
    """
    system_prompt = f"""You are Customer ai agent, an autonomous customer support agent 
micro-entrepreneur partner platform. it helps small business owners (kiranas, chemists, 
street vendors) provide financial services like money transfers, bill payments, and micro-loans.

YOUR TASK:
1. Read the partner's query carefully
2. Search the FAQ knowledge base below for a matching answer
3. Draft a warm, clear reply (3-5 sentences, simple English)
4. Decide if this needs human escalation (return escalation details if so)
5. Return ONLY a valid JSON object — no markdown, no extra text

KNOWLEDGE BASE:
{knowledge_base}

ESCALATION INFO FROM RULES ENGINE:
{json.dumps(escalation_info, indent=2)}

RESPONSE FORMAT (return exactly this JSON structure):
{{
  "status": "resolved" | "escalated" | "unclear",
  "category": "account | transaction | service | technical | commission | other",
  "confidence": 0.0 to 1.0,
  "draft_reply": "Your reply to the partner here",
  "escalation": {{
    "required": true | false,
    "reason": "reason string or null",
    "priority": "high | medium | low | null",
    "handoff_note": "Detailed note for human agent or null"
  }},
  "faq_matched": "Short description of which FAQ answered this, or null"
}}

IMPORTANT: If the rules engine already flagged escalation as required=true, honour that decision.
"""

    user_message = f"""Partner Query:
- Query ID: {query['query_id']}
- Partner ID: {query['partner_id']}  
- Channel: {query.get('channel', 'app')}
- Query: {query['query_text']}
- Time: {query.get('timestamp', datetime.now().isoformat())}

Please process this query and return the JSON response."""

    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=system_prompt
    )
    response = model.generate_content(
        user_message,
        generation_config=genai.types.GenerationConfig(max_output_tokens=1000)
    )
    raw = response.text.strip()

    
    # Strip markdown fences if present
    raw = re.sub(r'^```json\s*', '', raw)
    raw = re.sub(r'^```\s*', '', raw)
    raw = re.sub(r'\s*```$', '', raw)

    return json.loads(raw)



# MAIN: run_agent

def run_agent(query: dict) -> dict:
    """
    Full autonomous pipeline:
    receive → check escalation → search KB → draft reply → log → return
    """
    print(f"\n{'='*60}")
    print(f"[Agent] Processing Query: {query['query_id']}")
    print(f"[Agent] Partner: {query['partner_id']}")
    print(f"[Agent] Query: {query['query_text']}")
    print(f"{'='*60}")

    # Step 1: Rule-based escalation pre-check
    escalation_info = check_escalation(query["query_text"])
    if escalation_info["required"]:
        print(f"[Agent] ⚠️  Rule-based escalation triggered: {escalation_info['reason']}")

    # Step 2: Load knowledge base
    knowledge_base = read_knowledge_base()
    print(f"[Agent] ✓ Knowledge base loaded ({len(knowledge_base)} chars)")

    # Step 3: Process with Gemini
    print("[Agent] 🤖 Sending to Gemini for analysis...")
    llm_result = process_query_with_llm(query, knowledge_base, escalation_info)

    # Step 4: Build final result
    result = {
        "query_id": query["query_id"],
        "partner_id": query["partner_id"],
        "timestamp": datetime.now().isoformat(),
        "original_query": query["query_text"],
        **llm_result,
        "logged": True
    }

    # Step 5: Log
    is_escalation = result.get("escalation", {}).get("required", False)
    log_interaction(result, is_escalation=is_escalation)

    # Step 6: Print summary
    status_icon = {"resolved": "✅", "escalated": "🚨", "unclear": "❓"}.get(result["status"], "?")
    print(f"\n[Agent] {status_icon} Status: {result['status'].upper()}")
    print(f"[Agent] Category: {result['category']}")
    print(f"[Agent] Confidence: {result['confidence']:.0%}")
    if result.get("faq_matched"):
        print(f"[Agent] FAQ Matched: {result['faq_matched']}")
    print(f"\n[Draft Reply]:\n{result['draft_reply']}")
    if is_escalation:
        esc = result["escalation"]
        print(f"\n[Escalation Note]:\n{esc.get('handoff_note', 'No note')}")
        print(f"[Priority]: {esc.get('priority', 'N/A')}")

    return result



DEMO_QUERIES = [
    {
        "query_id": "Q001",
        "partner_id": "FIN_P_7823",
        "query_text": "My money transfer failed but ₹3,000 was deducted from my wallet. Transaction happened 2 hours ago. What should I do?",
        "channel": "app",
        "timestamp": datetime.now().isoformat()
    },
    {
        "query_id": "Q002",
        "partner_id": "FIN_P_4421",
        "query_text": "I am not getting OTP for login. I tried 5 times. My mobile number is registered.",
        "channel": "whatsapp",
        "timestamp": datetime.now().isoformat()
    },
    {
        "query_id": "Q003",
        "partner_id": "FIN_P_9901",
        "query_text": "Someone has done a fraud transaction of ₹45,000 from my account without my permission. I want to file a complaint and contact RBI.",
        "channel": "app",
        "timestamp": datetime.now().isoformat()
    },
    {
        "query_id": "Q004",
        "partner_id": "FIN_P_3312",
        "query_text": "How do I check my commission earnings for last month?",
        "channel": "app",
        "timestamp": datetime.now().isoformat()
    }
]


if __name__ == "__main__":
    print("=" * 60)
    print("  Eko Customer Support Knowledge Agent — Demo Run")
    print("=" * 60)

    results = []
    for query in DEMO_QUERIES:
        result = run_agent(query)
        results.append(result)
        print("\n" + "-"*60)

    # Summary
    resolved   = sum(1 for r in results if r["status"] == "resolved")
    escalated  = sum(1 for r in results if r["status"] == "escalated")
    unclear    = sum(1 for r in results if r["status"] == "unclear")

    print(f"\n{'='*60}")
    print(f"  BATCH SUMMARY")
    print(f"  Total Queries : {len(results)}")
    print(f"  ✅ Resolved   : {resolved}")
    print(f"  🚨 Escalated  : {escalated}")
    print(f"  ❓ Unclear    : {unclear}")
    print(f"  Logs saved to : {LOGS_DIR}")
    print(f"{'='*60}")
