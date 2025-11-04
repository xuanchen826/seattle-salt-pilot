import requests, re, pandas as pd, time, json, os
from tqdm import tqdm

API_KEY = 'AIzaSyCOEY-55qp1SArORJkXaE_l9SYLnpyubCw'
PER_REGION = 30
OUTPUT_XLSX = 'seattle_salt_ultimate.xlsx'
OUTPUT_JSON = 'seattle_salt_ultimate_progress.json'

REGIONS = [
    "Downtown Seattle", "Ballard Seattle", "Capitol Hill Seattle",
    "Fremont Seattle", "University District Seattle"
]

SALT_PATTERN = r'\b(salt|salty|sodium|too\s+salty|high\s+sodium|salty\s+broth|oversalted|salty\s+flavor|too\s+much\s+salt|salty\s+taste|high\s+salt|salty\s+food|briny|saline)\b'

def search_places(region):
    queries = [
        f"restaurants in {region}",
        f"ramen in {region}",
        f"pho in {region}",
        f"seafood in {region}"
    ]
    places = []
    seen = set()
    for q in queries:
        if len(places) >= PER_REGION: break
        url = 'https://places.googleapis.com/v1/places:searchText'
        headers = {
            'Content-Type': 'application/json',
            'X-Goog-Api-Key': API_KEY,
            'X-Goog-FieldMask': 'places.id,places.displayName'
        }
        data = {'textQuery': q, 'maxResultCount': 20}
        try:
            resp = requests.post(url, headers=headers, json=data).json()
            for p in resp.get('places', []):
                pid = p['id']
                if pid not in seen and len(places) < PER_REGION:
                    seen.add(pid)
                    places.append({**p, 'region': region})
            print(f"  {q}: +{len(resp.get('places', []))} 家 → 累计 {len(places)}")
        except: pass
    return places

# 关键修复：直接抓 10 条评论
def get_10_reviews_direct(place_id):
    url = f"https://places.googleapis.com/v1/places/{place_id}"
    headers = {'X-Goog-Api-Key': API_KEY, 'X-Goog-FieldMask': 'reviews'}
    try:
        r = requests.get(url, headers=headers, timeout=10).json()
        return r.get('reviews', [])[:10]  # 直接返回前 10 条
    except: return []

# 主程序
all_places = []
print("开始搜索（每区 30 家）...")
for region in REGIONS:
    print(f"\n正在搜索: {region}")
    region_places = search_places(region)
    all_places.extend(region_places)
    print(f"  {region} 完成 → 累计 {len(all_places)} 家")

print(f"\n成功获取 {len(all_places)} 家餐厅，开始抓 ≤4 星评论...\n")

salty_comments = []
processed = set()
if os.path.exists(OUTPUT_JSON):
    try:
        with open(OUTPUT_JSON, 'r') as f:
            data = json.load(f)
            salty_comments = data.get('comments', [])
            processed = set(data.get('processed', []))
        print(f"恢复进度：已处理 {len(processed)} 家，已找到 {len(salty_comments)} 条")
    except: pass

for place in tqdm(all_places, desc="处理"):
    pid = place['id']
    if pid in processed: continue
    name = place['displayName']['text']
    region = place['region']
    reviews = get_10_reviews_direct(pid)
    found = 0
    for r in reviews:
        txt = r.get('text', {}).get('text', '').lower()
        star = r.get('rating', 5)
        if star <= 4 and re.search(SALT_PATTERN, txt, re.IGNORECASE):
            salty_comments.append({
                '区域': region,
                '餐厅': name,
                '星级': star,
                '评论': r['text']['text']
            })
            found += 1
    if found > 0:
        print(f"  → {name} ({region}): 找到 {found} 条")

    processed.add(pid)
    if len(processed) % 10 == 0:
        with open(OUTPUT_JSON, 'w') as f:
            json.dump({'comments': salty_comments, 'processed': list(processed)}, f, ensure_ascii=False, indent=2)

df = pd.DataFrame(salty_comments)
df.to_excel(OUTPUT_XLSX, index=False)
print(f"\n完成！找到 {len(df)} 条 → {OUTPUT_XLSX}")
