# Seattle Salt Complaint Pilot

> **21 "too salty" complaints** from **150 Seattle restaurants** using **Google Places API**.

## Key Findings
- **Hit rate**: **1.4%** (vs. random ~0.25%)
- **Pattern**: 95% in **3–4 star reviews** ("delicious but too salty")
- **Hotspots**: Capitol Hill, Fremont (ramen, pho, seafood)

## Files
- `seattle_salt_ultimate.py` – Final stable script (direct `reviews[:10]` fetch)
- `seattle_salt_ultimate.xlsx` – 21 raw comments

## Reproduce
```bash
pip install requests pandas tqdm
python seattle_salt_ultimate.py
# seattle-salt-pilot
Pilot for salt-related sentiment analysis in Seattle restaurant reviews using Google Places API
