import random
import pandas as pd

def hitung_unbalance(R, S, T, I_R, I_S, I_T):
    v_avg = (R + S + T) / 3
    i_avg = (I_R + I_S + I_T) / 3

    deviasi_V = max(abs(R - v_avg), abs(S - v_avg), abs(T - v_avg))
    deviasi_I = max(abs(I_R - i_avg), abs(I_S - i_avg), abs(I_T - i_avg))

    percent_unbalance_V = (deviasi_V / v_avg) * 100
    percent_unbalance_I = (deviasi_I / i_avg) * 100

    # UBAH: Threshold tegangan diturunkan jadi 2% agar sensitif di range 230-245
    label = 1 if (percent_unbalance_V > 2 or percent_unbalance_I > 2) else 0

    return v_avg, i_avg, percent_unbalance_V, percent_unbalance_I, label

# Jumlah data
N = 5000
data = []

N_balance = N // 2
N_unbalance = N - N_balance

# --- Data Balance ---
for _ in range(N_balance):
    # UBAH: Range tegangan 230 - 245
    base_V = random.uniform(230, 245)
    base_I = random.uniform(1.0, 1.2)

    # Tegangan dan arus hampir seimbang
    R = base_V + random.uniform(-0.5, 0.5) # Deviasi diperkecil untuk balance murni
    S = base_V + random.uniform(-0.5, 0.5)
    T = base_V + random.uniform(-0.5, 0.5)

    I_R = base_I + random.uniform(-0.02, 0.02)
    I_S = base_I + random.uniform(-0.02, 0.02)
    I_T = base_I + random.uniform(-0.02, 0.02)

    v_avg, i_avg, percent_unbalance_V, percent_unbalance_I, label = hitung_unbalance(R, S, T, I_R, I_S, I_T)

    data.append({
        "R": round(R, 2),
        "S": round(S, 2),
        "T": round(T, 2),
        "I_R": round(I_R, 2),
        "I_S": round(I_S, 2),
        "I_T": round(I_T, 2),
        "Kondisi": label
    })

# --- Data Unbalance ---
for _ in range(N_unbalance):
    # UBAH: Range tegangan 230 - 245
    R = random.uniform(230, 245)
    S = random.uniform(230, 245)
    T = random.uniform(230, 245)

    I_R = random.uniform(0.8, 1.5)
    I_S = random.uniform(0.8, 1.5)
    I_T = random.uniform(0.8, 1.5)

    v_avg, i_avg, percent_unbalance_V, percent_unbalance_I, label = hitung_unbalance(R, S, T, I_R, I_S, I_T)

    data.append({
        "R": round(R, 2),
        "S": round(S, 2),
        "T": round(T, 2),
        "I_R": round(I_R, 2),
        "I_S": round(I_S, 2),
        "I_T": round(I_T, 2),
        "Kondisi": label
    })

# Simpan ke DataFrame dan acak barisnya
df = pd.DataFrame(data).sample(frac=1).reset_index(drop=True)
df.to_csv("dataset_tegangan_balance_unbalance.csv", index=False)

print(df['Kondisi'].value_counts())
print(df.head())