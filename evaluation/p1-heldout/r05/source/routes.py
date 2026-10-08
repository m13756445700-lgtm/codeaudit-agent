URLS = {"daily": "https://reports.invalid/daily", "weekly": "https://reports.invalid/weekly"}

def preview(user_choice, trusted_fetch):
    url = URLS[user_choice]
    return trusted_fetch(url, allow_redirects=False)

def dormant_fetch(raw_url, trusted_fetch):
    return trusted_fetch(raw_url)
