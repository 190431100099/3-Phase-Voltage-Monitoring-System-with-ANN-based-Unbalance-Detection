import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.callbacks import EarlyStopping
import joblib

df = pd.read_csv(r'E:\PROJECK\tobi\dataset_tegangan_balance_unbalance.csv')

required_columns = ['R', 'S', 'T', 'I_R', 'I_S', 'I_T', 'Kondisi']
missing = set(required_columns) - set(df.columns)
if missing:
    raise ValueError(f"Kolom berikut tidak ditemukan di dataset: {missing}")

X = df[['R', 'S', 'T', 'I_R', 'I_S', 'I_T']].values
y = df['Kondisi'].values  # 0: balance, 1: unbalance

scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

# Model ANN
model = Sequential([
    Dense(16, input_dim = 6, activation='relu'),
    Dense(8, activation='relu'),
    Dense(1, activation='sigmoid')
])

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

early_stop = EarlyStopping(monitor='val_accuracy', patience=10, restore_best_weights=True, verbose=1)

history = model.fit(
    X_train, y_train,
    validation_data=(X_test, y_test),
    epochs=200,           # Max epoch
    batch_size=16,
    callbacks=[early_stop],
    verbose=1
)

loss, accuracy = model.evaluate(X_test, y_test)
print(f"Akurasi terbaik pada data uji: {accuracy:.2f}")

plt.plot(history.history['accuracy'], label='Training')
plt.plot(history.history['val_accuracy'], label='Validation')
plt.title('Akurasi Training vs Validation')
plt.xlabel('Epoch')
plt.ylabel('Akurasi')
plt.grid()
plt.legend()
plt.show()

y_pred = (model.predict(X_test) > 0.5).astype(int)
plt.plot(y_test[:50], label='Label Asli')
plt.plot(y_pred[:50], label='Prediksi', linestyle='--')
plt.title('Tren Prediksi vs Label (50 sample)')
plt.xlabel('Sample')
plt.ylabel('Kelas')
plt.legend()
plt.grid()
plt.show()

model.save('model_ann.h5')
joblib.dump(scaler, 'scaler.pkl')
print("Model dan scaler berhasil disimpan.")