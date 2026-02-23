# AI-Driven CTI Orchestrator

An automated LLM-powered agent that handles the "Analysis" phase of the Cyber Threat Intelligence (CTI) lifecycle. 

This tool ingests unstructured OSINT data, uses a local Large Language Model (Llama 3.1) to extract Indicators of Compromise (IoCs) and MITRE ATT&CK techniques, verifies them against VirusTotal to prevent AI hallucinations, and packages the findings into standard STIX 2.1 bundles ready for TIP ingestion.

## Architecture & Pipeline

1. **Ingestion:** Parses cybersecurity RSS feeds (e.g., BleepingComputer) to extract raw article text.
2. **AI Analysis:** Uses `Ollama` running Meta's `Llama 3.1` locally to perform Zero-Shot Named Entity Recognition (NER), extracting IPs, domains, hashes, and TTPs.
3. **Contextual Enrichment:** Queries the VirusTotal v3 API to fetch malicious scores and automatically drops invalid indicators (AI hallucinations).
4. **Standardization:** Maps the validated intelligence into STIX 2.1 `Report`, `Indicator`, and `AttackPattern` objects for enterprise compatibility.

## Getting Started

### Prerequisites
* Python 3.10+ (Tested on Python 3.14 / Apple M4 Silicon)
* [Ollama](https://ollama.com/) installed and running locally.
* A free [VirusTotal API Key](https://www.virustotal.com/).

### Tech Stack
* AI/LLM: Llama 3.1 (8B), Ollama Native Python Library
* CTI Standards: STIX 2.1, MITRE ATT&CK Framework
* Data Sources: RSS (feedparser), VirusTotal API (REST)

### Configuration

1. **Install requirements**:
```bash
pip install -r requirements.txt
```

2. **Configure the AI Model**:
```bash
ollama run llama3.1
```

3. **Add your API Key**:
Create a .env file in the root directory abd add your VirusTotal key:
```Plaintext
VT_API_KEY=your_api_key_here
```

### Usage
1. **Add local Threat Artifacts (Optional)**:
you can drop raw text files (like copied phishing email or a threat report) into the data/input_drop/ directory. The pipeline will analyze these alongside the live RSS feeds.

2. **Run the Orchestrator**:
execute the entire pipeline sequentially by typing
```bash
python src/main.py
```

3. **Analyze the results**:
the final output will be generated in data/output/stix_bundle.json
