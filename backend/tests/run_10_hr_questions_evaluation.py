"""
Evaluation script testing at least 10 HR in-scope and out-of-scope questions.
Verifies groundedness, citation validity, and guardrail refusal enforcement.
"""

import sys
from pathlib import Path

# Add backend directory to path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.schemas import ChatRequest
from app.services.chat_service import chat_service

TEST_CASES = [
    {
        "id": 1,
        "type": "in_scope",
        "question": "How does Earned Leave accrue every month?",
        "expected_doc": "02_Leave_Policy.pdf",
        "expected_refusal": False,
    },
    {
        "id": 2,
        "type": "in_scope",
        "question": "When is monthly salary credited?",
        "expected_doc": "06_Compensation_and_Benefits_Policy.pdf",
        "expected_refusal": False,
    },
    {
        "id": 3,
        "type": "in_scope",
        "question": "What is the annual wellness allowance?",
        "expected_doc": "06_Compensation_and_Benefits_Policy.pdf",
        "expected_refusal": False,
    },
    {
        "id": 4,
        "type": "in_scope",
        "question": "How many counselling sessions are available?",
        "expected_doc": "06_Compensation_and_Benefits_Policy.pdf",
        "expected_refusal": False,
    },
    {
        "id": 5,
        "type": "in_scope",
        "question": "Can employees take leave during notice period?",
        "expected_doc": "02_Leave_Policy.pdf",
        "expected_refusal": False,
    },
    {
        "id": 6,
        "type": "in_scope",
        "question": "How many years of service are required for gratuity?",
        "expected_doc": "06_Compensation_and_Benefits_Policy.pdf",
        "expected_refusal": False,
    },
    {
        "id": 7,
        "type": "in_scope",
        "question": "What is the probation period for full-time employees?",
        "expected_doc": "01_Employee_Handbook.pdf",
        "expected_refusal": False,
    },
    {
        "id": 8,
        "type": "out_of_scope",
        "question": "What is the capital of France?",
        "expected_doc": None,
        "expected_refusal": True,
    },
    {
        "id": 9,
        "type": "out_of_scope",
        "question": "Who is the CEO of Google?",
        "expected_doc": None,
        "expected_refusal": True,
    },
    {
        "id": 10,
        "type": "out_of_scope",
        "question": "What is the company office WiFi password?",
        "expected_doc": None,
        "expected_refusal": True,
    },
    {
        "id": 11,
        "type": "out_of_scope",
        "question": "What is an employee's favorite food?",
        "expected_doc": None,
        "expected_refusal": True,
    },
    {
        "id": 12,
        "type": "out_of_scope",
        "question": "Write a python script to parse a CSV file",
        "expected_doc": None,
        "expected_refusal": True,
    },
]

def run_evaluation():
    print("=" * 80)
    print("ZYRO HR ASSISTANT — 12-QUESTION GROUNDEDNESS & GUARDRAIL EVALUATION")
    print("=" * 80)
    
    passed_count = 0
    total_count = len(TEST_CASES)
    
    for case in TEST_CASES:
        cid = case["id"]
        q = case["question"]
        qtype = case["type"]
        exp_refusal = case["expected_refusal"]
        exp_doc = case["expected_doc"]
        
        print(f"\n[Test Case {cid}/{total_count}] ({qtype.upper()})")
        print(f"Question: \"{q}\"")
        
        response = chat_service.process_chat(ChatRequest(question=q))
        
        is_refusal = response.is_refusal
        sources = response.sources
        answer_preview = " ".join(response.answer.split()[:25])
        
        print(f"Answer Preview: {answer_preview}...")
        print(f"Is Refusal: {is_refusal} (Expected: {exp_refusal})")
        print(f"Sources Count: {len(sources)}")
        for s in sources:
            print(f"   -> File: {s.file} | Page: {s.page}")
            
        # Assertions
        case_passed = True
        
        if is_refusal != exp_refusal:
            print(f"❌ FAILED: Expected is_refusal={exp_refusal}, got {is_refusal}")
            case_passed = False
            
        if exp_refusal:
            if len(sources) != 0:
                print(f"❌ FAILED: Out-of-scope query returned {len(sources)} sources (expected 0)")
                case_passed = False
        else:
            if len(sources) == 0:
                print("❌ FAILED: In-scope query returned 0 sources")
                case_passed = False
            if exp_doc and not any(exp_doc in s.file for s in sources):
                # Check if expected document was among the retrieved sources
                print(f"⚠️ Note: Expected document '{exp_doc}' was not in sources: {[s.file for s in sources]}")
                
        if case_passed:
            print("✅ PASSED")
            passed_count += 1
        else:
            print("❌ FAILED")
            
    print("\n" + "=" * 80)
    print(f"EVALUATION SUMMARY: {passed_count}/{total_count} Passed ({passed_count/total_count*100:.1f}%)")
    print("=" * 80)
    
    return passed_count == total_count

if __name__ == "__main__":
    success = run_evaluation()
    sys.exit(0 if success else 1)

