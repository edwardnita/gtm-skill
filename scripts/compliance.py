"""Compliance & Regulatory Matrix Engine."""

from typing import Dict, Any, List

PROHIBITED_MATERIALS = ["lead", "cadmium", "asbestos", "phthalate", "toxic", "mercury", "non-food-grade"]

class ComplianceEngine:
    def __init__(self):
        pass

    def evaluate(self, request: Dict[str, Any], baseline: Dict[str, Any]) -> Dict[str, Any]:
        specs = request.get("specifications", {})
        materials = [m.lower() for m in specs.get("materials", [])]
        fcm_declaration = str(specs.get("food_contact_compliance", "")).strip()
        
        target_country = request.get("target_country", "")
        pkg_baseline = baseline.get("packaging_compliance", {})
        fcm_baseline = baseline.get("food_contact_compliance", {})
        
        mandatory_actions = []
        kill_trigger = False
        kill_reason = None
        
        # 1. Prohibited material check
        for m in materials:
            for prohibited in PROHIBITED_MATERIALS:
                if prohibited in m:
                    kill_trigger = True
                    kill_reason = f"Prohibited or hazardous material detected ({m}) violating EU REACH & German LFGB food safety regulations."
                    break
            if kill_trigger:
                break
                
        if kill_trigger:
            return {
                "compliance_score": 0,
                "kill_trigger_triggered": True,
                "kill_reason": kill_reason,
                "mandatory_actions": [],
                "compliance_frameworks": []
            }
            
        score = 100
        compliance_frameworks = []
        
        # 2. Packaging Act Check (e.g. German VerpackG / LUCID)
        if pkg_baseline:
            framework_name = pkg_baseline.get("framework", "Packaging EPR")
            register_name = pkg_baseline.get("register", "EPR Registry")
            ref_url = pkg_baseline.get("reference_url", "")
            compliance_frameworks.append({
                "name": framework_name,
                "authority": register_name,
                "url": ref_url
            })
            mandatory_actions.append({
                "title": f"Register with {register_name}",
                "description": f"Mandatory registration under {framework_name} before shipping physical packages to {target_country}.",
                "url": ref_url,
                "estimated_cost_eur": pkg_baseline.get("estimated_annual_fee_eur", 45.00)
            })
            
        # 3. Food Contact Materials Check (FCM)
        is_food_related = "coffee" in request.get("category", "").lower() or "food" in request.get("category", "").lower() or "drink" in request.get("category", "").lower()
        if is_food_related:
            if not fcm_declaration or "none" in fcm_declaration.lower():
                score -= 40
                mandatory_actions.append({
                    "title": "Issue Declaration of Compliance (DoC) for Food Contact Materials",
                    "description": "Products intended for hot coffee contact require lab migration testing and a valid DoC under EU EC 1935/2004.",
                    "url": fcm_baseline.get("reference_url", "https://www.bfr.bund.de/en/food_contact_materials-231.html"),
                    "estimated_cost_eur": 350.00
                })
            else:
                compliance_frameworks.append({
                    "name": fcm_baseline.get("framework", "EU EC 1935/2004"),
                    "authority": "BfR (Federal Institute for Risk Assessment)",
                    "url": fcm_baseline.get("reference_url", "https://www.bfr.bund.de/en/food_contact_materials-231.html")
                })
                # minor reduction if purely self-declared without accredited lab cert mention
                score -= 5
                
        # 4. EU VAT OSS Check
        if baseline.get("eu_oss_applicable"):
            compliance_frameworks.append({
                "name": "EU One-Stop Shop (OSS) VAT Directive",
                "authority": "European Commission Taxation & Customs",
                "url": "https://taxation-customs.ec.europa.eu/one-stop-shop_en"
            })
            mandatory_actions.append({
                "title": "Enable EU OSS Quarterly Reporting",
                "description": f"Declare German destination VAT ({int(baseline.get('standard_vat_rate', 0.19)*100)}%) via Romanian ANAF OSS portal.",
                "url": "https://taxation-customs.ec.europa.eu/one-stop-shop_en",
                "estimated_cost_eur": 0.00
            })

        return {
            "compliance_score": max(0, score),
            "kill_trigger_triggered": False,
            "kill_reason": None,
            "mandatory_actions": mandatory_actions,
            "compliance_frameworks": compliance_frameworks
        }
