"""
Synthetic session-log generator.

20,000 legitimate sessions + 400 replayed-cookie sessions (2% base rate).
Attackers come from three profiles of increasing sophistication:
  naive       - no attempt to match the victim
  proxy_ua    - proxy in a similar region + copied user agent
  full_emul   - location, user agent and fingerprint largely matched

ALL probabilities are ASSUMPTIONS of the study, not measurements of real
attacks. No real victim data, malware or marketplace content is used.
"""
import os
import numpy as np
import pandas as pd

SEED = 42
N_LEGIT = 20_000
N_ATTACK = 400

FEATURES = [
    "asn_changed", "distance_km", "ua_match", "fp_match",
    "concurrent_use", "session_age_hours", "sensitive_action", "fresh_mfa",
]


def make_legit(rng, n):
    traveling = rng.random(n) < 0.0065          # travellers / VPN users
    distance = np.where(
        traveling,
        rng.uniform(500, 6000, n),
        np.abs(rng.normal(0, 25, n)),
    )
    return pd.DataFrame({
        "asn_changed": (rng.random(n) < 0.08).astype(int),
        "distance_km": distance.round(1),
        "ua_match": (rng.random(n) < 0.985).astype(int),
        "fp_match": (rng.random(n) < 0.985).astype(int),
        "concurrent_use": (rng.random(n) < 0.01).astype(int),
        "session_age_hours": rng.exponential(6, n).round(2),
        "sensitive_action": (rng.random(n) < 0.02).astype(int),
        "fresh_mfa": (rng.random(n) < 0.97).astype(int),
        "label": 0,
        "profile": "legit",
    })


# probability tables per attacker profile (assumptions of the study)
PROFILES = {
    "naive":     dict(asn=0.97, far=0.97, ua=0.05, fp=0.03, conc=0.20, sens=0.45, mfa=0.02, age=(30, 24)),
    "proxy_ua":  dict(asn=0.90, far=0.35, ua=0.92, fp=0.25, conc=0.15, sens=0.40, mfa=0.02, age=(30, 24)),
    "full_emul": dict(asn=0.35, far=0.03, ua=0.97, fp=0.88, conc=0.03, sens=0.30, mfa=0.02, age=(20, 16)),
}


def make_attack(rng, n, name):
    p = PROFILES[name]
    far = rng.random(n) < p["far"]
    distance = np.where(far, rng.uniform(550, 9000, n), rng.uniform(5, 450, n))
    mean, sd = p["age"]
    age = np.clip(rng.normal(mean, sd, n), 1, None)
    return pd.DataFrame({
        "asn_changed": (rng.random(n) < p["asn"]).astype(int),
        "distance_km": distance.round(1),
        "ua_match": (rng.random(n) < p["ua"]).astype(int),
        "fp_match": (rng.random(n) < p["fp"]).astype(int),
        "concurrent_use": (rng.random(n) < p["conc"]).astype(int),
        "session_age_hours": age.round(2),
        "sensitive_action": (rng.random(n) < p["sens"]).astype(int),
        "fresh_mfa": (rng.random(n) < p["mfa"]).astype(int),
        "label": 1,
        "profile": name,
    })


def generate(seed=SEED):
    rng = np.random.default_rng(seed)
    parts = [make_legit(rng, N_LEGIT)]
    split = [N_ATTACK // 3, N_ATTACK // 3, N_ATTACK - 2 * (N_ATTACK // 3)]
    for name, n in zip(PROFILES, split):
        parts.append(make_attack(rng, n, name))
    df = pd.concat(parts, ignore_index=True)
    return df.sample(frac=1, random_state=seed).reset_index(drop=True)


if __name__ == "__main__":
    out_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    os.makedirs(out_dir, exist_ok=True)
    df = generate()
    path = os.path.join(out_dir, "synthetic_sessions.csv")
    df.to_csv(path, index=False)
    print(f"Saved {len(df)} sessions -> {os.path.abspath(path)}")
    print(df["profile"].value_counts().to_string())
