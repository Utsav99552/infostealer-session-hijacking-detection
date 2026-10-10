"""Three detectors compared in the study."""
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline

THRESHOLD_B = 6.0


def detector_a(df):
    """A: legacy impossible-travel rule - flag distance above 500 km."""
    return (df["distance_km"] > 500).astype(int).values


def score_b(df):
    """B: hand-weighted score over all eight signals."""
    return (
        2.0 * df["asn_changed"]
        + 2.0 * (df["distance_km"] > 500)
        + 1.0 * (df["distance_km"] > 100)
        + 1.5 * (1 - df["ua_match"])
        + 2.0 * (1 - df["fp_match"])
        + 2.0 * df["concurrent_use"]
        + 1.0 * (df["session_age_hours"] > 24)
        + 2.0 * df["sensitive_action"]
        + 1.5 * (1 - df["fresh_mfa"])
    ).values


def detector_b(df):
    return (score_b(df) >= THRESHOLD_B).astype(int)


def build_detector_c(seed=42):
    """C: class-weighted logistic regression (scaled inputs)."""
    return make_pipeline(
        LogisticRegression(class_weight={0: 1, 1: 30}, max_iter=5000, C=1.0,
                           random_state=seed),
    )
