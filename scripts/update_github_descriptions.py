#!/usr/bin/env python3
"""
update_github_descriptions.py

Updates the GitHub repository descriptions, homepages, and topics for all 
repositories under the AdityaPatra-dev account using the GitHub REST API.

Usage:
  python3 scripts/update_github_descriptions.py --dry-run
  python3 scripts/update_github_descriptions.py --token <YOUR_GITHUB_PAT>
  GITHUB_TOKEN="<YOUR_TOKEN>" python3 scripts/update_github_descriptions.py
"""

import os
import sys
import json
import argparse
import urllib.request
import urllib.error

OWNER = "AdityaPatra-dev"

REPOSITORIES = {
    "CloudArena": {
        "description": "🌩️ AI-powered Cloud Infrastructure Survival Arena & SRE Chaos Simulator featuring local Kubernetes clusters and Google Gemini AI incident mentorship.",
        "homepage": "https://gdg-cloudarena.web.app",
        "topics": ["kubernetes", "chaos-engineering", "sre", "gemini-ai", "docker", "k3d", "python", "ctf"]
    },
    "DeployHub": {
        "description": "☁️ Automated self-service application deployment platform inspired by Render & Railway for containerizing and deploying GitHub repos to Kubernetes.",
        "homepage": "https://github.com/AdityaPatra-dev/DeployHub",
        "topics": ["devops", "kubernetes", "docker", "ci-cd", "paas", "deployment-automation", "cloud-native"]
    },
    "portfolio": {
        "description": "🌐 Modern, responsive developer portfolio web application built with React, TypeScript, and Tailwind CSS, deployed on Firebase Hosting.",
        "homepage": "https://adityapatradev.web.app",
        "topics": ["portfolio", "react", "typescript", "tailwindcss", "firebase", "frontend", "developer-portfolio"]
    },
    "mastering-llms": {
        "description": "🧠 Curated, prioritized knowledge base covering Large Language Model fundamentals, transformer architecture, fine-tuning, and RAG systems.",
        "homepage": "https://github.com/AdityaPatra-dev/mastering-llms",
        "topics": ["machine-learning", "llm", "transformers", "pytorch", "fine-tuning", "rag", "deep-learning"]
    },
    "Taarak": {
        "description": "📱 Offline-first disaster preparedness & emergency response platform built with Flutter and Firebase for Smart India Hackathon (SIH26191).",
        "homepage": "https://taakrak-d9ed0.web.app",
        "topics": ["flutter", "dart", "firebase", "disaster-management", "offline-first", "mobile-app", "sih"]
    },
    "Text-To-Video-Generator": {
        "description": "🎬 Generative AI pipeline in Python translating PDF documents into narrated video presentations with OpenAI GPT-3.5, TTS, and OpenCV.",
        "homepage": "https://github.com/AdityaPatra-dev/Text-To-Video-Generator",
        "topics": ["python", "generative-ai", "openai", "text-to-speech", "opencv", "video-generation", "nlp"]
    },
    "beat_wave": {
        "description": "🎵 DevOps-ready full-stack music streaming web application built with Node.js, Express, and PostgreSQL for Docker & Kubernetes showcase.",
        "homepage": "https://github.com/AdityaPatra-dev/beat_wave",
        "topics": ["nodejs", "express", "postgresql", "docker", "kubernetes", "devops", "fullstack", "microservices"]
    },
    "Web-Scrapper-Wikipedia": {
        "description": "🔍 Interactive Python CLI web scraper extracting structured infobox key-value data, suggestions, and introductory summaries from Wikipedia articles.",
        "homepage": "https://github.com/AdityaPatra-dev/Web-Scrapper-Wikipedia",
        "topics": ["python", "web-scraping", "beautifulsoup4", "cli", "wikipedia-api", "data-extraction"]
    },
    "Youtube_Download": {
        "description": "⚡ High-performance automated YouTube playlist downloader script leveraging PowerShell, yt-dlp, and ffmpeg for parallel media extraction.",
        "homepage": "https://github.com/AdityaPatra-dev/Youtube_Download",
        "topics": ["powershell", "yt-dlp", "ffmpeg", "downloader", "automation", "video-processing"]
    },
    "AdityaPatra-dev": {
        "description": "⚙️ Personal GitHub profile configuration, automated multi-cloud telemetry engine, and CI/CD pipelines showcasing cloud & DevOps engineering.",
        "homepage": "https://adityapatradev.web.app",
        "topics": ["github-profile", "github-actions", "telemetry", "svg-animations", "ci-cd", "devops"]
    }
}


def make_request(url: str, method: str, token: str, data: dict = None) -> tuple[int, str]:
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "AdityaPatra-DescUpdater"
    }
    payload = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=payload, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        return e.code, error_body


def update_repos(token: str):
    print(f"\n🚀 Updating descriptions and metadata for {len(REPOSITORIES)} repositories on GitHub...\n")
    for repo, meta in REPOSITORIES.items():
        print(f"📦 Updating {OWNER}/{repo}...")
        
        # 1. Update description & homepage
        repo_url = f"https://api.github.com/repos/{OWNER}/{repo}"
        status, resp = make_request(repo_url, "PATCH", token, {
            "description": meta["description"],
            "homepage": meta["homepage"]
        })
        if status == 200:
            print(f"   ✅ Description & Homepage updated successfully.")
        else:
            print(f"   ❌ Error updating repo ({status}): {resp}")

        # 2. Update topics
        topics_url = f"https://api.github.com/repos/{OWNER}/{repo}/topics"
        t_status, t_resp = make_request(topics_url, "PUT", token, {
            "names": meta["topics"]
        })
        if t_status == 200:
            print(f"   🏷️  Topics updated: {', '.join(meta['topics'])}")
        else:
            print(f"   ⚠️  Topics error ({t_status}): {t_resp}")
        print()

    print("🎉 All repositories processed!")


def dry_run():
    print(f"\n=======================================================")
    print(f"  TARGET REPOSITORY DESCRIPTIONS & METADATA PREVIEW")
    print(f"=======================================================\n")
    for i, (repo, meta) in enumerate(REPOSITORIES.items(), 1):
        print(f"{i}. 📁 {OWNER}/{repo}")
        print(f"   📝 Description : {meta['description']}")
        print(f"   🌐 Homepage    : {meta['homepage']}")
        print(f"   🏷️  Topics      : {', '.join(meta['topics'])}")
        print()
    print("💡 To apply these descriptions directly to GitHub, run:")
    print("   GITHUB_TOKEN=\"ghp_yourToken\" python3 scripts/update_github_descriptions.py\n")


def main():
    parser = argparse.ArgumentParser(description="Update descriptions and metadata for AdityaPatra-dev repositories.")
    parser.add_argument("--token", help="GitHub Personal Access Token (classic with repo scope, or fine-grained with read & write Metadata / Administration)")
    parser.add_argument("--dry-run", action="store_true", help="Print repository descriptions without applying")
    args = parser.parse_args()

    token = args.token or os.environ.get("GITHUB_TOKEN")

    if args.dry_run or not token:
        dry_run()
        if not token and not args.dry_run:
            print("ℹ️  No GITHUB_TOKEN provided. Ran in preview mode. Supply --token to write changes to GitHub.")
    else:
        update_repos(token)


if __name__ == "__main__":
    main()
