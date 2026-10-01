import json, os, urllib.request, urllib.error
from datetime import datetime, timezone
from pathlib import Path

TOKEN = os.environ.get("GITHUB_TOKEN", "")
USER = os.environ.get("GITHUB_USERNAME", "AdityaPatra-dev")

def api(path):
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "profile-telemetry",
    }
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    req = urllib.request.Request(f"https://api.github.com{path}", headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.load(r)
    except Exception as e:
        print(f"Warning: API call to {path} failed: {e}")
        return None

user_data = api(f"/users/{USER}")
repos_data = api(f"/users/{USER}/repos?per_page=100&sort=updated")

# Baseline fallback values if unauthenticated rate limit is reached
public_repos = user_data.get("public_repos", 10) if user_data else 10
followers = user_data.get("followers", 7) if user_data else 7
following = user_data.get("following", 23) if user_data else 23

if repos_data and isinstance(repos_data, list):
    stars = sum(r.get("stargazers_count", 0) for r in repos_data)
    forks = sum(r.get("forks_count", 0) for r in repos_data)
    langs = {}
    for r in repos_data:
        lang = r.get("language")
        if lang:
            langs[lang] = langs.get(lang, 0) + 1
    top_lang = max(langs, key=langs.get) if langs else "Python"
else:
    stars = 2
    forks = 0
    top_lang = "Python"

updated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

def esc(x):
    return str(x).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

cards = [
    ("PUBLIC REPOS", str(public_repos), "#22d3ee", "Active Projects"),
    ("COMMUNITY", f"{followers} Followers", "#a78bfa", f"{following} Following"),
    ("STARGAZERS", f"{stars} Stars", "#fbbf24", f"{forks} Forks"),
    ("CORE STACK", esc(top_lang), "#34d399", "Cloud & MLOps"),
]

svg = [
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 320">',
    '  <defs>',
    '    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">',
    '      <stop offset="0%" stop-color="#080d1a"/>',
    '      <stop offset="50%" stop-color="#0b1329"/>',
    '      <stop offset="100%" stop-color="#111827"/>',
    '    </linearGradient>',
    '    <linearGradient id="cardGrad" x1="0%" y1="0%" x2="100%" y2="100%">',
    '      <stop offset="0%" stop-color="#0f172a" stop-opacity="0.9"/>',
    '      <stop offset="100%" stop-color="#1e293b" stop-opacity="0.7"/>',
    '    </linearGradient>',
    '    <filter id="glow">',
    '      <feGaussianBlur stdDeviation="3" result="coloredBlur"/>',
    '      <feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge>',
    '    </filter>',
    '  </defs>',
    '  <!-- Background -->',
    '  <rect width="1200" height="320" rx="22" fill="url(#bg)" stroke="#1e293b" stroke-width="1.5"/>',
    '  ',
    '  <!-- Top Bar -->',
    '  <g font-family="JetBrains Mono, monospace">',
    '    <circle cx="36" cy="38" r="5" fill="#ef4444"/>',
    '    <circle cx="54" cy="38" r="5" fill="#f59e0b"/>',
    '    <circle cx="72" cy="38" r="5" fill="#10b981"/>',
    '    <text x="96" y="43" fill="#22d3ee" font-size="15" font-weight="700" letter-spacing="1">ADITYA-TELEMETRY-ENGINE // NODE: CLOUD-LAB</text>',
    '    ',
    '    <!-- Live Pulse -->',
    '    <g transform="translate(940, 26)">',
    '      <rect width="220" height="26" rx="13" fill="#064e3b" stroke="#059669" stroke-width="1"/>',
    '      <circle cx="16" cy="13" r="5" fill="#34d399">',
    '        <animate attributeName="opacity" values="1;0.3;1" dur="2s" repeatCount="indefinite"/>',
    '      </circle>',
    '      <text x="30" y="17" fill="#6ee7b7" font-size="11" font-weight="600">ALL SYSTEMS ONLINE</text>',
    '    </g>',
    '  </g>',
    '  ',
    '  <!-- Metric Cards -->',
]

x = 35
for title, val, color, sub in cards:
    svg.append(f'  <g transform="translate({x}, 75)">')
    svg.append(f'    <rect width="265" height="135" rx="14" fill="url(#cardGrad)" stroke="#334155" stroke-width="1"/>')
    svg.append(f'    <rect x="0" y="0" width="265" height="3" fill="{color}" rx="1"/>')
    svg.append(f'    <text x="20" y="32" fill="#94a3b8" font-family="JetBrains Mono, monospace" font-size="12" font-weight="600" letter-spacing="0.5">{title}</text>')
    svg.append(f'    <text x="20" y="78" fill="{color}" font-family="JetBrains Mono, monospace" font-size="28" font-weight="800">{val}</text>')
    svg.append(f'    <text x="20" y="112" fill="#64748b" font-family="JetBrains Mono, monospace" font-size="12">{sub}</text>')
    svg.append(f'  </g>')
    x += 288

svg.extend([
    '  <!-- Footer Telemetry Status Bar -->',
    '  <g transform="translate(35, 235)" font-family="JetBrains Mono, monospace">',
    '    <rect width="1130" height="60" rx="10" fill="#090d16" stroke="#1e293b" stroke-width="1"/>',
    '    <text x="20" y="27" fill="#94a3b8" font-size="12">',
    f'      <tspan fill="#22d3ee">▸ Pipeline:</tspan> Automated GitHub CI/CD &nbsp;|&nbsp; ',
    f'      <tspan fill="#a78bfa">Primary Lang:</tspan> {esc(top_lang)} &nbsp;|&nbsp; ',
    f'      <tspan fill="#34d399">Portfolio:</tspan> adityapatradev.web.app',
    '    </text>',
    '    <text x="20" y="47" fill="#64748b" font-size="11">',
    f'      Last synchronized: {updated} (UTC) • Host: GitHub Actions runner',
    '    </text>',
    '    <g transform="translate(1085, 24)">',
    '      <circle cx="8" cy="8" r="4" fill="#22d3ee">',
    '        <animate attributeName="r" values="3;6;3" dur="2s" repeatCount="indefinite"/>',
    '        <animate attributeName="opacity" values="0.8;0.2;0.8" dur="2s" repeatCount="indefinite"/>',
    '      </circle>',
    '    </g>',
    '  </g>',
    '</svg>'
])

Path("assets/telemetry.svg").write_text("\n".join(svg), encoding="utf-8")
print(f"Generated telemetry.svg successfully for {USER}: Repos={public_repos}, Followers={followers}, Stars={stars}, TopLang={top_lang}")
