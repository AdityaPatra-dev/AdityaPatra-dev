import json, os, urllib.request, urllib.error
from datetime import datetime, timezone
from pathlib import Path

TOKEN = os.environ.get("GITHUB_TOKEN", "")
USER = os.environ.get("GITHUB_USERNAME", "AdityaPatra-dev")
DOCKER_USER = "adityapatra"
HF_USER = "Aditya9438"

def api(url, auth=True):
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "profile-telemetry",
    }
    if auth and TOKEN and not TOKEN.startswith("ghs_"):
        headers["Authorization"] = f"Bearer {TOKEN}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=12) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        if e.code == 403 and auth and TOKEN:
            # GitHub Actions installation tokens return 403 on user endpoints; retry unauthenticated
            return api(url, auth=False)
        return None
    except Exception:
        return None

# 1. Fetch GitHub User & Repos
user_data = api(f"https://api.github.com/users/{USER}")
repos_data = api(f"https://api.github.com/users/{USER}/repos?per_page=100&sort=updated")

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

# 2. Fetch Docker Hub Repositories
docker_count = 1
try:
    d_req = urllib.request.Request(f"https://hub.docker.com/v2/repositories/{DOCKER_USER}/", headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(d_req, timeout=8) as r:
        d_data = json.load(r)
        docker_count = d_data.get("count", 1)
except Exception:
    docker_count = 1

updated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

def esc(x):
    return str(x).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

cards = [
    ("GITHUB REPOSITORIES", f"{public_repos} Repos", "#22d3ee", f"{stars} Stars • {followers} Followers"),
    ("DOCKER CONTAINER HUB", f"{docker_count} Repo(s)", "#38bdf8", f"hub.docker.com/u/{DOCKER_USER}"),
    ("HUGGING FACE HUB", "Aditya9438", "#fbbf24", "ML Models &amp; Datasets"),
    ("CLOUD DEPLOYMENTS", "3 Active Apps", "#34d399", "Portfolio • CloudArena • Taarak"),
]

svg = [
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 350" width="100%" height="auto">',
    '  <defs>',
    '    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">',
    '      <stop offset="0%" stop-color="#070a13"/>',
    '      <stop offset="50%" stop-color="#0b1329"/>',
    '      <stop offset="100%" stop-color="#111827"/>',
    '    </linearGradient>',
    '    <linearGradient id="cardGrad" x1="0%" y1="0%" x2="100%" y2="100%">',
    '      <stop offset="0%" stop-color="#0f172a" stop-opacity="0.95"/>',
    '      <stop offset="100%" stop-color="#1e293b" stop-opacity="0.8"/>',
    '    </linearGradient>',
    '  </defs>',
    '  <!-- Background -->',
    '  <rect width="1200" height="350" rx="22" fill="url(#bg)" stroke="#1e293b" stroke-width="1.5"/>',
    '  ',
    '  <!-- Window Header -->',
    '  <g font-family="JetBrains Mono, monospace">',
    '    <circle cx="36" cy="38" r="5" fill="#ef4444"/>',
    '    <circle cx="54" cy="38" r="5" fill="#f59e0b"/>',
    '    <circle cx="72" cy="38" r="5" fill="#10b981"/>',
    '    <text x="96" y="43" fill="#22d3ee" font-size="15" font-weight="700" letter-spacing="1">ADITYA-TELEMETRY-ENGINE // MULTI-CLOUD OBSERVABILITY</text>',
    '    ',
    '    <!-- Operational Pulse -->',
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
    svg.append(f'    <text x="18" y="32" fill="#94a3b8" font-family="JetBrains Mono, monospace" font-size="11" font-weight="600" letter-spacing="0.5">{title}</text>')
    svg.append(f'    <text x="18" y="78" fill="{color}" font-family="JetBrains Mono, monospace" font-size="25" font-weight="800">{esc(val)}</text>')
    svg.append(f'    <text x="18" y="112" fill="#64748b" font-family="JetBrains Mono, monospace" font-size="11">{esc(sub)}</text>')
    svg.append(f'  </g>')
    x += 288

svg.extend([
    '  <!-- Status Bar & Active Deployment Registry -->',
    '  <g transform="translate(35, 235)" font-family="JetBrains Mono, monospace">',
    '    <rect width="1130" height="85" rx="12" fill="#090d16" stroke="#1e293b" stroke-width="1"/>',
    '    <text x="20" y="28" fill="#94a3b8" font-size="12">',
    '      <tspan fill="#34d399">● Live Deployments:</tspan> ',
    '      <tspan fill="#38bdf8">gdg-cloudarena.web.app</tspan> | ',
    '      <tspan fill="#38bdf8">taakrak-d9ed0.web.app</tspan> | ',
    '      <tspan fill="#38bdf8">adityapatradev.web.app</tspan>',
    '    </text>',
    '    <text x="20" y="52" fill="#94a3b8" font-size="12">',
    '      <tspan fill="#fbbf24">● ML Flagships:</tspan> ',
    '      <tspan fill="#e2e8f0">mastering-llms (Complete)</tspan> | ',
    '      <tspan fill="#e2e8f0">Text-To-Video-Generator (Complete)</tspan> | ',
    '      <tspan fill="#a78bfa">Hugging Face: Aditya9438</tspan>',
    '    </text>',
    f'    <text x="20" y="74" fill="#64748b" font-size="11">Synchronized: {updated} (UTC) • GitHub Actions Automated Telemetry</text>',
    '    <g transform="translate(1085, 38)">',
    '      <circle cx="8" cy="8" r="4" fill="#22d3ee">',
    '        <animate attributeName="r" values="3;6;3" dur="2s" repeatCount="indefinite"/>',
    '        <animate attributeName="opacity" values="0.8;0.2;0.8" dur="2s" repeatCount="indefinite"/>',
    '      </circle>',
    '    </g>',
    '  </g>',
    '</svg>'
])

Path("assets/telemetry.svg").write_text("\n".join(svg), encoding="utf-8")
print(f"Generated telemetry.svg successfully with multi-cloud data: Repos={public_repos}, Docker={docker_count}, Deployments=3")
