import json
import os
import ollama

def load_raw_data(filename="latest_intel.json"):
    """Loads the raw RSS data we grabbed in Phase 2."""
    filepath = os.path.join(os.path.dirname(__file__), "..", "data", "raw", filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def extract_iocs(text):
    """Sends the text to the local LLM using the native Ollama library."""
    system_prompt = """You are an expert Cyber Threat Intelligence (CTI) analyst.
    Read the following cybersecurity article summary and extract any Indicators of Compromise (IoCs) and MITRE ATT&CK techniques.
    
    Strictly return a JSON object with the following keys:
    - "ips": [list of IP addresses]
    - "domains": [list of domains]
    - "hashes": [list of file hashes like MD5, SHA256]
    - "mitre_techniques": [list of MITRE technique IDs, e.g., "T1566"]
    
    If you do not find any of these, return an empty list for that key. Do not include any markdown formatting or explanations, only the raw JSON object."""

    response = ollama.chat(
        model='llama3.1',
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': text}
        ],
        format='json', # Ollama's native JSON mode
        options={'temperature': 0.1}
    )
    
    return response['message']['content']

if __name__ == "__main__":
    print("Starting Phase 3: AI Extraction Pipeline...")
    articles = load_raw_data()
    
    extracted_data = []
    
    for article in articles:
        print(f"Analyzing: {article['title']}")
        if article['summary']:
            try:
                # Pass the article summary to the LLM
                ioc_json_str = extract_iocs(article['summary'])
                
                # Convert the LLM's text output back into a real Python dictionary
                iocs = json.loads(ioc_json_str)
                
                extracted_data.append({
                    "title": article['title'],
                    "link": article['link'],
                    "extracted_intelligence": iocs
                })
                print("Extraction successful.")
            except Exception as e:
                print(f"Failed to parse LLM output. Error: {e}")
        else:
            print("No summary available to analyze.")
            
    # Save the final structured data
    out_dir = os.path.join(os.path.dirname(__file__), "..", "data", "output")
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "extracted_iocs.json")
    
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(extracted_data, f, indent=4)
        
    print(f"\nPhase 3 Complete. Saved structured IoCs to {out_file}")