# Seattle Salt Pilot

**Full-spectrum salt perception analysis** using Google Places API.

> **17 salt-related comments** from 100 Seattle restaurants  
> **Too salty**: 5 | **Not salty enough**: 3 | **Just right**: 9

---

## Result
| Type | Count | % |
|------|-------|---|
| Too salty | 5 | 29% |
| Not salty enough | 3 | 18% |
| Just right | 9 | 53% |

**Rate**: 1.7% of ~1,000 reviews mention salt.

---

## Files
- `seattle_salt_full_spectrum.py` – Main script  
- `seattle_salt_full_spectrum.xlsx` – 17 comments (Excel)  
- `README.md` – This file

---

## How to Run

### 1. Get Your **Free** Google Places API Key
1. Go to [cloud.google.com](https://cloud.google.com)  
2. Create a project → Enable **Places API**  
3. Copy your **API key**  
→ Free $200 credit/month (enough for 40,000+ requests)

### 2. Set Up
```bash
# Clone repo
git clone https://github.com/xuanchen826/seattle-salt-pilot.git
cd seattle-salt-pilot

# Install dependencies
pip install requests pandas tqdm
