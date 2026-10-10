# Infostealer-Driven Session Hijacking and MFA Bypass Detection

**Case study: Genesis Market takedown (Operation Cookie Monster, 2023)**

Group 36 | Cyber Security, Theory CA-2 (Part 2) | Symbiosis Institute of Technology, Pune

| Member | PRN |
|---|---|
| Utsav Raj Singh | 23070122256 |
| Sourav Singh | 23070122257 |
| Sumit Pathak | 23070122255 |

Guide: Dr. Pooja Bagane

**GitHub link:** https://github.com/YOUR-USERNAME/YOUR-REPO-NAME   <!-- replace with your link -->

---

## 1. What this project does
Infostealer malware can copy a victim's session cookies, so an attacker can
replay the session and inherit an already-completed MFA check. This project
implements the **detection experiment** from the report:

- generates a **synthetic** log dataset of **20,400 sessions**
  (20,000 legitimate + 400 replayed-cookie sessions, 2% base rate)
- models three attacker profiles: *naive*, *proxy + user-agent*, *full emulation*
- computes **8 features** per session: ASN change, geographic distance,
  user-agent match, fingerprint match, concurrent use, session age,
  sensitive action, fresh-MFA event
- compares three detectors on a stratified 70/30 split (6,120 held-out sessions, 120 attacks):
  - **A** - geo/IP-only rule (distance > 500 km)
  - **B** - hand-weighted multi-signal rule (threshold 6)
  - **C** - class-weighted logistic regression
- reports Precision, Recall, F1, FPR, ROC AUC, recall per attacker profile,
  and ROC / bar-chart figures

> **Ethics:** no real credentials, malware, marketplace content or victim data is
> used. All attacker probabilities are assumptions of the study.

## 2. Project structure
```
.
├── README.md
├── requirements.txt
├── run.bat                 # Windows: install + run
├── build_exe.bat           # Windows: build standalone .exe
├── src/
│   ├── generate_dataset.py # synthetic session generator
│   ├── detectors.py        # detectors A, B, C
│   └── evaluate.py         # full pipeline (main entry point)
├── data/synthetic_sessions.csv
├── results/                # tables (.csv), figures (.png), console_output.txt
└── report/G_36_Report.docx
```

## 3. How to execute

**Requirements:** Python 3.10+ (tested with scikit-learn 1.8.0)

```bash
# 1. get the code
git clone https://github.com/Utsav99552/infostealer-session-hijacking-detection
cd infostealer-session-hijacking-detection

# 2. (optional) virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux / macOS

# 3. install dependencies
pip install -r requirements.txt

# 4. run the whole experiment
python src/evaluate.py
```

On Windows you can simply double-click **`run.bat`**.

To generate only the dataset: `python src/generate_dataset.py`

### Executable (.exe)
Double-click `build_exe.bat` (needs Python + internet once) to build
`dist\G36_Detection.exe`, or use the pre-built exe if it is included in the submission zip.
The exe runs the same pipeline and writes results next to it.

## 4. Output
Running the program prints metrics and saves to `results/`:

| File | Content |
|---|---|
| `detection_results.csv` | Precision, Recall, F1, FPR, AUC, confusion counts |
| `recall_by_profile.csv` | Recall for naive / proxy+UA / full-emulation attackers |
| `lr_coefficients.csv` | Logistic regression coefficients |
| `roc_curves.png` | ROC curves of the 3 detectors |
| `recall_by_profile.png` | Recall by attacker profile |
| `lr_coefficients.png` | Feature coefficients |

Results are reproducible (fixed random seed = 42).

## 5. Key findings
- Geo/IP-only detection (A) is weak: it collapses against attackers who proxy
  into the victim's region.
- Multi-signal rules (B) are very precise but miss fully emulated attackers.
- Logistic regression (C) catches nearly all attacks, because the
  **fresh-MFA event** feature dominates: a replayed session never completed MFA itself.
- Conclusion: MFA must be paired with session-bound credentials, short token
  lifetimes, endpoint hygiene and cross-signal session monitoring.

## 6. Limitations
Synthetic data; assumptions about attacker behaviour; real systems with
"remember this device" and long-lived refresh tokens will show less separation.
Results show the *relative* value of signals, not production accuracy.
