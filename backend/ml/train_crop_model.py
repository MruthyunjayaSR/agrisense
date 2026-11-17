"""
AgriSense - Crop Recommendation Model Training Pipeline
Algorithm: Random Forest Classifier
Features: Nitrogen (N), Phosphorus (P), Potassium (K), Temperature, Humidity, Soil pH, Rainfall
Target: Optimal Crop (22 Indian Crops)
"""

import os
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import classification_report, accuracy_score, precision_recall_fscore_support, confusion_matrix

BASE_DIR = Path(__file__).resolve().parent.parent
SAVED_MODELS_DIR = BASE_DIR / "ml" / "saved_models"
SAVED_MODELS_DIR.mkdir(parents=True, exist_ok=True)

def generate_agricultural_dataset(samples_per_crop=150):
    """
    Synthesize representative agricultural dataset based on ICAR agronomic benchmarks
    """
    benchmarks = {
        "Rice": {"N": (70, 110), "P": (35, 60), "K": (35, 55), "temp": (24, 34), "hum": (75, 95), "ph": (5.5, 7.2), "rain": (150, 300)},
        "Wheat": {"N": (80, 130), "P": (45, 65), "K": (30, 50), "temp": (14, 25), "hum": (45, 70), "ph": (6.0, 7.5), "rain": (40, 100)},
        "Tomato": {"N": (60, 100), "P": (45, 75), "K": (50, 85), "temp": (20, 30), "hum": (55, 75), "ph": (6.0, 7.0), "rain": (80, 150)},
        "Cotton": {"N": (90, 140), "P": (35, 60), "K": (40, 60), "temp": (25, 36), "hum": (50, 75), "ph": (6.5, 8.2), "rain": (60, 120)},
        "Maize": {"N": (75, 120), "P": (40, 65), "K": (35, 55), "temp": (20, 32), "hum": (55, 80), "ph": (5.8, 7.5), "rain": (70, 160)},
        "Potato": {"N": (80, 110), "P": (50, 80), "K": (70, 110), "temp": (15, 24), "hum": (50, 75), "ph": (5.0, 6.5), "rain": (50, 100)},
        "Onion": {"N": (50, 80), "P": (40, 65), "K": (45, 70), "temp": (18, 28), "hum": (50, 70), "ph": (6.0, 7.2), "rain": (40, 90)},
        "Soybean": {"N": (20, 50), "P": (50, 80), "K": (30, 55), "temp": (22, 32), "hum": (60, 85), "ph": (6.0, 7.5), "rain": (90, 180)},
        "Groundnut": {"N": (15, 40), "P": (40, 70), "K": (40, 65), "temp": (24, 34), "hum": (50, 75), "ph": (5.8, 7.0), "rain": (60, 130)},
        "Sugarcane": {"N": (120, 180), "P": (50, 85), "K": (60, 100), "temp": (26, 38), "hum": (70, 90), "ph": (6.0, 7.8), "rain": (140, 250)},
        "Pomegranate": {"N": (30, 60), "P": (20, 45), "K": (40, 70), "temp": (24, 38), "hum": (30, 55), "ph": (6.5, 8.5), "rain": (30, 80)},
        "Grapes": {"N": (40, 70), "P": (30, 55), "K": (60, 90), "temp": (18, 30), "hum": (40, 65), "ph": (6.5, 8.0), "rain": (40, 90)}
    }
    
    np.random.seed(42)
    rows = []
    for crop, ranges in benchmarks.items():
        for _ in range(samples_per_crop):
            rows.append({
                "N": np.random.uniform(*ranges["N"]) + np.random.normal(0, 3),
                "P": np.random.uniform(*ranges["P"]) + np.random.normal(0, 2),
                "K": np.random.uniform(*ranges["K"]) + np.random.normal(0, 2),
                "temperature": np.random.uniform(*ranges["temp"]) + np.random.normal(0, 0.8),
                "humidity": np.clip(np.random.uniform(*ranges["hum"]) + np.random.normal(0, 2), 10, 100),
                "ph": np.clip(np.random.uniform(*ranges["ph"]) + np.random.normal(0, 0.1), 3.5, 9.5),
                "rainfall": max(np.random.uniform(*ranges["rain"]) + np.random.normal(0, 5), 10),
                "crop": crop
            })
            
    df = pd.DataFrame(rows)
    return df

def train_model():
    print("=" * 60)
    print("AGRISENSE: TRAINING RANDOM FOREST CROP RECOMMENDATION MODEL")
    print("=" * 60)
    
    df = generate_agricultural_dataset()
    print(f"Generated agricultural dataset with {len(df)} samples across {df['crop'].nunique()} crops.")
    
    feature_cols = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
    X = df[feature_cols].values
    y = df["crop"].values
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded)
    
    model = RandomForestClassifier(n_estimators=120, max_depth=15, min_samples_split=3, random_state=42)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    precision, recall, f1, _ = precision_recall_fscore_support(y_test, y_pred, average="weighted")
    
    print("\nMODEL EVALUATION RESULTS:")
    print(f"Accuracy:  {accuracy * 100:.2f}%")
    print(f"Precision: {precision * 100:.2f}%")
    print(f"Recall:    {recall * 100:.2f}%")
    print(f"F1-Score:  {f1 * 100:.2f}%")
    
    # Save Model Bundle
    model_path = SAVED_MODELS_DIR / "crop_model.joblib"
    bundle = {
        "model": model,
        "scaler": scaler,
        "label_encoder": le,
        "features": feature_cols,
        "accuracy": accuracy,
        "classes": list(le.classes_)
    }
    joblib.dump(bundle, model_path)
    print(f"\nSaved trained model bundle to: {model_path}")

if __name__ == "__main__":
    train_model()
