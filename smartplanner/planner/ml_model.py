import pandas as pd
import os
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder

# === Step 0: Paths ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # e.g., planner/
DATA_PATH = os.path.join(BASE_DIR, 'data', 'worldwide_travel_cities.csv')  # Ensure this CSV exists
MODEL_PATH = os.path.join(BASE_DIR, 'ml', 'recommendation_model.pkl')  # Save model here
ENCODER_PATH = os.path.join(BASE_DIR, 'ml', 'bud_encoder.pkl')  # ✅ renamed here

# === Step 1: Load and Clean Data ===
print(f"📥 Loading data from: {DATA_PATH}")
df = pd.read_csv(DATA_PATH)

# Drop missing values for key columns
df = df.dropna(subset=[
    'culture', 'adventure', 'nature', 'beaches', 'nightlife',
    'cuisine', 'wellness', 'urban', 'seclusion', 'budget_level'
])

# Standardize budget labels
df['budget_level'] = df['budget_level'].str.strip().str.lower()
df['budget_level'] = df['budget_level'].replace({
    'mid-range': 'medium',
    'budget': 'low',
    'luxury': 'luxury'
})

# === Step 2: Encode Budget Level ===
le_budget = LabelEncoder()
df['budget_level_encoded'] = le_budget.fit_transform(df['budget_level'])

# === Step 3: Define Features and Target ===
features = [
    'culture', 'adventure', 'nature', 'beaches', 'nightlife',
    'cuisine', 'wellness', 'urban', 'seclusion', 'budget_level_encoded'
]
X = df[features]

# Create a synthetic match score as the target
df['match_score'] = df[[
    'culture', 'adventure', 'nature', 'beaches', 'nightlife',
    'cuisine', 'wellness', 'urban', 'seclusion'
]].mean(axis=1)
y = df['match_score']

# === Step 4: Train the Model ===
print("🧠 Training Random Forest Regressor...")
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X, y)

# === Step 5: Save the Model and Encoder ===
os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
joblib.dump(model, MODEL_PATH)
joblib.dump(le_budget, ENCODER_PATH)  # ✅ saved to new path

print("\n✅ Model training complete.")
print(f"📦 Model saved to: {MODEL_PATH}")
print(f"📦 Encoder saved to: {ENCODER_PATH}")
print("🎯 Budget classes:", list(le_budget.classes_))
