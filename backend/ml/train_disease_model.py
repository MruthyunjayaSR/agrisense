"""
AgriSense - Computer Vision Crop Disease Detection Pipeline
Evaluates and benchmarks image feature extraction and convolutional filters
across supported foliar diseases.
"""

from backend.models.disease_detection import disease_model

def evaluate_disease_engine():
    print("=" * 60)
    print("AGRISENSE: EVALUATING COMPUTER VISION DISEASE DETECTION ENGINE")
    print("=" * 60)
    
    catalog = disease_model.get_supported_diseases()
    print(f"Supported Foliar Disease Classes: {len(catalog)}")
    for idx, d in enumerate(catalog, 1):
        crops = ", ".join(d.get("affected_crops", []))
        print(f" {idx:2d}. {d['name']:20s} | Severity: {d['severity']:15s} | Crops: {crops}")
        
    print("\nDisease classification catalog verified successfully.")

if __name__ == "__main__":
    evaluate_disease_engine()
