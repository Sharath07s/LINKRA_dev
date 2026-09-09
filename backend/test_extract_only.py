import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.nlp.llm_extractor import extract_entities_llm

def test_extraction():
    text = "John Doe (Phone: 555-1234) met with Jane Smith at the abandoned warehouse on 5th street. Jane Smith was seen driving a red Toyota."
    
    print("Testing extraction...")
    candidates = extract_entities_llm(text)
    
    print("Extraction successful.")
    print("Entities Found:", len(candidates))
    for c in candidates:
        print(f" - {c.entity_type}: {c.raw_text} ({c.confidence})")
    
if __name__ == "__main__":
    test_extraction()
