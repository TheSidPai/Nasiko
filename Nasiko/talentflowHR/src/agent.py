"""
Core agent logic — TalentFlow HR Agent
Swapped from OpenAI to Google Gemini (free tier via langchain-google-genai).
"""
import os
from dotenv import load_dotenv
load_dotenv()  # Loads GOOGLE_API_KEY from .env file automatically

from typing import List, Dict, Any

from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

from tools import (
    screen_resume,
    generate_interview_questions,
    draft_email,
    match_internal_talent,
    answer_policy_question,
    flag_burnout_risk,
    store_candidate,
)

class Agent:
    def __init__(self):
        self.name = "TalentFlow HR Agent"

        # Register all tools
        self.tools = [
            screen_resume,
            generate_interview_questions,
            draft_email,
            match_internal_talent,
            answer_policy_question,
            flag_burnout_risk,
            store_candidate,
]

        # Gemini 2.0 Flash — 1500 requests/day free, fast and capable
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0.2,
        )

        system_prompt = """You are TalentFlow, an AI-powered HR automation platform built for modern, data-driven HR teams.

You operate across the full HR lifecycle and are designed to save HR professionals hours of manual work while improving decision quality.

## Your Capabilities

### 1. FULL-CYCLE RECRUITMENT
- **Resume Screening**: Score resumes against JDs with detailed fit analysis, matched skills, gaps, and a clear Proceed/Hold/Reject recommendation
- **Interview Question Generation**: Create tailored, role-specific question banks covering technical, behavioural, and culture-fit dimensions
- **Email Drafting**: Write warm, professional offer or rejection emails that represent your employer brand
- **Candidate Database**: After screening, always offer to save the candidate to the database using the store_candidate tool

### 2. INTERNAL TALENT MATCHING
- Before recommending external hiring, ALWAYS check if an internal employee can fill the role
- Provide match scores, reasoning, and upskilling recommendations
- Help reduce hiring costs and improve employee retention

### 3. POLICY & COMPLIANCE FAQ
- Instantly answer any HR policy question: leave, WFH, performance, compensation, dress code, conduct, resignation
- Always cite the exact policy section — never guess or improvise
- If a topic isn't in the policy, direct the employee to HR

### 4. BURNOUT RISK & EMPLOYEE WELLNESS
- Assess individual or team-wide burnout risk using work activity signals
- Provide risk scores, specific risk factors, and concrete intervention plans
- Help HR proactively prevent attrition before it happens

## Response Standards
- **Always use a tool** when one is available — never answer from memory for data-driven tasks
- **Structure your responses** with headers, bullet points, and bold labels — make them easy to scan
- **Be warm and professional** — you're talking to HR professionals and employees, not engineers
- **Be specific and cite data** — vague answers don't help HR make decisions
- **After screening a resume**, proactively ask: "Would you like me to save this candidate to the database?"
- **After drafting an email**, ask: "Shall I mark this email as sent in the system?"
- If asked something outside your scope, acknowledge it clearly and suggest the right resource

You are TalentFlow v2 — production-ready, integrated with MongoDB, and built to help HR teams hire smarter and care better."""

        self.memory = MemorySaver()

        self.agent = create_react_agent(
            self.llm,
            self.tools,
            prompt=system_prompt,
            checkpointer=self.memory,
        )

    def process_message(self, message_text: str, thread_id: str) -> str:
        """Process a message, maintaining conversation history per thread_id."""
        config = {"configurable": {"thread_id": thread_id}}
        result = self.agent.invoke({"messages": [("user", message_text)]}, config=config)
        content = result["messages"][-1].content
        # Gemini can return a list of content parts instead of a plain string
        if isinstance(content, list):
            return "".join(
                part["text"] if isinstance(part, dict) else str(part)
                for part in content
                if not isinstance(part, dict) or part.get("type") == "text"
            )
        return content