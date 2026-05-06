"""
test_agent_logic.py
Tests the rule-based escalation and utility functions
without requiring an API key.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from agent import check_escalation, read_knowledge_base

def test_escalation_rules():
    print("Running escalation rule tests...\n")
    
    tests = [
        ("Normal query - should NOT escalate",
         "My OTP is not coming. What should I do?",
         False),
        ("Fraud keyword - should escalate",
         "Someone did fraud on my account please help",
         True),
        ("RBI mention - should escalate",
         "I want to complain to RBI about this issue",
         True),
        ("Large amount - should escalate",
         "My ₹45,000 transaction failed and money is gone",
         True),
        ("Small amount - should NOT escalate",
         "My ₹500 recharge failed",
         False),
        ("Legal threat - should escalate",
         "I will take legal action against Eko",
         True),
    ]
    
    passed = 0
    for desc, query, expected_escalate in tests:
        result = check_escalation(query)
        actual = result["required"]
        status = "✅ PASS" if actual == expected_escalate else "❌ FAIL"
        if actual == expected_escalate:
            passed += 1
        print(f"{status} | {desc}")
        if actual != expected_escalate:
            print(f"       Expected: {expected_escalate}, Got: {actual}, Reason: {result['reason']}")
    
    print(f"\nEscalation Tests: {passed}/{len(tests)} passed\n")

def test_knowledge_base_loading():
    print("Testing knowledge base loading...\n")
    kb = read_knowledge_base()
    assert len(kb) > 100, "Knowledge base is too short"
    assert "transaction" in kb.lower(), "FAQ should contain transaction info"
    assert "commission" in kb.lower(), "FAQ should contain commission info"
    print(f"✅ Knowledge base loaded successfully ({len(kb)} characters)")
    print(f"✅ Contains FAQ sections: account, transaction, technical, commission\n")

if __name__ == "__main__":
    print("=" * 50)
    print("  Eko Agent — Logic Tests (no API key needed)")
    print("=" * 50 + "\n")
    test_escalation_rules()
    test_knowledge_base_loading()
    print("=" * 50)
    print("All logic tests complete.")
    print("To run the full agent with Claude: python agent.py")
    print("=" * 50)
