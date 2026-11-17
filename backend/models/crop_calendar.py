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
