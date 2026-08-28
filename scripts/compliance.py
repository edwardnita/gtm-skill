"""Universal Physical Product Compliance & Regulatory Matrix Engine."""

from typing import Dict, Any, List

PROHIBITED_MATERIALS = ["lead", "cadmium", "asbestos", "phthalate", "toxic", "mercury", "non-food-grade", "pfas-prohibited", "azo-carcinogen"]

class ComplianceEngine:
    def __init__(self):
        pass

    def evaluate(self, request: Dict[str, Any], baseline: Dict[str, Any]) -> Dict[str, Any]:
        specs = request.get("specifications", {})
        materials = [m.lower() for m in specs.get("materials", [])]
        category = request.get("category", "").lower().strip()
        fcm_declaration = str(specs.get("food_contact_compliance", "")).strip()
        has_electrical = bool(specs.get("electrical_components", False)) or any(k in category for k in ["electric", "audio", "smart", "appliance", "battery", "light"])
        
        target_country = request.get("target_country", "DE")
        target_name = baseline.get("country_name", target_country)
        is_eu = baseline.get("region") == "EU" or baseline.get("eu_oss_applicable", False)
        
        mandatory_actions = []
        kill_trigger = False
        kill_reason = None
        
        # 1. Prohibited material check
        for m in materials:
            for prohibited in PROHIBITED_MATERIALS:
                if prohibited in m:
                    # Ignore safe negations like "non-toxic"
                    if prohibited == "toxic" and ("non-toxic" in m or "nontoxic" in m):
                        continue
                    kill_trigger = True
                    kill_reason = f"Prohibited or hazardous material detected ({m}) violating international consumer product safety and chemical regulations."
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
        
        # 2. Packaging EPR Check
        pkg_baseline = baseline.get("packaging_compliance", {})
        if pkg_baseline:
            framework_name = pkg_baseline.get("framework", "Packaging EPR")
            register_name = pkg_baseline.get("register", "EPR Registry")
            ref_url = pkg_baseline.get("reference_url", "https://europa.eu")
            compliance_frameworks.append({
                "name": framework_name,
                "authority": register_name,
                "url": ref_url
            })
            mandatory_actions.append({
                "title": f"Register with {register_name}",
                "description": f"Mandatory registration under {framework_name} before shipping physical packages to {target_name}.",
                "url": ref_url,
                "estimated_cost_eur": pkg_baseline.get("estimated_annual_fee_eur", 45.00)
            })

        # 3. Category-Specific Regulatory Evaluation
        # A. Food Contact Materials (FCM)
        is_food_related = any(k in category for k in ["coffee", "food", "drink", "kitchen", "cook", "tableware", "cutlery", "bottle", "cup", "carafe"])
        if is_food_related:
            if is_eu:
                compliance_frameworks.append({
                    "name": "EU EC 1935/2004 & LFGB / National FCM Standards",
                    "authority": "EU Food Safety & National Authorities",
                    "url": "https://food.ec.europa.eu/safety/chemical-safety/food-contact-materials_en"
                })
                if not fcm_declaration or "none" in fcm_declaration.lower():
                    score -= 40
                    mandatory_actions.append({
                        "title": "Issue Declaration of Compliance (DoC) for Food Contact Materials",
                        "description": "Products in contact with food/beverages require lab migration testing and a valid DoC under EU EC 1935/2004.",
                        "url": "https://food.ec.europa.eu/safety/chemical-safety/food-contact-materials_en",
                        "estimated_cost_eur": 350.00
                    })
                else:
                    score -= 5  # minor documentation maintenance
            else:
                compliance_frameworks.append({
                    "name": f"{target_name} Food Contact & Safety Standards",
                    "authority": f"{target_name} Health & Food Authority",
                    "url": "https://wto.org"
                })
                mandatory_actions.append({
                    "title": f"Verify {target_name} Food Contact Import Clearance",
                    "description": f"Ensure product compliance with {target_name} local import standards for kitchenware.",
                    "url": "https://wto.org",
                    "estimated_cost_eur": 250.00
                })

        # B. Electronics & Electrical Appliances
        elif has_electrical or any(k in category for k in ["electronic", "audio", "gadget", "smart", "appliance", "hardware"]):
            if is_eu:
                compliance_frameworks.append({
                    "name": "CE Marking (LVD 2014/35/EU, EMC 2014/30/EU, RoHS 2011/65/EU)",
                    "authority": "European Single Market Standards",
                    "url": "https://single-market-economy.ec.europa.eu/single-market/ce-marking_en"
                })
                compliance_frameworks.append({
                    "name": "EU WEEE Directive (2012/19/EU) Producer Responsibility",
                    "authority": f"{target_name} National WEEE Register",
                    "url": "https://environment.ec.europa.eu/topics/waste-and-recycling/waste-electrical-and-electronic-equipment-weee_en"
                })
                mandatory_actions.append({
                    "title": "Affix CE Mark & Prepare EU Declaration of Conformity (DoC)",
                    "description": "Ensure technical documentation file and RoHS compliance testing are complete.",
                    "url": "https://single-market-economy.ec.europa.eu/single-market/ce-marking_en",
                    "estimated_cost_eur": 500.00
                })
                mandatory_actions.append({
                    "title": f"Register with {target_name} National WEEE Register",
                    "description": "Mandatory e-waste producer registration before selling electrical devices.",
                    "url": "https://environment.ec.europa.eu",
                    "estimated_cost_eur": 120.00
                })
            else:
                compliance_frameworks.append({
                    "name": f"{target_name} Electrical Safety & FCC/Telecomm Certification",
                    "authority": f"{target_name} Standards Agency",
                    "url": "https://wto.org"
                })
                mandatory_actions.append({
                    "title": f"Obtain {target_name} Electrical Safety & Radio Certification",
                    "description": f"Verify local electrical voltage, plug type, and electromagnetic compliance for {target_name}.",
                    "url": "https://wto.org",
                    "estimated_cost_eur": 450.00
                })

        # C. Cosmetics, Skincare & Personal Care
        elif any(k in category for k in ["cosmetic", "skin", "beauty", "hair", "serum", "lotion", "soap", "cream"]):
            if is_eu:
                compliance_frameworks.append({
                    "name": "EU Cosmetics Regulation (EC 1223/2009)",
                    "authority": "European Commission CPNP",
                    "url": "https://ec.europa.eu/growth/sectors/cosmetics/legislation_en"
                })
                mandatory_actions.append({
                    "title": "Complete CPNP Notification & Cosmetic Product Safety Report (CPSR)",
                    "description": "Designate an EU Responsible Person (RP) and submit formula notification to CPNP portal.",
                    "url": "https://ec.europa.eu/growth/sectors/cosmetics/cpnp_en",
                    "estimated_cost_eur": 850.00
                })
            else:
                compliance_frameworks.append({
                    "name": f"{target_name} Cosmetic Registration & Safety Dossier",
                    "authority": f"{target_name} Drug & Cosmetic Administration",
                    "url": "https://wto.org"
                })
                mandatory_actions.append({
                    "title": f"Submit {target_name} Cosmetic Product Registration",
                    "description": f"File ingredient safety dossier and labeling translation with {target_name} authorities.",
                    "url": "https://wto.org",
                    "estimated_cost_eur": 600.00
                })

        # D. Apparel, Footwear & Textiles
        elif any(k in category for k in ["apparel", "clothing", "textile", "shirt", "pant", "shoe", "footwear", "fashion", "sweater", "wool", "garment", "dress", "jacket", "sock"]):
            if is_eu:
                compliance_frameworks.append({
                    "name": "EU Textile Fiber Labeling Regulation (EU 1007/2011) & REACH",
                    "authority": "European Chemicals Agency (ECHA)",
                    "url": "https://echa.europa.eu/regulations/reach/legislation"
                })
                mandatory_actions.append({
                    "title": f"Affix Destination Language Textile Composition Label ({target_country})",
                    "description": f"Provide 100% accurate fiber percentages in the official language of {target_name}.",
                    "url": "https://europa.eu",
                    "estimated_cost_eur": 0.00
                })
            else:
                compliance_frameworks.append({
                    "name": f"{target_name} Textile Care Labeling & Import Regulations",
                    "authority": f"{target_name} Customs & Trade Standards",
                    "url": "https://wto.org"
                })

        # E. Toys & Children Products
        elif any(k in category for k in ["toy", "baby", "child", "game", "plush"]):
            if is_eu:
                compliance_frameworks.append({
                    "name": "EU Toy Safety Directive (2009/48/EC) & EN 71 Testing",
                    "authority": "European Toy Safety Standards",
                    "url": "https://single-market-economy.ec.europa.eu/sectors/toys/toy-safety_en"
                })
                mandatory_actions.append({
                    "title": "Conduct EN 71 Toy Safety Lab Certification & CE Marking",
                    "description": "Mandatory mechanical, flammability, and chemical migration testing for children products.",
                    "url": "https://single-market-economy.ec.europa.eu/sectors/toys/toy-safety_en",
                    "estimated_cost_eur": 1200.00
                })

        # F. General Consumer Goods (GPSR Fallback)
        else:
            if is_eu:
                compliance_frameworks.append({
                    "name": "EU General Product Safety Regulation (GPSR - Regulation EU 2023/988)",
                    "authority": "European Product Safety Network",
                    "url": "https://commission.europa.eu/business-economy-euro/product-safety-and-requirements/product-safety/general-product-safety-regulation_en"
                })
                mandatory_actions.append({
                    "title": "Designate EU Economic Operator & Affix Traceability Batch Label",
                    "description": "Ensure manufacturer name, postal address, email, and product batch ID are marked on item/packaging.",
                    "url": "https://commission.europa.eu/business-economy-euro/product-safety-and-requirements/product-safety/general-product-safety-regulation_en",
                    "estimated_cost_eur": 0.00
                })

        # 4. Tax & Customs Reporting
        if is_eu:
            compliance_frameworks.append({
                "name": "EU One-Stop Shop (OSS) VAT Directive",
                "authority": "European Commission Taxation & Customs",
                "url": "https://taxation-customs.ec.europa.eu/one-stop-shop_en"
            })
            mandatory_actions.append({
                "title": f"Enable EU OSS Quarterly Reporting for {target_name}",
                "description": f"Declare destination VAT ({int(baseline.get('standard_vat_rate', 0.20)*100)}%) via home EU Member State OSS portal.",
                "url": "https://taxation-customs.ec.europa.eu/one-stop-shop_en",
                "estimated_cost_eur": 0.00
            })
        else:
            compliance_frameworks.append({
                "name": f"{target_name} Customs Declaration & Import Duty Clearance",
                "authority": f"{target_name} Customs Authority",
                "url": "https://wto.org"
            })
            mandatory_actions.append({
                "title": f"Configure DDP (Delivered Duty Paid) Commercial Invoicing for {target_name}",
                "description": f"Pre-pay import tariffs and local sales tax ({int(baseline.get('standard_vat_rate', 0.15)*100)}%) to prevent parcel refusal at delivery.",
                "url": "https://wto.org",
                "estimated_cost_eur": 0.00
            })

        return {
            "compliance_score": max(0, score),
            "kill_trigger_triggered": False,
            "kill_reason": None,
            "mandatory_actions": mandatory_actions,
            "compliance_frameworks": compliance_frameworks
        }
