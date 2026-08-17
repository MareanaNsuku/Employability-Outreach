import csv, os, time, random, json
from playwright.sync_api import sync_playwright
from email_utils import scrape_emails

def scrape_industry(city, industry_key, keywords):
    all_places = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        # 1. Collect place URLs from Maps search
        for kw in keywords:
            query = f"{kw} in {city}"
            print(f"🔍 {query}")
            url = f"https://www.google.com/maps/search/{query.replace(' ', '+')}"
            page.goto(url, timeout=30000, wait_until='domcontentloaded')
            page.wait_for_timeout(5000)
            for _ in range(4):
                page.keyboard.press("PageDown")
                time.sleep(1.5)
            links = page.locator("a[href^='https://www.google.com/maps/place/']")
            for i in range(min(links.count(), 10)):
                try:
                    link = links.nth(i)
                    href = link.get_attribute("href")
                    if not href or '/place/' not in href:
                        continue
                    aria_label = link.get_attribute("aria-label")
                    name = aria_label if aria_label else "Unknown"
                    if href not in all_places:
                        all_places[href] = name
                        print(f"   ✅ {name}")
                except:
                    continue
            time.sleep(random.uniform(1,2))

        # 2. Visit each place to extract website
        companies = []
        for place_url, name in all_places.items():
            try:
                page.goto(place_url, timeout=15000, wait_until='domcontentloaded')
                page.wait_for_timeout(3000)
                website = ""
                website_btn = page.locator("a[aria-label*='Website']")
                if website_btn.count() > 0:
                    website = website_btn.first.get_attribute("href") or ""
                if not website:
                    external = page.locator("a[href^='http']:not([href*='google'])")
                    if external.count() > 0:
                        website = external.first.get_attribute("href") or ""
                if website and 'google.com' not in website:
                    companies.append({
                        'company_name': name,
                        'contact_name': '',
                        'email': '',
                        'industry': industry_key,
                        'tier': 1,
                        'city': city,
                        'phone': '',
                        'website': website
                    })
                    print(f"   🌐 {name} → {website}")
                else:
                    print(f"   ⚠️  {name} – no website found")
            except:
                pass
            time.sleep(1)
        browser.close()

    # Remove duplicates by website
    seen = set()
    unique = []
    for c in companies:
        if c['website'] not in seen:
            seen.add(c['website'])
            unique.append(c)

    out_dir = os.path.join('industry_data', industry_key)
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, f'{industry_key}_gmaps.csv')
    if unique:
        with open(out_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=unique[0].keys())
            writer.writeheader()
            for row in unique:
                row['email'] = scrape_emails(row.get('website',''))
            writer.writerows(unique)
        print(f"\n✅ Saved {len(unique)} {industry_key} companies to {out_file}")
    else:
        print("❌ No companies found.")

if __name__ == '__main__':
    import sys
    industry_key = os.path.basename(__file__).replace('_bot.py', '')
    with open('industries.json', 'r') as f:
        industries = json.load(f)
    keywords = industries.get(industry_key, {}).get('keywords', [])
    if not keywords:
        print(f"❌ No keywords for {industry_key}")
        sys.exit(1)
    city = sys.argv[1] if len(sys.argv) > 1 else 'Cape Town'
    scrape_industry(city, industry_key, keywords)
