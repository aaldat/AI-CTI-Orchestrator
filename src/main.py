import subprocess
import sys
import os

def run_script(script_name):
    """Runs a Python script and checks for errors."""
    print(f"\n{'='*60}")
    print(f"🚀 EXECUTING: {script_name}")
    print(f"{'='*60}")
    
    # Ensure we run the script from the correct directory relative to main.py
    script_path = os.path.join(os.path.dirname(__file__), script_name)
    
    # Use sys.executable to ensure we use the virtual environment's Python
    result = subprocess.run([sys.executable, script_path])
    
    if result.returncode != 0:
        print(f"\n[-] Fatal Error: {script_name} failed. Halting pipeline.")
        sys.exit(1)

if __name__ == "__main__":
    print("""
    ================================================
       AI-DRIVEN CTI ORCHESTRATOR PIPELINE
    ================================================
    """)
    
    pipeline = [
        "ingest.py",   # Phase 2: Collect Data
        "analyzer.py", # Phase 3: AI Extraction
        "enrich.py",   # Phase 4: Contextual Enrichment
        "export.py"    # Phase 5: STIX 2.1 Export
    ]
    
    for script in pipeline:
        run_script(script)
        
    print("\n[+] ========================================================")
    print("[+] 🎯 PIPELINE COMPLETE! ")
    print("[+] Final STIX 2.1 Bundle is ready in: data/output/stix_bundle.json")
    print("[+] ========================================================\n")