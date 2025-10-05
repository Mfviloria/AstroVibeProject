import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report
import joblib

KOI = pd.read_csv("koi_completo.csv")

features = [
    'koi_model_snr', 'koi_prad', 'koi_sma', 'koi_teq', 'koi_period',
    'koi_duration', 'koi_depth', 'koi_steff', 'koi_slogg', 'koi_srad', 'koi_time0bk'
]
target = 'koi_disposition'

data = KOI.dropna(subset=features + [target])

X = data[features]
y = data[target]

encoder = LabelEncoder()
y = encoder.fit_transform(y)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_test_s = scaler.transform(X_test)

model = RandomForestClassifier(n_estimators=200, random_state=42)
model.fit(X_train_s, y_train)

y_pred = model.predict(X_test_s)
print(classification_report(y_test, y_pred, target_names=encoder.classes_))

joblib.dump(model, "exoplanet_classifier.joblib")
joblib.dump(encoder, "label_encoder.joblib")
joblib.dump(scaler, "scaler.joblib")