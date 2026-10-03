#!/usr/bin/env python3
"""
update_readme_projects.py

Automates:
1. Dynamic selection of Featured Projects:
   - Fetches repositories pinned on the user's GitHub profile.
   - Appends the latest updated repositories at the end.
   - Strictly prevents duplicates (if a latest repo is already pinned, it is skipped).
   - Renders them in a responsive side-by-side 2-column table grid.
2. Dynamic Full Repository Directory & Architecture Matrix:
   - Discovers all public non-fork repositories owned by the user.
   - Dynamically updates the total project count: "(X Projects)".
   - Formats project name, description, tech stack, and live demo / status badges.
   - Places the directory inside a clean, collapsible <details> tag.

Usage:
  python3 scripts/update_readme_projects.py
"""

import os
import re
import json
import urllib.request
import urllib.error
from pathlib import Path

USER = os.environ.get("GITHUB_USERNAME", "AdityaPatra-dev")
TOKEN = os.environ.get("GITHUB_TOKEN", "")

README_PATH = Path(__file__).resolve().parent.parent / "README.md"

KNOWN_ICONS = {
    "CloudArena": "🌩️",
    "DeployHub": "☁️",
    "portfolio": "🌐",
    "Taarak": "📱",
    "mastering-llms": "🧠",
    "Text-To-Video-Generator": "🎬",
    "beat_wave": "🎵",
    "Web-Scrapper-Wikipedia": "🔍",
    "Youtube_Download": "⚡",
    "DevPulse": "📊",
    "gemeni-smart-note": "📝",
    "AdityaPatra-dev": "⚙️",
}

KNOWN_STATUS = {
    "mastering-llms": "**Complete ✅**",
    "Text-To-Video-Generator": "**Complete ✅**",
    "Web-Scrapper-Wikipedia": "**Complete ✅**",
    "Youtube_Download": "**Complete ✅**",
    "AdityaPatra-dev": "**Automated 🔄**",
}

FALLBACK_PINNED = [
    "Taarak",
    "CloudArena",
    "Youtube_Download",
    "DeployHub",
    "DevPulse",
    "portfolio",
]


def fetch_api(url: str, auth: bool = True):
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "AdityaPatra-ReadmeAutomation",
    }
    if auth and TOKEN and not TOKEN.startswith("ghs_"):
        headers["Authorization"] = f"Bearer {TOKEN}"

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as e:
        if e.code == 403 and auth and TOKEN:
            return fetch_api(url, auth=False)
        return None
    except Exception:
        return None


def get_pinned_repos() -> list[str]:
    """Retrieves pinned repository names via GraphQL or HTML fallback."""
    # 1. Try GraphQL if valid token exists
    if TOKEN:
        graphql_url = "https://api.github.com/graphql"
        query = """
        query($login: String!) {
          user(login: $login) {
            pinnedItems(first: 10, types: REPOSITORY) {
              nodes {
                ... on Repository {
                  name
                }
              }
            }
          }
        }
        """
        data = json.dumps({"query": query, "variables": {"login": USER}}).encode("utf-8")
        headers = {
            "Authorization": f"Bearer {TOKEN}",
            "User-Agent": "AdityaPatra-ReadmeAutomation",
            "Content-Type": "application/json",
        }
        req = urllib.request.Request(graphql_url, data=data, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=10) as r:
                res = json.load(r)
                nodes = res.get("data", {}).get("user", {}).get("pinnedItems", {}).get("nodes", [])
                pinned = [n["name"] for n in nodes if n and "name" in n]
                if pinned:
                    print(f"📌 Found {len(pinned)} pinned repos via GraphQL: {pinned}")
                    return pinned
        except Exception as e:
            print(f"ℹ️  GraphQL pinned lookup skipped ({e}); falling back to profile HTML.")

    # 2. Try HTML scraping
    try:
        req = urllib.request.Request(f"https://github.com/{USER}", headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode("utf-8")
        matches = re.findall(r"href=\"/" + USER + r"/([a-zA-Z0-9_.-]+)\"[^>]*class=\"[^\"]*Link[^\"]*text-bold", html)
        pinned = []
        for m in matches:
            if m not in pinned:
                pinned.append(m)
        if pinned:
            print(f"📌 Found {len(pinned)} pinned repos via Profile HTML: {pinned}")
            return pinned
    except Exception as e:
        print(f"⚠️  HTML scrape error ({e}); using fallback pinned list.")

    return list(FALLBACK_PINNED)


def get_all_repos() -> list[dict]:
    """Fetches all non-fork repositories owned by the user, sorted by pushed_at descending."""
    url = f"https://api.github.com/users/{USER}/repos?per_page=100&sort=updated"
    repos = fetch_api(url)
    if not repos or not isinstance(repos, list):
        print("⚠️ Could not fetch repositories from GitHub API.")
        return []

    # Filter out forks
    owned_repos = [r for r in repos if not r.get("fork", False)]
    # Sort strictly by pushed_at descending
    owned_repos.sort(key=lambda x: x.get("pushed_at") or "", reverse=True)
    return owned_repos


def build_featured_table(featured_repos: list[str]) -> str:
    """Builds a responsive side-by-side 2-column HTML table for featured pinned and latest cards."""
    rows = []
    # Pair items into rows of 2
    for i in range(0, len(featured_repos), 2):
        pair = featured_repos[i : i + 2]
        r1 = pair[0]
        c1 = (
            f'    <td width="50%" align="center">\n'
            f'      <a href="https://github.com/{USER}/{r1}">'
            f'<img src="https://github-readme-stats.vercel.app/api/pin/?username={USER}&repo={r1}&theme=dark&bg_color=0D1117&title_color=22D3EE&icon_color=7C3AED&text_color=C9D1D9&description_lines=3" '
            f'width="100%" alt="{r1} repository" /></a>\n'
            f'    </td>'
        )

        if len(pair) > 1:
            r2 = pair[1]
            c2 = (
                f'    <td width="50%" align="center">\n'
                f'      <a href="https://github.com/{USER}/{r2}">'
                f'<img src="https://github-readme-stats.vercel.app/api/pin/?username={USER}&repo={r2}&theme=dark&bg_color=0D1117&title_color=22D3EE&icon_color=7C3AED&text_color=C9D1D9&description_lines=3" '
                f'width="100%" alt="{r2} repository" /></a>\n'
                f'    </td>'
            )
        else:
            c2 = '    <td width="50%" align="center"></td>'

        rows.append(f"  <tr>\n{c1}\n{c2}\n  </tr>")

    table_content = "\n".join(rows)
    return f'<table align="center" width="100%">\n{table_content}\n</table>'


def build_directory_matrix(repos: list[dict]) -> str:
    """Builds the collapsible repository matrix with dynamic project count and tech stacks."""
    lines = [
        "<details>",
        f"<summary><b>📂 View Full Repository Directory & Architecture Matrix ({len(repos)} Projects)</b></summary>",
        "",
        "<br/>",
        "",
        "| Project | Highlights & Architecture | Tech Stack | Status / Demo |",
        "| :--- | :--- | :--- | :---: |",
    ]

    for r in repos:
        name = r["name"]
        icon = KNOWN_ICONS.get(name, "📦")
        url = r.get("html_url", f"https://github.com/{USER}/{name}")
        desc = r.get("description") or f"{name} repository."

        # Clean leading emojis from description for consistency with table icon
        cleaned_desc = desc
        for emo in ["🌩️", "☁️", "🌐", "📱", "🧠", "🎬", "🎵", "🔍", "⚡", "⚙️", "📊", "📝"]:
            if cleaned_desc.startswith(emo):
                cleaned_desc = cleaned_desc[len(emo) :].strip()

        # Build Tech Stack
        lang = r.get("language")
        topics = r.get("topics", [])
        stack_items = []
        if lang:
            stack_items.append(lang)
        for t in topics:
            if t.lower() not in [name.lower(), "portfolio", "developer-portfolio", "ci-cd"] and len(stack_items) < 3:
                label = t.replace("-", " ").title() if len(t) > 4 else t.upper()
                if label not in stack_items:
                    stack_items.append(label)

        stack_str = " ".join([f"`{item}`" for item in stack_items[:3]]) if stack_items else "`Code`"

        # Status / Demo
        homepage = r.get("homepage")
        if homepage and "github.com" not in homepage:
            status = f"[**Live App**]({homepage})"
        elif name in KNOWN_STATUS:
            status = KNOWN_STATUS[name]
        else:
            status = "**Active ⚡**"

        lines.append(f"| {icon} **[{name}]({url})** | {cleaned_desc} | {stack_str} | {status} |")

    lines.append("")
    lines.append("</details>")
    return "\n".join(lines)


def update_readme():
    if not README_PATH.exists():
        print(f"❌ README file not found at {README_PATH}")
        return

    content = README_PATH.read_text(encoding="utf-8")

    # 1. Fetch pinned and all repos
    pinned_repos = get_pinned_repos()
    all_repos = get_all_repos()

    if not all_repos:
        print("⚠️ No repositories returned; aborting update to protect README.")
        return

    # 2. Select Featured: Pinned + Latest (strictly deduplicated)
    all_repo_names = [r["name"] for r in all_repos]

    # Validate pinned are valid repos
    valid_pinned = [p for p in pinned_repos if p in all_repo_names]
    if not valid_pinned:
        valid_pinned = [r["name"] for r in all_repos[:6]]

    # Find latest non-pinned repos (excluding special profile readme repo unless pinned)
    latest_candidates = [
        r["name"]
        for r in all_repos
        if r["name"] not in valid_pinned and r["name"] != USER
    ]

    # Pick latest count so that the 2-column table is completely balanced
    # If pinned count is even, add 2 latest; if odd, add 1 latest
    num_latest = 2 if len(valid_pinned) % 2 == 0 else 1
    selected_latest = latest_candidates[:num_latest]

    featured_selection = valid_pinned + selected_latest
    print(f"⭐ Featured Repositories ({len(featured_selection)} total):")
    print(f"   • Pinned ({len(valid_pinned)}): {valid_pinned}")
    print(f"   • Latest ({len(selected_latest)}): {selected_latest}")

    # 3. Generate Blocks
    featured_table = build_featured_table(featured_selection)
    directory_matrix = build_directory_matrix(all_repos)

    # 4. Replace using comment anchors if available, or regex
    p_start = "<!-- FEATURED_PROJECTS_START -->"
    p_end = "<!-- FEATURED_PROJECTS_END -->"
    d_start = "<!-- REPO_DIRECTORY_START -->"
    d_end = "<!-- REPO_DIRECTORY_END -->"

    if p_start in content and p_end in content and d_start in content and d_end in content:
        # Markers exist, clean surgical replacement
        featured_pattern = re.compile(rf"{re.escape(p_start)}.*?{re.escape(p_end)}", re.DOTALL)
        content = featured_pattern.sub(f"{p_start}\n{featured_table}\n{p_end}", content)

        dir_pattern = re.compile(rf"{re.escape(d_start)}.*?{re.escape(d_end)}", re.DOTALL)
        content = dir_pattern.sub(f"{d_start}\n{directory_matrix}\n{d_end}", content)
    else:
        # First time injection: replace between '## 🚀 Featured Projects' and '---'
        featured_header = "## 🚀 Featured Projects"
        if featured_header in content:
            pre_header, post_header = content.split(featured_header, 1)
            # Find the next '---' section separator
            parts = post_header.split("\n---", 1)
            intro = "\n\n> Pinned repositories and live production builds. Discover more on my [GitHub repositories page](https://github.com/AdityaPatra-dev?tab=repositories).\n\n"
            new_section = (
                f"{intro}"
                f"{p_start}\n{featured_table}\n{p_end}\n\n"
                f"{d_start}\n{directory_matrix}\n{d_end}\n"
            )
            content = f"{pre_header}{featured_header}{new_section}\n---{parts[1]}"

    README_PATH.write_text(content, encoding="utf-8")
    print(f"✅ Successfully updated {README_PATH}")
    print(f"   • Featured grid: {len(featured_selection)} projects in side-by-side layout")
    print(f"   • Directory matrix: {len(all_repos)} projects cataloged with complete metadata")


if __name__ == "__main__":
    update_readme()
