import requests, re, pandas as pd, time, json, os
from tqdm import tqdm

API_KEY = 'use yours'
TOTAL_RESTAURANTS = 150
OUTPUT_XLSX = 'seattle_salt_full_spectrum.xlsx'
OUTPUT_JSON = 'seattle_salt_full_spectrum_progress.json'

REGIONS = [
    "Downtown Seattle", "Capitol Hill Seattle", "Ballard Seattle",
    "Fremont Seattle", "University District Seattle"
]

SALT_KEYWORDS = {
    "too_salty": r'\b(too\s+salty|oversalted|way\s+too\s+salty|salty\s+as|salt\s+bomb|too\s+much\s+salt)\b',
    "not_salty": r'\b(not\s+salty|not\s+enough\s+salt|lack\s+salt|needs?\s+more\s+salt|bland|no\s+salt)\b',
    "just_right": r'\b(perfectly\s+salted|just\s+right|well\s+seasoned|good\s+salt|balanced\s+salt|nice\s+salty|umami)\b'
}

def search_restaurants(region):
    url = 'https://places.googleapis.com/v1/places:searchText'
    headers = {
        'Content-Type': 'application/json',
        'X-Goog-Api-Key': API_KEY,
        'X-Goog-FieldMask': 'places.id,places.displayName'
    }
    data = {'textQuery': f"restaurants in {region}", 'maxResultCount': 20}
    places = []
    seen = set()
    try:
        resp = requests.post(url, headers=headers, json=data).json()
        for p in resp.get('places', []):
            pid = p['id']
            if pid not in seen and len(places) < 30:
                seen.add(pid)
                places.append({**p, 'region': region})
        print(f"  {region}: +{len(places)} 家")
    except Exception as e:
        print(f"  {region} 搜索失败: {e}")
    return places

def get_all_reviews(place_id):
    url = f"https://places.googleapis.com/v1/places/{place_id}"
    headers = {'X-Goog-Api-Key': API_KEY, 'X-Goog-FieldMask': 'reviews'}
    try:
        r = requests.get(url, headers=headers, timeout=10).json()
        return r.get('reviews', [])[:10]
    except Exception as e:
        print(f"  获取评论失败 {place_id}: {e}")
        return []

all_places = []
print("开始搜索餐厅...")
for region in REGIONS:
    all_places.extend(search_restaurants(region))
    if len(all_places) >= TOTAL_RESTAURANTS:
        break
all_places = all_places[:TOTAL_RESTAURANTS]

print(f"\n开始抓取 {len(all_places)} 家餐厅的评论（全星级）...")

salt_comments = []
processed = set()
if os.path.exists(OUTPUT_JSON):
    try:
        with open(OUTPUT_JSON, 'r', encoding='utf-8') as f:
            data = json.load(f)
            salt_comments = data.get('comments', [])
            processed = set(data.get('processed', []))
        print(f"恢复进度：已处理 {len(processed)} 家，已找到 {len(salt_comments)} 条")
    except:
        pass

for place in tqdm(all_places, desc="处理"):
    pid = place['id']
    if pid in processed:
        continue
    name = place['displayName']['text']
    region = place['region']
    reviews = get_all_reviews(pid)
    for r in reviews:
        txt = r.get('text', {}).get('text', '').lower()
        star = r.get('rating', 'N/A')
        matched = False
        for typ, pattern in SALT_KEYWORDS.items():
            if re.search(pattern, txt, re.IGNORECASE):
                salt_comments.append({
                    '区域': region,
                    '餐厅': name,
                    '星级': star,
                    '评论': r['text']['text'],
                    '盐味类型': 
                        '太咸' if typ == 'too_salty' else 
                        '不够咸' if typ == 'not_salty' else 
                        '正好'
                })
                matched = True
                break
    if matched:
        print(f"  → {name} ({region}): 找到盐味评论")

    processed.add(pid)
    if len(processed) % 10 == 0:
        with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
            json.dump({'comments': salt_comments, 'processed': list(processed)}, f, ensure_ascii=False, indent=2)

df = pd.DataFrame(salt_comments)
df.to_excel(OUTPUT_XLSX, index=False)
print(f"\n完成！共找到 {len(df)} 条盐味评价 → {OUTPUT_XLSX}")
if len(df) > 0:
    print("分布：")
    print(df['盐味类型'].value_counts().to_string())
else:
    print("未找到盐味评价")
