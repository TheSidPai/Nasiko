# TalentFlow HR Agent

An intelligent HR automation agent built on the Nasiko A2A platform. Automates full-cycle recruitment, internal talent matching, policy FAQs, and burnout risk detection.

## Capabilities (Stage 1)

| Tool | What it does |
|------|-------------|
| Resume Screening | Scores a resume against a JD, identifies skill gaps, gives a hiring recommendation |
| Interview Questions | Generates tailored questions based on candidate profile and role gaps |
| Email Drafting | Drafts offer or rejection emails |
| Internal Talent Matching | Checks existing employees before posting a role externally |
| Policy FAQ | Answers employee HR policy questions from the official policy document |
| Burnout Risk Detection | Flags at-risk employees and suggests interventions |

## Tech Stack

- **Protocol**: A2A JSON-RPC 2.0
- **Server**: FastAPI
- **Agent**: LangChain + Google Gemini 1.5 Flash
- **Containerisation**: Docker

## Setup

### Prerequisites
- Python 3.11+
- Docker Desktop
- Google Gemini API Key (free at [aistudio.google.com](https://aistudio.google.com))

### Local Development (no Docker)

```bash
# Install dependencies
pip install fastapi uvicorn pydantic python-dotenv requests \
  "langchain>=0.2.0,<0.3.0" langchain-google-genai google-generativeai click

# Set your API key
export GOOGLE_API_KEY=your_gemini_api_key_here

# Run the server
cd src
python __main__.py --host 0.0.0.0 --port 5000
```

### Docker

```bash
# Build
docker build -t talentflow-hr-agent .

# Run
docker run -p 5000:5000 -e GOOGLE_API_KEY=your_key talentflow-hr-agent
```

### Test with curl

```bash
# Policy FAQ example
curl -X POST http://localhost:5000/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "test-1",
    "method": "message/send",
    "params": {
      "message": {
        "role": "user",
        "parts": [{"kind": "text", "text": "How many days of annual leave do I get?"}]
      }
    }
  }'

# Burnout risk example
curl -X POST http://localhost:5000/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "test-2",
    "method": "message/send",
    "params": {
      "message": {
        "role": "user",
        "parts": [{"kind": "text", "text": "Check burnout risk for Priya Sharma"}]
      }
    }
  }'
```

## Project Structure

```
talentflow-hr-agent/
├── src/
│   ├── __main__.py      # FastAPI server + A2A protocol (do not edit)
│   ├── models.py        # A2A Pydantic models (do not edit)
│   ├── agent.py         # LangChain agent + Gemini config
│   └── tools.py         # All HR tools
├── Dockerfile
├── docker-compose.yml
├── AgentCard.json
└── README.md
```

## Stage 2 (Coming Soon)

- Exit interview pattern analysis
- Interview scheduling with calendar integration
- Offer vs JD integrity checker
