<div align="center">

# 🧠 TalentFlow HR Agent

### *The AI-Powered HR Automation Platform That Does the Heavy Lifting*

[![Live Demo](https://img.shields.io/badge/🌐%20Live%20Demo-Netlify-00C7B7?style=for-the-badge)](https://zesty-malabi-8f49d2.netlify.app)
[![Backend API](https://img.shields.io/badge/⚡%20Backend%20API-Railway-7E3AF2?style=for-the-badge)](https://nasiko-production.up.railway.app/health)
[![Protocol](https://img.shields.io/badge/Protocol-A2A%20JSON--RPC%202.0-0078D4?style=for-the-badge)]()
[![Model](https://img.shields.io/badge/AI-GPT--4o--mini-412991?style=for-the-badge&logo=openai)](https://platform.openai.com)
[![Database](https://img.shields.io/badge/Database-MongoDB%20Atlas-47A248?style=for-the-badge&logo=mongodb)](https://www.mongodb.com/atlas)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python)](https://python.org)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react)](https://react.dev)

---

*From screening 500 resumes to predicting who\'s about to quit — TalentFlow handles the entire employee lifecycle so your HR team doesn\'t have to.*

</div>

---

## 🚀 What Is TalentFlow?

TalentFlow is a **full-stack, AI-native HR automation platform** that replaces the most time-consuming parts of Human Resources with an intelligent conversational agent. It is built on the **A2A (Agent-to-Agent) JSON-RPC 2.0 protocol**, allowing it to interoperate with other AI agents in a multi-agent ecosystem.

The platform serves **two distinct user types**:
- 👔 **HR Professionals** — who get a powerful dashboard, AI chat assistant, resume screener, attrition predictor, onboarding planner, and more
- 🧑‍💼 **Job Candidates** — who can self-apply, check their application status, get CV improvement advice, and negotiate offers confidently

Powered by **OpenAI GPT-4o-mini** with a toolset of **19 specialized HR functions**, a **React frontend**, a **FastAPI backend**, and **MongoDB Atlas** as the persistent brain.

---

## ✨ The 19 Tools — What the Agent Can Do

This is the heart of TalentFlow. The agent intelligently selects and calls the right tool based on any natural language request. No menus. No forms. Just ask.

| # | Tool | What It Does | Real-World Problem Solved |
|---|------|-------------|--------------------------|
| 1 | `screen_resume` | Scores a resume against a job description, identifies skill gaps, and returns **Proceed / Hold / Reject** with a fit score | Eliminates hours of manual resume sifting for every open role |
| 2 | `generate_interview_questions` | Creates a **tailored question bank** based on the candidate\'s specific profile gaps vs the JD | Interviewers walk in prepared, not improvising |
| 3 | `draft_email` | Writes polished **offer or rejection emails** ready to send | Zero awkward copy-paste moments |
| 4 | `match_internal_talent` | Searches existing employees in MongoDB **before posting externally** | Reduces hiring costs by surfacing hidden internal talent |
| 5 | `answer_policy_question` | Answers any HR policy FAQ from the official embedded policy document | Instant 24/7 policy clarification — no HR ticket needed |
| 6 | `flag_burnout_risk` | Pulls an employee\'s work data from MongoDB and returns a **burnout risk score + interventions** | Catch burnout before it becomes resignation |
| 7 | `store_candidate` | Persists a screened candidate\'s full profile and status into MongoDB | Builds a living talent pipeline that HR can revisit anytime |
| 8 | `check_application_status` | Candidate looks up their own status by email — **no login required** | Self-service for candidates; fewer "did I get the job?" emails |
| 9 | `improve_cv` | Returns structured, role-aware feedback on how to strengthen a CV | Candidates improve; quality of applicant pool rises |
| 10 | `send_email_to_candidate` | **Actually sends** a styled HTML email via Gmail SMTP — not just a draft | One-click delivery of offer/rejection with branded formatting |
| 11 | `get_my_meetings` | Fetches today\'s or tomorrow\'s interviews from **Google Calendar** | HR never opens Calendar — meetings appear in the chat |
| 12 | `add_employee_to_database` | Adds a fully onboarded employee record to MongoDB | Single command to register a new hire across the system |
| 13 | `check_leave_balance` | Returns leave entitlement data for any employee | Instant leave queries without bugging the HR inbox |
| 14 | `generate_onboarding_plan` | Creates a detailed **Day 1 / 30-day / 60-day / 90-day plan** for any role + department | New hires don\'t fall through the cracks in their first month |
| 15 | `predict_attrition_risk` | Scores **flight risk** for one employee or the entire team + retention actions | Act before the resignation letter, not after |
| 16 | `benchmark_salary` | Compares an offered salary against **market rates** by role, experience, and location | Stop losing candidates to counteroffers — know the market |
| 17 | `analyze_exit_interview` | Parses an exit interview transcript and extracts **root causes + systemic patterns** | Turn departing employee feedback into org-level insight |
| 18 | `advise_offer_negotiation` | Returns **word-for-word negotiation scripts** from the candidate\'s perspective | Candidates negotiate confidently; companies attract better talent |
| 19 | `get_pipeline_summary` | Returns a live **hiring pipeline overview** — counts by stage and role | Recruiters see their funnel at a glance, no spreadsheet needed |

---

## 🖥️ Frontend — 8 Pages for Every Workflow

The React frontend is a complete HR portal with role-aware navigation (HR vs Candidate).

### 🏠 Home Page
Landing page with 8 animated feature cards, tech stack highlights, and dual CTA buttons — *"I\'m an HR Professional"* and *"I\'m a Candidate"*. First impression of the full platform scope.

### 🔐 Login Page
Dual-path authentication:
- **HR** → enters a 4-digit HR code (no database needed, zero friction)
- **Candidate** → self-registers with name + email → instantly gets a candidate profile

### 📊 Dashboard Page *(HR only)*
The command center for HR teams. Four live data tabs:

| Tab | Data Shown |
|-----|-----------|
| 🔥 Burnout Risk | All employees sorted by burnout score with risk level badges |
| 📋 Candidates Pipeline | Every screened candidate with status, role, and score |
| 📉 Attrition Risk | Employee flight-risk scores with retention action tooltips |
| 📅 My Meetings | Today\'s calendar pulled live from Google Calendar |

Plus an **Add Employee** modal — fill a form, click save, employee is in MongoDB instantly.

### 📄 Resume Screener Page *(HR only)*
- Upload a **PDF resume** — extracted server-side via PyMuPDF
- Paste the job description
- Get AI screening: fit score, matched skills, gaps, recommendation
- Save to MongoDB with one click
- Trigger email send directly from the result panel
- Schedule interview (Google Calendar quick-add link)

### 🔍 Internal Talent Search Page *(HR only)*
- Natural-language search: *"Find me someone with Python and 3 years of ML experience"*
- Agent searches the employee database before recommending external hiring
- Returns matched employees with skill breakdowns

### 🎯 Onboarding Plan Page *(HR only)*
- Enter new hire\'s role, department, and start date
- Generates a structured Day 1, 30-day, 60-day, and 90-day plan
- Exportable as readable text or shareable via chat

### 👋 Exit Interview Page *(HR only)*
- Paste the full exit interview transcript
- AI identifies: primary resignation reason, secondary factors, systemic patterns, severity level
- Output structured as an actionable report for HR leadership

### 💬 Chat Page *(Both roles)*
- **HR view** → Full AI assistant: ask anything from *"What\'s Priya\'s burnout risk?"* to *"Draft me an offer for Aditya"*
- **Candidate view** → Ask about application status, get CV tips, practice negotiation scenarios
- Real-time responses backed by all 19 tools

### 📝 Apply Page *(Candidate only)*
- Upload CV + select target role
- AI screens the CV and auto-saves a *"pending"* profile in MongoDB
- Candidate gets instant feedback on their fit

---

## 🏗️ Architecture

```
+------------------------------------------------------------------+
|                       FRONTEND (React)                           |
|   Netlify CDN  .  8 Pages  .  Role-Aware Navigation              |
|   zesty-malabi-8f49d2.netlify.app                                |
+---------------------------+--------------------------------------+
                            |  HTTPS REST + A2A JSON-RPC 2.0
                            v
+------------------------------------------------------------------+
|                     BACKEND (FastAPI)                            |
|   Railway  .  nasiko-production.up.railway.app                   |
|                                                                  |
|  +--------------+   +----------------------------------------+  |
|  |  REST Routes |   |         LangGraph Agent                 |  |
|  |  /candidates |   |  +----------------------------------+   |  |
|  |  /employees  |   |  |  ChatOpenAI  GPT-4o-mini         |   |  |
|  |  /upload-pdf |   |  |  temp=0.2  .  19 bound tools     |   |  |
|  |  /email/send |   |  +----------+-----------------------+   |  |
|  |  /calendar/  |   |             | tool calls              |  |
|  +--------------+   |  +----------v-----------------------+   |  |
|                     |  |         Tools Layer              |   |  |
|                     |  |  Screen . Generate . Draft .     |   |  |
|                     |  |  Match . Store . Email . Cal .   |   |  |
|                     |  |  Attrition . Onboard . Exit ...  |   |  |
|                     |  +----------------------------------+   |  |
|                     +----------------------------------------+  |
+-----------+-----------------------------+------------------------+
            |                             |
            v                             v
+------------------+           +---------------------+
|  MongoDB Atlas   |           |  External Services  |
|  talentflow DB   |           |  Gmail SMTP         |
|  . candidates    |           |  Google Calendar    |
|  . employees     |           |  OpenAI API         |
+------------------+           +---------------------+
```

---

## 🛠️ Full Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **AI Model** | OpenAI GPT-4o-mini | Language model powering all 19 tools |
| **Agent Framework** | LangGraph + LangChain | Stateful tool-calling agent with conversation memory |
| **Protocol** | A2A JSON-RPC 2.0 | Standardised agent-to-agent communication |
| **Backend** | FastAPI + Uvicorn | High-performance async Python API server |
| **PDF Parsing** | PyMuPDF (fitz) | Server-side resume text extraction from PDF uploads |
| **Database** | MongoDB Atlas | Cloud-hosted document store for candidates + employees |
| **ODM** | PyMongo | Python MongoDB driver |
| **Email** | Gmail SMTP + smtplib | Sends real HTML emails to candidates |
| **Calendar** | Google Calendar API | Fetches/creates interview events |
| **Frontend** | React 18 (CRA) | Single-page application with hooks + CSS Modules |
| **HTTP Client** | Axios | Frontend API calls with interceptors |
| **Container** | Docker + Docker Compose | Reproducible local + CI builds |
| **Frontend Host** | Netlify | CDN-deployed React build with SPA redirects |
| **Backend Host** | Railway | Auto-deployed from GitHub with env var injection |

---

## 🔌 API Reference

### Health Check
```
GET /health
Response: { "status": "ok", "service": "TalentFlow HR Agent", "version": "2.0.0" }
```

### A2A Chat — Main Endpoint
```
POST /
Content-Type: application/json

{
  "jsonrpc": "2.0",
  "id": "<uuid>",
  "method": "message/send",
  "params": {
    "message": {
      "role": "user",
      "parts": [{ "kind": "text", "text": "<your HR request>" }]
    }
  }
}
```

### REST Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/upload-pdf` | Upload resume PDF, returns extracted text |
| `GET` | `/candidates` | List all candidates from MongoDB |
| `GET` | `/candidates/<email>` | Single candidate by email |
| `GET` | `/employees` | List all employees from MongoDB |
| `POST` | `/email/send` | Trigger an offer/rejection email |
| `POST` | `/calendar/schedule` | Create a calendar event or return quick-add URL |
| `POST` | `/internal-search` | Employee search by natural language |

---

## 🧪 Live A2A Examples

### 1 — Screen a Resume
```bash
curl -X POST https://nasiko-production.up.railway.app/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc":"2.0","id":"demo-1","method":"message/send",
    "params":{"message":{"role":"user","parts":[{"kind":"text",
    "text":"Screen this resume for a Senior Backend Engineer. Candidate: Aditya Verma, 4 yrs Python, Django, PostgreSQL. No Kubernetes. JD requires Python, SQL, REST, Docker, Kubernetes."}]}}
  }'
```

### 2 — Check Burnout Risk
```bash
curl -X POST https://nasiko-production.up.railway.app/ \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":"demo-2","method":"message/send",
       "params":{"message":{"role":"user","parts":[{"kind":"text","text":"What is the burnout risk for Priya Sharma?"}]}}}'
```

### 3 — Predict Team Attrition
```bash
curl -X POST https://nasiko-production.up.railway.app/ \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":"demo-3","method":"message/send",
       "params":{"message":{"role":"user","parts":[{"kind":"text","text":"Predict attrition risk for all employees and show me who is most likely to leave."}]}}}'
```

### 4 — Benchmark Salary
```bash
curl -X POST https://nasiko-production.up.railway.app/ \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":"demo-4","method":"message/send",
       "params":{"message":{"role":"user","parts":[{"kind":"text","text":"Is 18 LPA competitive for a Data Scientist with 3 years experience in Bangalore?"}]}}}'
```

### 5 — Generate Onboarding Plan
```bash
curl -X POST https://nasiko-production.up.railway.app/ \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":"demo-5","method":"message/send",
       "params":{"message":{"role":"user","parts":[{"kind":"text","text":"Create a 30-60-90 day onboarding plan for a new Product Manager joining the Growth team on 2025-08-01."}]}}}'
```

---

## 🐳 Docker Agent Packages

Three pre-packaged Docker agent ZIPs are available for multi-agent deployments:

| ZIP File | Agent Role | Use Case |
|----------|-----------|----------|
| `talentflow-candidate.zip` | Candidate-facing agent | CV improvement, application status, offer negotiation |
| `talentflow-internal-hr.zip` | Internal HR agent | Burnout, attrition, leave, onboarding, policy |
| `talentflow-recruitment-hr.zip` | Recruitment agent | Screening, questions, email, pipeline, internal matching |

```bash
# Unzip and run any agent
unzip talentflow-recruitment-hr.zip
cd talentflow-recruitment-hr
docker-compose up
```

---

## ⚙️ Local Development Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker Desktop *(optional)*
- MongoDB Atlas account *(free tier works)*
- OpenAI API Key

### 1. Clone and Backend Setup

```bash
git clone https://github.com/TheSidPai/Nasiko.git
cd Nasiko/talentflowHR

python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create `talentflowHR/.env`:

```env
# Required
OPENAI_API_KEY=sk-proj-...
MONGO_URI=mongodb+srv://<user>:<pass>@<cluster>.mongodb.net/talentflow?retryWrites=true&w=majority

# Email (Gmail SMTP)
GMAIL_USER=your@gmail.com
GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx

# Google Calendar (optional — falls back to quick-add URL if not set)
GOOGLE_CALENDAR_CREDENTIALS_JSON=
GOOGLE_CALENDAR_ID=primary
GOOGLE_CALENDAR_TIMEZONE=Asia/Kolkata
```

### 3. Run the Backend

```bash
cd src
python __main__.py --host 0.0.0.0 --port 5000
```

### 4. Run the Frontend

```bash
cd frontend
npm install
npm start
# Opens at http://localhost:3000
```

### 5. Run Everything with Docker

```bash
docker-compose up --build
```

---

## 🌍 Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | OpenAI API key for GPT-4o-mini |
| `MONGO_URI` | Yes | Full MongoDB Atlas connection string |
| `GMAIL_USER` | For email | Gmail address used for SMTP sending |
| `GMAIL_APP_PASSWORD` | For email | Google app password (16-char, not account password) |
| `GOOGLE_CALENDAR_CREDENTIALS_JSON` | Optional | Path to Google service account JSON |
| `GOOGLE_CALENDAR_ID` | Optional | Calendar ID (default: `primary`) |
| `GOOGLE_CALENDAR_TIMEZONE` | Optional | Timezone string (default: `Asia/Kolkata`) |

---

## 📁 Project Structure

```
talentflowHR/
|
+-- README.md                    <- You are here
+-- AgentCard.json               <- A2A agent discovery descriptor
+-- requirements.txt             <- Python dependencies
+-- Dockerfile                   <- Backend container definition
+-- docker-compose.yml           <- Full stack orchestration
|
+-- src/                         <- Python backend
|   +-- __main__.py              <- FastAPI server + A2A protocol handler
|   +-- models.py                <- A2A Pydantic request/response models
|   +-- agent.py                 <- LangGraph agent + GPT-4o-mini config
|   +-- tools.py                 <- All 19 HR tools (1087 lines)
|   +-- email_service.py         <- Gmail SMTP + HTML email templates
|   +-- calendar_service.py      <- Google Calendar API integration
|   \-- __init__.py
|
\-- frontend/                    <- React application
    +-- package.json
    +-- public/
    |   +-- index.html
    |   \-- _redirects            <- Netlify SPA redirect rule
    \-- src/
        +-- App.jsx               <- Router + auth guard
        +-- components/Nav/       <- Role-aware navigation bar
        +-- constants/index.js    <- API base URL + HR code constant
        +-- pages/
        |   +-- HomePage/         <- Landing page
        |   +-- LoginPage/        <- HR + Candidate auth
        |   +-- DashboardPage/    <- 4-tab HR command center
        |   +-- ResumePage/       <- PDF upload + AI screening
        |   +-- InternalSearchPage/ <- Employee talent search
        |   +-- OnboardingPage/   <- 30/60/90-day plan generator
        |   +-- ExitInterviewPage/ <- Transcript analysis
        |   +-- ChatPage/         <- AI assistant (HR + Candidate)
        |   \-- ApplyPage/        <- Candidate self-apply
        +-- services/api.js       <- Axios client + all API calls
        \-- styles/               <- Global CSS + theme
```

---

## 🚢 Deployment

### Backend — Railway

```
Production URL : https://nasiko-production.up.railway.app/
Health Check   : https://nasiko-production.up.railway.app/health
```

Railway auto-deploys from the `master` branch. Set these environment variables in the Railway dashboard: `OPENAI_API_KEY`, `MONGO_URI`, `GMAIL_USER`, `GMAIL_APP_PASSWORD`.

### Frontend — Netlify

```
Production URL : https://zesty-malabi-8f49d2.netlify.app
```

The `_redirects` file in `public/` ensures SPA routing works correctly on Netlify.

```bash
# To redeploy after code changes
cd frontend
npm run build
# Drag and drop the build/ folder to Netlify dashboard
```

---

## 🤝 A2A Protocol

TalentFlow implements the **Agent-to-Agent (A2A) JSON-RPC 2.0** standard. The `AgentCard.json` describes the agent for discovery by other A2A-compatible agents:

```json
{
  "name": "TalentFlow HR Agent",
  "version": "2.0.0",
  "protocol": "A2A/1.0",
  "endpoint": "https://nasiko-production.up.railway.app/",
  "capabilities": ["text-generation", "tool-use", "multi-turn"],
  "skills": ["recruitment", "hr-automation", "people-analytics"]
}
```

---

## 👥 Team

Built for the **Nasiko A2A Agent Platform** project at **IIT Dharwad**.

---

<div align="center">

*Built with love and way too much coffee*

[![Try It Live](https://img.shields.io/badge/Try%20It%20Live-TalentFlow-00C7B7?style=for-the-badge)](https://zesty-malabi-8f49d2.netlify.app)

</div>