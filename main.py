# -*- coding: utf-8 -*-
"""صائد العروض - ملف واحد بسيط"""

import time

try:
    from curl_cffi import requests
    print("✅ curl_cffi متاح")
except ImportError:
    print("❌ ثبّت curl_cffi أول: pip install curl_cffi")
    exit()

# ============================================================
# ✏️ الكوكيز - حدّثها من Chrome
# ============================================================
CF_CLEARANCE = "CkcRnZrNvWYr5U_ibmZ5tAh14e9LjCsamT-i5ZwO0dNyHW-1sQbtMxo3tjI2ucm_yuj5je7AXtxvR1--Jp6jrj6DXxx-0sYmOrjrRRfzd2v6YoQqlCCAdy77DO22uY5m-DNkB7DbRQw14Jl2Y7Cagqi998em94v78yMTNALpfo0W38ut2Mp4zyJjWiEVswENRS0i2GFsgy3LNRC5WilSjZB90A5JBR2zIj6sdZX2b6SlYqwTLXykHUfQm9IV0Sq3u-_1cq2aBFo1uzRGyXjrQIxTEs5JRLUv6rRaUF0tJehYWA"
GID = "eyJnIjoiMjE3ZjIzZDc5N2Y2Mjc2NSJ9.au4ilQ.LygSlT27ujoQpI-KWHKWzrj9K28"

# ============================================================
# الإعدادات
# ============================================================
BASE_URL = "https://deals.3rrood.com"
MIN_DROP = 5      # أقل نسبة خصم مقبولة
TOP_N = 10        # كم عرض تعرض

COOKIES = {'cf_clearance': CF_CLEARANCE, 'gid': GID}

HEADERS = {
    'x-app': '1',
    'accept': '*/*',
    'accept-language': 'ar-EG,ar;q=0.9,en;q=0.8',
    'referer': f'{BASE_URL}/live',
    'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
}


# ============================================================
# الجلب
# ============================================================
def fetch(url, params=None):
    try:
        r = requests.get(
            url,
            headers=HEADERS,
            cookies=COOKIES,
            params=params,
            impersonate="chrome120",
            timeout=30,
        )
        print(f"   {url.split('/')[-1]} → {r.status_code}")
        if r.status_code == 200:
            return r.json()
        if r.status_code == 403:
            print("   ❌ 403 - الكوكيز انتهت. جددها من Chrome.")
        return None
    except Exception as e:
        print(f"   ❌ {e}")
        return None


# ============================================================
# التقييم
# ============================================================
def score(item):
    s = item.get('drop', 0) * 3
    s += item.get('off', 0) * 2
    if item.get('lowest'): s += 40
    if item.get('low90'):  s += 20
    if item.get('fake'):   s -= 50
    if item.get('out'):    s -= 200
    return round(s, 1)


def real_price(item):
    if item.get('fake'):
        return (item.get('price', 0) + item.get('was', 0)) / 2
    return item.get('was', item.get('price', 0))


# ============================================================
# العرض
# ============================================================
def show(items, title):
    print("\n" + "=" * 65)
    print(title)
    print("=" * 65)
    for i, it in enumerate(items, 1):
        rp = real_price(it)
        save = rp - it.get('price', 0)
        pct = (save / rp * 100) if rp > 0 else 0

        badges = []
        if it.get('lowest'): badges.append("🏆 أقل سعر تاريخي")
        if it.get('low90'):  badges.append("📉 90يوم")
        if it.get('off', 0) > 0: badges.append(f"🎟️{it['off']}%")

        print(f"\n{i}. {(it.get('name') or '?')[:60]}")
        print(f"   🏪 {it.get('store_name', '?')}  |  🔖 {it.get('code', '?')}")
        print(f"   💰 {it.get('price', 0):,.0f} {it.get('currency','EGP')}  "
              f"(كان {it.get('was', 0):,.0f})")
        print(f"   💸 توفير {save:,.0f} ({pct:.0f}%)  |  drop {it.get('drop',0)}%")
        if badges:
            print(f"   {' | '.join(badges)}")
        print(f"   🔗 {BASE_URL}/{it.get('code','')}")


# ============================================================
# MAIN
# ============================================================
def main():
    print("\n🚀 صائد العروض - بداية\n")

    # 1) جلب العروض الحية
    print("📡 بجلب /api/live ...")
    data = fetch(f"{BASE_URL}/api/live")
    if not data:
        print("\n❌ فشل الجلب. تحقق من الكوكيز.")
        return

    items = data.get('items', [])
    stores = data.get('stores', [])
    print(f"\n✅ استلمت {len(items)} عرض من {len(stores)} متجر")

    # 2) إحصائيات المتاجر
    if stores:
        print("\n🏪 عدد العروض لكل متجر:")
        for s in sorted(stores, key=lambda x: x['n'], reverse=True)[:10]:
            print(f"   • {s['name']:<20} {s['n']:>5}")

    # 3) فلترة
    hot = [
        i for i in items
        if not i.get('out')
        and not i.get('fake')
        and i.get('drop', 0) >= MIN_DROP
    ]
    hot.sort(key=score, reverse=True)
    print(f"\n🔥 لقيت {len(hot)} عرض جامد (drop ≥ {MIN_DROP}%، بدون fake/out)")

    # 4) عرض أفضل العروض
    if hot:
        show(hot[:TOP_N], f"أفضل {min(len(hot), TOP_N)} عروض")
    else:
        print("مفيش عروض تستاهل النهاردة 😅")


if __name__ == "__main__":
    main()
