import os
import re

entry_file = r"C:\Users\т\.gemini\antigravity\scratch\rolls-game\public\_nuxt\ZEhFy-gV.js"

with open(entry_file, "r", encoding="utf-8") as f:
    text = f.read()

# Look for dynamic import statements or chunk filenames
# Typically in Nuxt/Vite: () => import("./something.js") or { [key]: () => import("./...") }
chunks = set(re.findall(r'["\']([a-zA-Z0-9_\-]{8,}\.js)["\']', text))
print("Found potential JS chunk names:", len(chunks))

nuxt_paths = set(re.findall(r'/_nuxt/[a-zA-Z0-9_\-\.]+', text))
print("Nuxt paths in JS:", len(nuxt_paths))

# Search for routes or page names
routes = re.findall(r'name:["\']([^"\']+)["\'],path:["\']([^"\']+)["\']', text)
print("Routes:", len(routes), routes[:10])

# Search for API endpoints
apis = set(re.findall(r'https?://[a-zA-Z0-9_\-\.:]+(?:/[a-zA-Z0-9_\-\./\?=&%]+)?', text))
print("\nAPIs and External URLs found:", len(apis))
for api in sorted(apis):
    if "telegram" not in api and "w3.org" not in api:
        print("  -", api)
