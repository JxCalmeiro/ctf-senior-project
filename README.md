# CTF Challenge Platform — AI Senior Project

A self-hosted Capture The Flag platform with Active Directory authentication and a locally-run AI hint bot, built for [Course Name] Senior Project.

## Architecture

- **Windows Server 2025** — Active Directory Domain Services (`ctf.local`), provides authentication
- **Ubuntu Server 24.04** — hosts the application stack via Docker Compose:
  - Flask web app (Gunicorn) — challenge platform, flag validation, leaderboard
  - MySQL 8.0 — application data (users, challenges, solves, hint logs)
  - Ollama (Llama 3.1 8B) — self-hosted AI hint bot, no external API calls or costs
  - Standalone SQLi challenge container — deliberately vulnerable login for the web category
- **GitHub** — source control with a webhook-triggered auto-deploy pipeline: pushing to `main` automatically pulls and rebuilds the running application

```Windows Server 2025 (AD DS) <--LDAP--> Ubuntu Server 24.04
192.168.151.10 192.168.151.20
├── ctf-web (Flask, :5000)
├── ctf-db (MySQL)
├── ollama (:11434)
├── sqli-challenge (:5001)
└── webhook receiver (systemd, :9000)
```


## Features

- **AD-integrated authentication** — users log in with real Active Directory credentials via LDAP bind
- **6 challenges across 3 categories** — crypto, forensics, web, easy to medium difficulty
- **AI hint bot** — self-hosted Ollama model gives conceptual nudges without leaking flags, with tiered specificity and prompt-injection resistance
- **Live leaderboard** — points update in real time as challenges are solved
- **CI/CD auto-deploy** — GitHub webhook triggers `git pull` + Docker rebuild on every push to `main`

## Setup

### Prerequisites
- VMware Workstation Pro (or equivalent)
- Windows Server 2025 evaluation ISO
- Ubuntu Server 24.04 LTS ISO

### 1. Active Directory
1. Install Windows Server 2025, promote to a domain controller (`ctf.local`)
2. Create OUs: `CTF-Users`, `CTF-Admins`, `Groups`
3. Create test user accounts and a `CTF-Players` security group

### 2. Application server
```bash
git clone https://github.com/JxCalmeiro/ctf-senior-project.git
cd ctf-senior-project
docker compose up -d --build
docker compose exec ctf-web python init_db.py
```

### 3. Ollama
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.1:8b
```

### 4. Environment
Copy `.env.example` to `.env` and adjust values (LDAP host, database credentials, webhook secret) to match your environment.

## Challenge Set

| Challenge | Category | Difficulty | Points |
|---|---|---|---|
| Caesar Cipher Warmup | Crypto | Easy | 100 |
| Layers | Crypto | Easy | 100 |
| Repeating Key | Crypto | Medium | 150 |
| Recycle Bin Recovery | Forensics | Medium | 200 |
| Hidden in Plain Sight | Web | Easy | 100 |
| Internal Portal | Web | Medium | 150 |

## AI Hint Bot Design

The hint bot runs entirely locally via Ollama — no data leaves the network, no API costs. It enforces:
- Never reveals flags, even under direct prompt injection attempts
- Tiered hint specificity (vague category-level nudges at tier 1, escalating with tier)
- All hint requests logged to the database for auditability

Tested against prompt injection ("ignore previous instructions...") and social-engineering ("I am the professor grading this...") attempts — both correctly refused to leak the flag.

## Notes / Known Limitations

- LDAP authentication runs unencrypted (port 389) rather than LDAPS, due to a Windows Server 2025 LDAP-signing enforcement change encountered during development. LDAPS remains a documented hardening opportunity.
- The GitHub webhook is tunneled via Cloudflare Tunnel (`cloudflared`) for local development; a production deployment would use a static public endpoint instead.
- The Ollama hint bot occasionally exceeds intended tier-1 vagueness (naming a technique earlier than intended) — a known tradeoff of running a smaller local model versus a larger hosted one.

## Built With

Claude Code, Flask, MySQL, Docker, Ollama, VMware Workstation Pro, Windows Server 2025, Ubuntu Server 24.04





