# -*- coding: utf-8 -*-
"""
فحص سريع: هل الكوكيز شغالة؟
لو الكوكيز منتهية، السكريبت هيقولك ونرجع نجيب واحدة جديدة.
"""

import sys
import requests
import json

# ============================================================
# ✏️ حدّث الكوكيز هنا من Chrome
# ============================================================
COOKIES = {
    'cf_clearance': 'CkcRnZrNvWYr5U_ibmZ5tAh14e9LjCsamT-i5ZwO0dNyHW-1sQbtMxo3tjI2ucm_yuj5je7AXtxvR1--Jp6jrj6DXxx-0sYmOrjrRRfzd2v6YoQqlCCAdy77DO22uY5m-DNkB7DbRQw14Jl2Y7Cagqi998em94v78yMTNALpfo0W38ut2Mp4zyJjWiEVswENRS0i2GFsgy3LNRC5WilSjZB90A5JBR2zIj6sdZX2b6SlYqwTLXykHUfQm9IV0Sq3u-_1cq2aBFo1uzRGyXjrQIxTEs5JRLUv6rRaUF0tJehYWA',
    'gid': 'eyJnIjoiMjE3ZjIzZDc5N2Y2Mjc2NSJ9.au4ilQ.LygSlT27ujoQpI-KWHKWzrj9K28',
}

HEADERS = {
    'authority': 'deals.3rrood.com',
    'accept': '*/*',
    'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'referer': 'https://deals.3rrood.com/store/amazon',
    'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
    'x-app': '1',
}

BASE_URL = "https://deals.3rrood.com"


def check_response(response, label=""):
    """يفحص الرد ويقولنا هل هو JSON (نجاح) أو Cloudflare (فشل)."""
    if response.status_code == 403:
        print(f"\n❌ {label}: 403 Forbidden")
        return False

    # Cloudflare challenge?
    if 'Just a moment' in response.text[:500] or 'cf_chl_opt' in response.text:
        print(f"\n🛡️  {label}: Cloudflare Challenge!")
        print("   السبب: الكوكيز منتهية أو IP مختلف.")
        return False

    # JSON?
    try:
        data = response.json()
        print(f"\n✅ {label}: نجح! رجع JSON.")
        return data
    except (json.JSONDecodeError, ValueError):
        print(f"\n⚠️  {label}: HTTP {response.status_code} لكن مش JSON.")
        print(f"   أول 100 حرف: {response.text[:100]}")
        return False


def test_live_endpoint():
    """اختبار /api/live."""
    print("\n📡 بختبر /api/live ...")
    try:
        r = requests.get(
            f'{BASE_URL}/api/live',
            headers=HEADERS,
            cookies=COOKIES,
            timeout=30,
        )
        print(f"   Status: {r.status_code}")
        return check_response(r, "/api/live")
    except Exception as e:
        print(f"   ❌ استثناء: {e}")
        return False


def test_store_endpoint(slug="amazon"):
    """اختبار /api/stores/{slug}/products."""
    print(f"\n📡 بختبر /api/stores/{slug}/products ...")
    try:
        r = requests.get(
            f'{BASE_URL}/api/stores/{slug}/products',
            headers={**HEADERS, 'referer': f'{BASE_URL}/store/{slug}'},
            cookies=COOKIES,
            params={'page': '1', 'sort': 'recent'},
            timeout=30,
        )
        print(f"   Status: {r.status_code}")
        return check_response(r, f"/api/stores/{slug}/products")
    except Exception as e:
        print(f"   ❌ استثناء: {e}")
        return False


def main():
    print("=" * 60)
    print("🔍 فحص صلاحية الكوكيز")
    print("=" * 60)

    # اختبار 1: /api/live
    live_data = test_live_endpoint()

    # اختبار 2: /api/stores/amazon/products
    store_data = test_store_endpoint("amazon")

    # -------- النتيجة --------
    print("\n" + "=" * 60)
    print("📊 النتيجة")
    print("=" * 60)

    if not live_data and not store_data:
        print("""
❌ الكوكيز منتهية أو مش شغالة.

الحل:
1. افتح Chrome في الموبايل
2. روح https://deals.3rrood.com/live
3. استنى الصفحة تحمل كاملة (30 ثانية)
4. اضغط F12 (أو استخدم Kiwi Browser)
5. Application → Cookies → deals.3rrood.com
6. انسخ cf_clearance الجديدة والصقها في الكود
7. شغّل السكريبت فورًا (في نفس دقيقة النسخ)
""")
        sys.exit(1)

    # -------- عرض النتائج --------
    if live_data:
        items = live_data.get('items', [])
        print(f"\n🔥 /api/live: {len(items)} عرض")
        for it in items[:3]:
            print(f"   • {it.get('name', '?')[:50]}")
            print(f"     💰 {it.get('price', 0):,.0f} {it.get('currency', 'EGP')}"
                  f" (كان {it.get('was', 0):,.0f})")

    if store_data:
        items = store_data if isinstance(store_data, list) else (
            store_data.get('items') or store_data.get('products') or []
        )
        print(f"\n🔥 amazon products: {len(items)} منتج")
        for it in items[:3]:
            print(f"   • {it.get('name', '?')[:50]}")
            print(f"     💰 {it.get('price', 0):,.0f} {it.get('currency', 'EGP')}")

    print("\n✅ الكوكيز شغالة!")


if __name__ == "__main__":
    main()
