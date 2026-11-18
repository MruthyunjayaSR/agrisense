import datetime
from typing import List, Dict

class CropCalendarEngine:
    """
    Intelligent Crop Calendar & Lifecycle Monitoring Engine
    Calculates scientifically sound agronomic schedules based on crop variety,
    sowing date, growth stages, and weather alerts.
    """

    # Agricultural crop growth profiles (duration in days, stages and critical operations)
    CROP_SCHEDULE_TEMPLATES = {
        "Rice": {
            "total_duration": 120,
            "stages": [
                {"name": "Land Preparation", "start_day": 0, "end_day": 7},
                {"name": "Nursery Sowing", "start_day": 8, "end_day": 25},
                {"name": "Transplanting", "start_day": 26, "end_day": 35},
                {"name": "Tillering & Vegetative", "start_day": 36, "end_day": 65},
                {"name": "Panicle Initiation & Flowering", "start_day": 66, "end_day": 85},
                {"name": "Grain Filling & Milking", "start_day": 86, "end_day": 105},
                {"name": "Maturity & Harvesting", "start_day": 106, "end_day": 120}
            ],
            "milestone_tasks": [
                {"day_offset": 0, "name": "Deep Summer Ploughing & Soil Solarization", "type": "soil", "priority": "Medium", "stage": "Land Preparation"},
                {"day_offset": 7, "name": "Seed Treatment with Trichoderma (10g/kg)", "type": "sow", "priority": "High", "stage": "Nursery Sowing"},
                {"day_offset": 8, "name": "Nursery Bed Wet Sowing", "type": "plant", "priority": "High", "stage": "Nursery Sowing"},
                {"day_offset": 18, "name": "Nursery Top Dressing with Urea", "type": "fertilize", "priority": "Medium", "stage": "Nursery Sowing"},
                {"day_offset": 28, "name": "Field Puddling & Basal NPK (50% N, 100% P & K)", "type": "fertilize", "priority": "Critical", "stage": "Transplanting"},
                {"day_offset": 30, "name": "Main Field Seedling Transplanting (2-3 per hill)", "type": "plant", "priority": "Critical", "stage": "Transplanting"},
                {"day_offset": 45, "name": "First Hand Weeding & Cono-Weeder Run", "type": "care", "priority": "Medium", "stage": "Tillering & Vegetative"},
                {"day_offset": 55, "name": "Active Tillering First Top Dressing (Urea + Zinc)", "type": "fertilize", "priority": "High", "stage": "Tillering & Vegetative"},
                {"day_offset": 70, "name": "Panicle Initiation Stage Irrigation Check", "type": "irrigate", "priority": "High", "stage": "Panicle Initiation & Flowering"},
                {"day_offset": 75, "name": "Prophylactic Spray for Stem Borer & Leaf Folder", "type": "spray", "priority": "High", "stage": "Panicle Initiation & Flowering"},
                {"day_offset": 90, "name": "Milking Stage Standing Water Maintenance (2-3cm)", "type": "irrigate", "priority": "Medium", "stage": "Grain Filling & Milking"},
                {"day_offset": 110, "name": "Terminal Drain-out (10 days before harvest)", "type": "irrigate", "priority": "High", "stage": "Maturity & Harvesting"},
                {"day_offset": 120, "name": "Harvesting at 85% Golden Grain Color", "type": "harvest", "priority": "Critical", "stage": "Maturity & Harvesting"}
            ]
        },
        "Wheat": {
            "total_duration": 135,
            "stages": [
                {"name": "Field Preparation", "start_day": 0, "end_day": 5},
                {"name": "Sowing & Germination", "start_day": 6, "end_day": 20},
                {"name": "Crown Root Initiation (CRI)", "start_day": 21, "end_day": 35},
                {"name": "Tillering & Jointing", "start_day": 36, "end_day": 70},
                {"name": "Booting & Heading", "start_day": 71, "end_day": 90},
                {"name": "Flowering & Milking", "start_day": 91, "end_day": 115},
                {"name": "Dough & Maturity", "start_day": 116, "end_day": 135}
            ],
            "milestone_tasks": [
                {"day_offset": 0, "name": "Fine Tilth Pre-sowing Irrigation (Palewa)", "type": "irrigate", "priority": "High", "stage": "Field Preparation"},
                {"day_offset": 5, "name": "Basal Fertilization (Full P & K, 1/3rd Nitrogen)", "type": "fertilize", "priority": "Critical", "stage": "Field Preparation"},
                {"day_offset": 6, "name": "Line Sowing with Seed-cum-Fertilizer Drill", "type": "sow", "priority": "Critical", "stage": "Sowing & Germination"},
                {"day_offset": 21, "name": "CRI Stage 1st Irrigation (CRITICAL for yield)", "type": "irrigate", "priority": "Critical", "stage": "Crown Root Initiation"},
                {"day_offset": 25, "name": "Broadleaf Weed Spray (Sulfosulfuron)", "type": "spray", "priority": "High", "stage": "Crown Root Initiation"},
                {"day_offset": 42, "name": "Tillering Stage 2nd Irrigation & 1st Top Dressing", "type": "fertilize", "priority": "High", "stage": "Tillering & Jointing"},
                {"day_offset": 65, "name": "Late Jointing Stage 3rd Irrigation", "type": "irrigate", "priority": "Medium", "stage": "Tillering & Jointing"},
                {"day_offset": 85, "name": "Flowering Stage 4th Irrigation & Rust Monitoring", "type": "monitor", "priority": "High", "stage": "Booting & Heading"},
                {"day_offset": 105, "name": "Milking Stage 5th Light Irrigation", "type": "irrigate", "priority": "Medium", "stage": "Flowering & Milking"},
                {"day_offset": 135, "name": "Combine Harvesting at 12-14% Moisture", "type": "harvest", "priority": "Critical", "stage": "Dough & Maturity"}
            ]
        },
        "Tomato": {
            "total_duration": 130,
            "stages": [
                {"name": "Nursery & Seedling", "start_day": 0, "end_day": 25},
                {"name": "Transplanting", "start_day": 26, "end_day": 35},
                {"name": "Early Vegetative", "start_day": 36, "end_day": 55},
                {"name": "Flowering & Fruit Set", "start_day": 56, "end_day": 80},
                {"name": "Fruit Enlargement", "start_day": 81, "end_day": 105},
                {"name": "Harvesting Flushes", "start_day": 106, "end_day": 130}
            ],
            "milestone_tasks": [
                {"day_offset": 0, "name": "Pro-tray Nursery Sowing with Cocopeat", "type": "sow", "priority": "High", "stage": "Nursery & Seedling"},
                {"day_offset": 15, "name": "Drenching with 19:19:19 Soluble Fertilizer", "type": "fertilize", "priority": "Medium", "stage": "Nursery & Seedling"},
                {"day_offset": 26, "name": "Main Field Raised Beds & Drip Line Laying", "type": "soil", "priority": "High", "stage": "Transplanting"},
                {"day_offset": 28, "name": "Seedling Root Dip & Evening Transplanting", "type": "plant", "priority": "Critical", "stage": "Transplanting"},
                {"day_offset": 40, "name": "Bamboo Staking / Trellis Tying & Earthing Up", "type": "care", "priority": "High", "stage": "Early Vegetative"},
                {"day_offset": 45, "name": "Preventative Neem Spray for Whitefly & Leaf Miner", "type": "spray", "priority": "Medium", "stage": "Early Vegetative"},
                {"day_offset": 60, "name": "Flowering Stage Boron & Calcium Spray (0.2%)", "type": "spray", "priority": "High", "stage": "Flowering & Fruit Set"},
                {"day_offset": 75, "name": "Fruit Set Fertigation with Potassium Nitrate (13:0:45)", "type": "fertilize", "priority": "High", "stage": "Fruit Enlargement"},
                {"day_offset": 90, "name": "Fruit Borer Pheromone Trap Installation", "type": "monitor", "priority": "Medium", "stage": "Fruit Enlargement"},
                {"day_offset": 105, "name": "First Harvest Flush at Breaker / Turning Stage", "type": "harvest", "priority": "Critical", "stage": "Harvesting Flushes"},
                {"day_offset": 125, "name": "Final Picking & Post-Harvest Grade Sorting", "type": "harvest", "priority": "High", "stage": "Harvesting Flushes"}
            ]
        }
    }

    def get_frontend_calendar_events(self, crop: str = "Rice"):
        """
        Formats events specifically for index.html calendar widget expectations:
        List of { month: int, day: int, event: str, type: str }
        """
        crop_key = crop if crop in self.CROP_SCHEDULE_TEMPLATES else "Rice"
        template = self.CROP_SCHEDULE_TEMPLATES[crop_key]
        
        # Anchor to representative season:
        # Kharif (Rice) starts June; Rabi (Wheat) starts November; Tomato starts July
        base_months = {"Rice": 6, "Wheat": 11, "Tomato": 7}
        start_month = base_months.get(crop_key, 6)
        start_year = datetime.datetime.now().year
        
        start_date = datetime.date(start_year, start_month, 1)
        
        events = []
        for task in template["milestone_tasks"]:
            task_date = start_date + datetime.timedelta(days=task["day_offset"])
            events.append({
                "month": task_date.month,
                "day": task_date.day,
                "event": task["name"],
                "type": task["type"]
            })
            
        return events

    def generate_full_crop_calendar(self, crop_name: str, sowing_date_str: str, variety: str = "Standard", user_id: str = None, farm_id: str = None):
        """
        Generates dynamically dated agricultural lifecycle calendar from farmer's actual sowing date
        """
        crop_key = crop_name if crop_name in self.CROP_SCHEDULE_TEMPLATES else "Rice"
        template = self.CROP_SCHEDULE_TEMPLATES[crop_key]
        
        try:
            sowing_date = datetime.date.fromisoformat(sowing_date_str)
        except Exception:
            sowing_date = datetime.date.today()
            
        expected_harvest = sowing_date + datetime.timedelta(days=template["total_duration"])
        
        tasks = []
        for task in template["milestone_tasks"]:
            t_date = sowing_date + datetime.timedelta(days=task["day_offset"])
            tasks.append({
                "user_id": user_id,
                "crop_id": None, # Will be set on crop association
                "task_name": task["name"],
                "task_description": f"Recommended operation during {task['stage']} for {crop_name} ({variety}).",
                "task_date": t_date.isoformat(),
                "growth_stage": task["stage"],
                "task_type": task["type"],
                "priority": task["priority"],
                "status": "Pending"
            })
            
        return {
            "crop_name": crop_name,
            "crop_variety": variety,
            "sowing_date": sowing_date.isoformat(),
            "expected_harvest_date": expected_harvest.isoformat(),
            "total_duration_days": template["total_duration"],
            "tasks": tasks
        }

    def get_daily_advisory(self, crop_name: str = "Rice", month: int = 6, day: int = 15, sowing_date_str: str = None):
        """
        AI Crop Health Monitoring and Date-Specific Agricultural Advisory
        Provides exact health status, scouting checklists, and irrigation/fertilizer/spray
        recommendations for any selected calendar date.
        """
        crop_key = crop_name if crop_name in self.CROP_SCHEDULE_TEMPLATES else "Rice"
        template = self.CROP_SCHEDULE_TEMPLATES[crop_key]
        year = datetime.datetime.now().year

        base_months = {"Rice": 6, "Wheat": 11, "Tomato": 7}
        sowing_month = base_months.get(crop_key, 6)

        try:
            if sowing_date_str:
                sowing_date = datetime.date.fromisoformat(sowing_date_str)
            else:
                sowing_date = datetime.date(year, sowing_month, 1)
        except Exception:
            sowing_date = datetime.date(year, sowing_month, 1)

        try:
            target_date = datetime.date(year, int(month), int(day))
        except Exception:
            target_date = sowing_date + datetime.timedelta(days=14)

        # Days relative to sowing
        days_from_sowing = (target_date - sowing_date).days
        if days_from_sowing < 0:
            # If target month is prior in the year, wrap to agricultural crop year
            days_from_sowing += 365

        total_days = template["total_duration"]
        capped_days = min(max(days_from_sowing, 0), total_days)

        # Find current stage
        current_stage = template["stages"][-1]["name"]
        for st in template["stages"]:
            if st["start_day"] <= capped_days <= st["end_day"]:
                current_stage = st["name"]
                break

        # Check for matching milestone on this exact day
        matched_milestone = None
        for task in template["milestone_tasks"]:
            task_date = sowing_date + datetime.timedelta(days=task["day_offset"])
            if task_date.month == int(month) and task_date.day == int(day):
                matched_milestone = task
                break

        # Crop-specific detailed health & agronomy recommendations
        advisory_kb = {
            "Rice": {
                "Land Preparation": {
                    "health_status": "Pre-Planting Soil Preparation",
                    "health_score": 98,
                    "checklist": [
                        "Perform 2–3 deep ploughings to expose resting pupae to sunlight",
                        "Incorporate 10 tonnes/ha well-decomposed FYM or vermicompost",
                        "Ensure field bunds are reinforced to retain standing water"
                    ],
                    "irrigation": "Palewa irrigation: Settle the field with 5–7 cm water 3 days before final puddling.",
                    "fertilizer": "Apply basal zinc sulphate @ 25 kg/ha if soil is deficient.",
                    "protection": "Solarize nursery beds with clear polythene sheets for 15 days.",
                    "action": "Complete final laser levelling for uniform water distribution."
                },
                "Nursery Sowing": {
                    "health_status": "Seedling Emergence & Root Vigour",
                    "health_score": 96,
                    "checklist": [
                        "Check for uniform germination across nursery beds (>85% target)",
                        "Monitor seedling density to avoid crowding and damping off",
                        "Inspect for early leaf folder or thrips attack"
                    ],
                    "irrigation": "Maintain saturated soil condition without fully submerging delicate seedlings.",
                    "fertilizer": "Foliar spray of 0.5% Urea solution at day 12 for robust green shoot emergence.",
                    "protection": "Seed treated with Carbendazim 2g/kg or Trichoderma viride 10g/kg.",
                    "action": "Drain water overnight and replenish fresh water at sunrise."
                },
                "Transplanting": {
                    "health_status": "Seedling Establishment & Anchorage",
                    "health_score": 95,
                    "checklist": [
                        "Transplant 21–25 day-old seedlings at 20 cm x 15 cm spacing",
                        "Place 2–3 seedlings per hill at shallow depth (2–3 cm)",
                        "Inspect root system for root-knot nematode swelling"
                    ],
                    "irrigation": "Maintain 2–3 cm shallow standing water for the first 7 days.",
                    "fertilizer": "Apply 50% Nitrogen, 100% Phosphorus, and 50% Potassium as basal dose.",
                    "protection": "Root dip in Pseudomonas fluorescens (20g/L) for 30 minutes prior to planting.",
                    "action": "Gap filling within 7-10 days of transplanting to ensure uniform plant population."
                },
                "Tillering & Vegetative": {
                    "health_status": "Active Canopy Expansion & Crown Tillering",
                    "health_score": 94,
                    "checklist": [
                        "Count active tillers per hill (target: 10–14 healthy tillers)",
                        "Inspect underside of leaves for Yellow Stem Borer egg masses",
                        "Monitor for bacterial leaf blight lesions on leaf tips"
                    ],
                    "irrigation": "Maintain alternate wetting and drying (AWD) with 2–4 cm water depth.",
                    "fertilizer": "Top-dress with Urea @ 30–35 kg/acre + 5 kg Zinc Sulphate at active tillering.",
                    "protection": "Spray Azadirachtin (Neem 1500 ppm @ 3ml/L) or Cartap Hydrochloride 50 SP @ 2g/L.",
                    "action": "Run cono-weeder between rows to aerate soil and incorporate weeds as green manure."
                },
                "Panicle Initiation & Flowering": {
                    "health_status": "Critical Reproductive Phase",
                    "health_score": 97,
                    "checklist": [
                        "Inspect flag leaf health (crucial for 80% grain filling)",
                        "Check for neck blast and sheath blight lesions on stems",
                        "Monitor weather for cloudy or excessively rainy forecast"
                    ],
                    "irrigation": "CRITICAL: Maintain 5 cm continuous standing water. Water stress now causes spikelet sterility.",
                    "fertilizer": "Apply final 25% Nitrogen top-dressing + Potassium Chloride (MOP) @ 15 kg/acre.",
                    "protection": "Prophylactic foliar spray of Tricyclazole 75% WP @ 0.6g/L for blast prevention.",
                    "action": "Avoid spraying chemical pesticides during peak morning flowering hours (9 AM–11 AM)."
                },
                "Grain Filling & Milking": {
                    "health_status": "Kernel Starch Accumulation",
                    "health_score": 95,
                    "checklist": [
                        "Inspect ear heads for Gundhi Bug (smell bug) infestations in early mornings",
                        "Check for false smut yellow powdery balls on grains",
                        "Verify heavy panicle bending without premature lodging"
                    ],
                    "irrigation": "Provide light irrigation every 4–5 days; keep soil moist without stagnation.",
                    "fertilizer": "Foliar spray of 1% Potassium Schoenite or 13:0:45 to enhance grain weight and shine.",
                    "protection": "Dust Malathion 5% DP @ 10 kg/acre on field borders to repel Gundhi bug.",
                    "action": "Install bird scares and ribbon flags around the perimeter."
                },
                "Maturity & Harvesting": {
                    "health_status": "Crop Physiological Ripening",
                    "health_score": 99,
                    "checklist": [
                        "Check grain moisture (optimum harvesting moisture is 20–22%)",
                        "Verify 85% of panicles have turned golden yellow",
                        "Ensure field is completely dry to support combine harvester machinery"
                    ],
                    "irrigation": "Completely stop irrigation 10–12 days prior to expected harvest date.",
                    "fertilizer": "Zero fertilizer application. Allow natural crop senescence.",
                    "protection": "No chemical sprays. Prepare clean, disinfected threshing yards.",
                    "action": "Harvest on a dry, sunny morning and sun-dry paddy to 14% storage moisture."
                }
            },
            "Wheat": {
                "Field Preparation": {
                    "health_status": "Pre-Rabi Soil Tillage",
                    "health_score": 98,
                    "checklist": ["Plough field to fine crumb tilth", "Incorporate basal compost", "Laser-level field"],
                    "irrigation": "Palewa pre-sowing irrigation.",
                    "fertilizer": "Basal DAP @ 50 kg/acre + MOP @ 20 kg/acre.",
                    "protection": "Termite protection: Chlorpyrifos 20 EC @ 2ml/kg seed.",
                    "action": "Calibrate seed drill for 100 kg/ha seed rate."
                },
                "Sowing & Germination": {
                    "health_status": "Radicle Emergence & Coleoptile Growth",
                    "health_score": 96,
                    "checklist": ["Check 85%+ germination emergence", "Monitor line spacing at 20-22 cm", "Check soil crusting"],
                    "irrigation": "Light sprinkler or misting if top soil crusts.",
                    "fertilizer": "Full P&K placed 5 cm below seed level.",
                    "protection": "Seed treatment with Vitavax (Carboxin) 2g/kg.",
                    "action": "Ensure uniform sowing depth of 4–5 cm."
                },
                "Crown Root Initiation (CRI)": {
                    "health_status": "CRI Root Development (Critical Stage)",
                    "health_score": 95,
                    "checklist": ["Inspect crown root nodes at 21 days", "Check for Phalaris minor (gulli danda) weeds", "Assess crown vigor"],
                    "irrigation": "FIRST & MOST CRITICAL IRRIGATION at 21 days. Yield loss of 25% if missed.",
                    "fertilizer": "First top dressing: Urea @ 45 kg/acre immediately after 1st irrigation.",
                    "protection": "Spray Clodinafop-propargyl 15% WP @ 160g/acre for wild oats and canary grass.",
                    "action": "Do not allow water stagnation for more than 6 hours."
                },
                "Tillering & Jointing": {
                    "health_status": "Stem Elongation & Tiller Synchronization",
                    "health_score": 95,
                    "checklist": ["Count 4–6 tillers per plant", "Check for Yellow/Stripe Rust stripes on leaves", "Inspect leaf color"],
                    "irrigation": "Second irrigation at 40-45 days.",
                    "fertilizer": "Second top dressing: Urea @ 45 kg/acre + Zinc 5kg.",
                    "protection": "Spray Propiconazole 25 EC (Tilt @ 1ml/L) if yellow rust patches appear.",
                    "action": "Hoeing and manual weeding between lines."
                },
                "Booting & Heading": {
                    "health_status": "Ear Head Emergence",
                    "health_score": 96,
                    "checklist": ["Inspect flag leaf for spots", "Monitor aphid colonies on young heads", "Check stem strength"],
                    "irrigation": "Third irrigation at boot stage (65-70 days).",
                    "fertilizer": "Foliar spray of 2% Urea or 0.2% Boron.",
                    "protection": "Spray Thiamethoxam 25 WG @ 0.3g/L if aphids exceed 5/tiller.",
                    "action": "Avoid irrigation on windy days to prevent lodging."
                },
                "Flowering & Milking": {
                    "health_status": "Grain Synthesis & Starch Deposition",
                    "health_score": 94,
                    "checklist": ["Check grain development in earheads", "Assess flag leaf longevity", "Monitor terminal heat stress"],
                    "irrigation": "Fourth irrigation at milking stage (85-90 days).",
                    "fertilizer": "Foliar spray of 0:0:50 (Potassium sulphate 1%) to protect against heat stress.",
                    "protection": "Monitor for armyworm or head blight.",
                    "action": "Keep soil moist to buffer root temperatures."
                },
                "Dough & Maturity": {
                    "health_status": "Grain Hardening & Desiccation",
                    "health_score": 99,
                    "checklist": ["Check grain hardness with thumbnail test", "Verify yellow-straw canopy color", "Check grain moisture"],
                    "irrigation": "Cease all irrigation 15 days before harvest.",
                    "fertilizer": "No fertilizer.",
                    "protection": "Prepare clean storage bags with aluminium phosphide fumigation tablets.",
                    "action": "Harvest at 12–14% grain moisture using combine harvester."
                }
            },
            "Tomato": {
                "Nursery & Seedling": {
                    "health_status": "Pro-Tray Seedling Growth",
                    "health_score": 97,
                    "checklist": ["Check for 4–5 true leaves", "Inspect for damping off root constriction", "Check for whitefly presence"],
                    "irrigation": "Gentle rose-can watering twice daily.",
                    "fertilizer": "Drench with 19:19:19 (3g/L) at 12 days.",
                    "protection": "Cover nursery with 40-mesh insect-proof netting.",
                    "action": "Harden seedlings 3 days before transplanting by reducing water."
                },
                "Transplanting": {
                    "health_status": "Field Establishment on Raised Beds",
                    "health_score": 95,
                    "checklist": ["Inspect 60cm row spacing", "Ensure mulch film hole centering", "Check root contact with soil"],
                    "irrigation": "Immediate drip irrigation (2 hours) post transplanting in late afternoon.",
                    "fertilizer": "Basal FYM 10t/ha + 50kg DAP + 50kg MOP.",
                    "protection": "Root dip in Trichoderma (10g/L) + Imidacloprid (0.5ml/L).",
                    "action": "Replace missing or dead plants within 5 days."
                },
                "Early Vegetative": {
                    "health_status": "Lateral Branching & Staking Phase",
                    "health_score": 94,
                    "checklist": ["Check bamboo trellis support stability", "Inspect foliage for Early Blight target spots", "Check for Leaf Miner trails"],
                    "irrigation": "Drip irrigation every 2 days (4-6 liters per plant).",
                    "fertilizer": "Fertigation with 12:61:0 (Mono Ammonium Phosphate) @ 3kg/acre.",
                    "protection": "Spray Mancozeb 75 WP @ 2.5g/L or Neem oil 3ml/L.",
                    "action": "Tie main stem to trellis wires with jute twine."
                },
                "Flowering & Fruit Set": {
                    "health_status": "Blossom Flush & Fruit Cluster Initiation",
                    "health_score": 96,
                    "checklist": ["Monitor flower drop percentage", "Check for Blossom End Rot (Calcium deficiency)", "Inspect for Fruit Borer moth eggs"],
                    "irrigation": "Strict uniform drip irrigation to prevent flower abortion.",
                    "fertilizer": "Foliar spray of Calcium Nitrate (2g/L) + Boron (1g/L) at 10-day intervals.",
                    "protection": "Install Helicoverpa pheromone traps (5 traps/acre). Spray Spinosad 45 SC @ 0.3ml/L if caterpillars seen.",
                    "action": "Prune lower suckers (side shoots) up to 20 cm from ground."
                },
                "Fruit Enlargement": {
                    "health_status": "Fruit Bulk Expansion & Calyx Health",
                    "health_score": 95,
                    "checklist": ["Inspect fruit sizing and skin firmness", "Check for late blight fruit rot", "Ensure trellis holds fruit cluster weight"],
                    "irrigation": "Regular drip moisture; avoid heavy irrigation after dry spell to prevent fruit cracking.",
                    "fertilizer": "Fertigate with Potassium Nitrate (13:0:45) @ 4kg/acre twice weekly.",
                    "protection": "Spray Azoxystrobin + Difenoconazole @ 1ml/L for fruit rot prevention.",
                    "action": "Remove yellowing or diseased bottom leaves for aeration."
                },
                "Harvesting Flushes": {
                    "health_status": "Multi-Pick Harvesting & Grade Selection",
                    "health_score": 98,
                    "checklist": ["Pick at breaker/pink stage for long distance transport", "Grade tomatoes into A, B, and C tiers", "Harvest with intact calyx"],
                    "irrigation": "Maintain light drip irrigation between pickings.",
                    "fertilizer": "Post-picking booster: 19:19:19 @ 2kg/acre to support subsequent fruit sets.",
                    "protection": "Maintain 3-day pre-harvest waiting interval (PHI) for any crop protection.",
                    "action": "Pack in ventilated plastic crates of 20 kg capacity; store in shaded cool packhouse."
                }
            }
        }

        crop_advisories = advisory_kb.get(crop_key, advisory_kb["Rice"])
        stage_advisory = crop_advisories.get(current_stage, list(crop_advisories.values())[0])

        return {
            "crop": crop_key,
            "date": target_date.strftime("%d %B %Y"),
            "month": int(month),
            "day": int(day),
            "crop_age_days": capped_days,
            "total_duration": total_days,
            "growth_stage": current_stage,
            "health_status": stage_advisory["health_status"],
            "health_score": stage_advisory["health_score"],
            "checklist": stage_advisory["checklist"],
            "recommendations": {
                "irrigation": stage_advisory["irrigation"],
                "fertilizer": stage_advisory["fertilizer"],
                "protection": stage_advisory["protection"],
                "action": stage_advisory["action"]
            },
            "milestone_task": matched_milestone["name"] if matched_milestone else None,
            "milestone_type": matched_milestone["type"] if matched_milestone else None
        }

    def monitor_crop_progress(self, crop_name: str, sowing_date_str: str):
        """
        Calculates live growth progress:
        - Current age in days
        - Current growth stage
        - Next upcoming task
        - Days remaining for next task
        - Percentage completed
        """
        crop_key = crop_name if crop_name in self.CROP_SCHEDULE_TEMPLATES else "Rice"
        template = self.CROP_SCHEDULE_TEMPLATES[crop_key]
        
        try:
            sowing_date = datetime.date.fromisoformat(sowing_date_str)
        except Exception:
            sowing_date = datetime.date.today() - datetime.timedelta(days=32)
            
        today = datetime.date.today()
        age_days = max((today - sowing_date).days, 0)
        
        # Determine current stage
        current_stage = template["stages"][-1]["name"]
        for st in template["stages"]:
            if st["start_day"] <= age_days <= st["end_day"]:
                current_stage = st["name"]
                break
                
        pct = min(round((age_days / template["total_duration"]) * 100, 1), 100.0)
        
        # Find next task
        next_task = None
        days_remaining = 0
        for task in template["milestone_tasks"]:
            if task["day_offset"] >= age_days:
                next_task = task
                days_remaining = task["day_offset"] - age_days
                break
                
        if not next_task:
            next_task = {"name": "Final Harvest Completed", "type": "harvest", "priority": "Medium"}
            days_remaining = 0
            
        return {
            "crop": crop_name,
            "crop_age_days": age_days,
            "current_growth_stage": current_stage,
            "progress_percentage": pct,
            "next_activity": next_task["name"],
            "days_remaining_for_next_task": days_remaining,
            "expected_harvest_date": (sowing_date + datetime.timedelta(days=template["total_duration"])).isoformat()
        }

# Global singleton
crop_calendar = CropCalendarEngine()
