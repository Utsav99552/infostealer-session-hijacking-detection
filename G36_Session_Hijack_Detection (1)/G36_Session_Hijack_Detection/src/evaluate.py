"""
Runs the full pipeline: generate data -> split -> 3 detectors -> metrics/plots.
Usage:  python src/evaluate.py
"""
import os
import sys
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import (precision_score, recall_score, f1_score,
                             confusion_matrix, roc_auc_score, roc_curve)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generate_dataset import generate, FEATURES, SEED
from detectors import detector_a, detector_b, score_b, build_detector_c

if getattr(sys, "frozen", False):          # running as a PyInstaller .exe
    ROOT = os.path.dirname(sys.executable)  # save results next to the exe
else:
    ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.abspath(os.path.join(ROOT, "results"))
DATA = os.path.abspath(os.path.join(ROOT, "data"))


def metrics(y, pred, score):
    tn, fp, fn, tp = confusion_matrix(y, pred).ravel()
    return {
        "Precision": precision_score(y, pred, zero_division=0),
        "Recall": recall_score(y, pred),
        "F1": f1_score(y, pred),
        "FPR_%": 100 * fp / (fp + tn),
        "AUC": roc_auc_score(y, score),
        "TP": tp, "FP": fp, "FN": fn, "TN": tn,
    }


def main():
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(DATA, exist_ok=True)

    df = generate(SEED)
    df.to_csv(os.path.join(DATA, "synthetic_sessions.csv"), index=False)
    print(f"Dataset: {len(df)} sessions "
          f"({(df.label == 0).sum()} legit, {(df.label == 1).sum()} replayed)\n")

    train, test = train_test_split(df, test_size=0.30, stratify=df["label"],
                                   random_state=SEED)
    print(f"Held-out test set: {len(test)} sessions, {test.label.sum()} attacks\n")

    y = test["label"].values
    model = build_detector_c(SEED).fit(train[FEATURES], train["label"])
    proba_c = model.predict_proba(test[FEATURES])[:, 1]

    preds = {
        "A: geo/IP only": (detector_a(test), test["distance_km"].values),
        "B: weighted rules": (detector_b(test), score_b(test)),
        "C: logistic regression": ((proba_c >= 0.5).astype(int), proba_c),
    }

    rows = {name: metrics(y, p, s) for name, (p, s) in preds.items()}
    res = pd.DataFrame(rows).T
    res[["TP", "FP", "FN", "TN"]] = res[["TP", "FP", "FN", "TN"]].astype(int)
    print("=== Detection results (held-out) ===")
    print(res.round(3).to_string(), "\n")
    res.round(4).to_csv(os.path.join(OUT, "detection_results.csv"))

    attacks = test[test.label == 1]
    prof_rows = {}
    for name, (p, _) in preds.items():
        p = pd.Series(p, index=test.index)
        prof_rows[name] = {
            prof: p[attacks[attacks.profile == prof].index].mean()
            for prof in ["naive", "proxy_ua", "full_emul"]
        }
    prof = pd.DataFrame(prof_rows).T
    print("=== Recall by attacker profile ===")
    print(prof.round(2).to_string(), "\n")
    prof.round(4).to_csv(os.path.join(OUT, "recall_by_profile.csv"))

    coefs = pd.Series(model[-1].coef_[0], index=FEATURES).sort_values()
    print("=== Logistic regression coefficients (raw features) ===")
    print(coefs.round(2).to_string(), "\n")
    coefs.round(4).to_csv(os.path.join(OUT, "lr_coefficients.csv"), header=["coef"])

    fig, ax = plt.subplots(figsize=(6, 5))
    for name, (_, s) in preds.items():
        fpr, tpr, _ = roc_curve(y, s)
        ax.plot(fpr, tpr, label=f"{name} (AUC={rows[name]['AUC']:.3f})")
    ax.plot([0, 1], [0, 1], "k--", lw=0.8)
    ax.set(xlabel="False positive rate", ylabel="True positive rate",
           title="ROC curves (synthetic held-out set)")
    ax.legend(loc="lower right")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "roc_curves.png"), dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 4.5))
    prof.T.plot(kind="bar", ax=ax)
    ax.set(ylabel="Recall", title="Recall by attacker profile", ylim=(0, 1.25))
    plt.setp(ax.get_xticklabels(), rotation=0)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "recall_by_profile.png"), dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6, 4))
    coefs.plot(kind="barh", ax=ax, color="steelblue")
    ax.set(title="Logistic regression coefficients", xlabel="Coefficient")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "lr_coefficients.png"), dpi=150)
    plt.close(fig)

    print(f"Saved tables and plots to: {OUT}")


if __name__ == "__main__":
    main()
    if getattr(sys, "frozen", False):       # keep the window open on double-click
        try:
            input("\nDone. Press Enter to close...")
        except EOFError:
            pass
