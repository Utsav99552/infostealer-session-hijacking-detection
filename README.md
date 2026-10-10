# infostealer-session-hijacking-detection
# Infostealer-Driven Session Hijacking & MFA Bypass Detection
Group 36 | Cyber Security CA-2 | SIT Pune
Members: Utsav Raj Singh, Sourav Singh, Sumit Pathak
Guide: Dr. Pooja Bagane

## About
Synthetic-log simulation (20,400 sessions) comparing three detectors for
replayed stolen sessions: geo/IP rule, weighted multi-signal rule,
and logistic regression. Based on the Genesis Market takedown case study.
No real victim data or malware is used.

## Requirements
- Python 3.10+
- Install: `pip install -r requirements.txt`

## How to Run
1. Clone: `git clone https://github.com/YOUR-USERNAME/YOUR-REPO.git`
2. `cd YOUR-REPO`
3. Generate data: `python src/generate_dataset.py`
4. Run detectors and evaluation: `python src/evaluate.py`
5. Results (F1, precision, recall, plots) are saved in `results/`.

## Results
| Detector | Precision | Recall | F1 |
|---|---|---|---|
| Geo/IP rule | ... | ... | 0.49 |
| Weighted multi-signal | 0.97 | ... | 0.77 |
| Logistic regression | ... | 0.98 | ... |

## Executable (optional)
Windows .exe is in `dist/`, built with PyInstaller.

## GitHub Link
https://github.com/YOUR-USERNAME/YOUR-REPO
