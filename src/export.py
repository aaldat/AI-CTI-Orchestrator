import json
import os
from datetime import datetime, timezone
from stix2 import Indicator, AttackPattern, Report, Bundle

def load_enriched_data(filename="enriched_iocs.json"):
    """Loads the data we verified with VirusTotal."""
    filepath = os.path.join(os.path.dirname(__file__), "..", "data", "output", filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def create_stix_bundle(articles):
    stix_objects = []

    for article in articles:
        intel = article.get("extracted_intelligence", {})
        enrichment = article.get("enrichment_data", {})
        
        # Skip this article if the AI didn't find any intelligence
        if not any(intel.values()):
            continue

        article_objects = []
        object_refs = [] # Hold our generated IDs here
        
        # Map our simple keys to complex STIX pattern formats
        stix_pattern_mapping = {
            "ips": "ipv4-addr:value",
            "domains": "domain-name:value",
            "hashes": "file:hashes.'SHA-256'"
        }
        
        # 1. Process Domains, IPs, and Hashes FIRST
        for ioc_type in ["ips", "domains", "hashes"]:
            for item in intel.get(ioc_type, []):
                vt_data = enrichment.get(item, {})
                
                # THE SAFETY NET: Skip if VirusTotal said this format was invalid
                if vt_data.get("status") == "invalid":
                    print(f"Dropping AI Hallucination: {item}")
                    continue
                    
                # Create the strict STIX query pattern
                pattern = f"[{stix_pattern_mapping[ioc_type]} = '{item}']"
                
                # Create the STIX Indicator Object
                indicator = Indicator(
                    name=f"Extracted {ioc_type[:-1].capitalize()}: {item}",
                    pattern_type="stix",
                    pattern=pattern,
                    valid_from=datetime.now(timezone.utc)
                )
                article_objects.append(indicator)
                object_refs.append(indicator.id) # Save the ID

        # 2. Process MITRE ATT&CK Techniques
        for tech in intel.get("mitre_techniques", []):
            attack_pattern = AttackPattern(
                name=f"MITRE Technique {tech}",
                external_references=[
                    {
                        "source_name": "mitre-attack",
                        "external_id": tech
                    }
                ]
            )
            article_objects.append(attack_pattern)
            object_refs.append(attack_pattern.id) # Save the ID

        # 3. Create the STIX Report Object ONLY if we have valid references
        if object_refs:
            report = Report(
                name=article.get("title", "CTI Report"),
                description=f"Source: {article.get('link', 'Unknown')}",
                published=datetime.now(timezone.utc),
                object_refs=object_refs # Pass the fully populated list of IDs
            )
            article_objects.append(report)
            stix_objects.extend(article_objects)

    if not stix_objects:
        print("No valid intelligence found to export.")
        return None

    # 4. Bundle everything together
    return Bundle(objects=stix_objects)

if __name__ == "__main__":
    print("Starting Phase 5: STIX 2.1 Export Pipeline...")
    articles = load_enriched_data()
    
    bundle = create_stix_bundle(articles)
    
    if bundle:
        out_dir = os.path.join(os.path.dirname(__file__), "..", "data", "output")
        os.makedirs(out_dir, exist_ok=True)
        out_file = os.path.join(out_dir, "stix_bundle.json")
        
        with open(out_file, 'w', encoding='utf-8') as f:
            f.write(bundle.serialize(pretty=True))
            
        print(f"\nPhase 5 Complete. Saved STIX 2.1 Bundle to {out_file}")