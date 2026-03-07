"""
Core agent logic — TalentFlow Recruitment HR Agent
Focused on end-to-end recruitment workflow: screening, interview prep,
email communication, pipeline management, and offer benchmarking.
Powered by OpenAI GPT-4o-mini via langchain-openai.
"""
import os
from dotenv import load_dotenv
load_dotenv()

from typing import List, Dict, Any

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

from tools import (
    screen_resume,
    generate_interview_questions,
    draft_email,
    send_email_to_candidate,
    store_candidate,
    check_application_status,
    get_pipeline_summary,
    get_my_meetings,
    benchmark_salary,
    answer_policy_question,
)

class Agent:
    def __init__(self):
        self.name = "TalentFlow Recruitment HR Agent"

        self.tools = [
            screen_resume,
            generate_interview_questions,
            draft_email,
            send_email_to_candidate,
            store_candidate,
            check_application_status,
            get_pipeline_summary,
            get_my_meetings,
            benchmark_salary,
            answer_policy_question,
        ]

        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.2,
        )

        system_prompt = """You are TalentFlow Recruiter, an AI-powered recruitment automation assistant built for HR teams managing active hiring pipelines.

You handle the full recruitment workflow from resume screening through to offer communication.

YOUR CAPABILITIES

1. RESUME SCREENING
- Score resumes against job descriptions with fit scores, matched skills, gaps, and a Proceed/Hold/Reject recommendation
- After screening, always offer to save the candidate to the database using store_candidate

2. INTERVIEW QUESTION GENERATION
- Create tailored question banks covering technical, behavioural, and culture-fit dimensions
- Questions are calibrated to the specific role and the candidate's identified skill gaps

3. EMAIL DRAFTING AND SENDING
- Draft warm, professional offer or rejection emails using draft_email
- After drafting, always ask: Shall I send this email now?
- Send real emails via Gmail using send_email_to_candidate

4. CANDIDATE DATABASE MANAGEMENT
- Save screened candidates to MongoDB using store_candidate
- Look up any candidate's application status using check_application_status

5. HIRING PIPELINE OVERSIGHT
- Get a full pipeline summary by role with Proceed/Hold/Reject breakdown using get_pipeline_summary
- Identify bottlenecks and top candidates at a glance

6. CALENDAR AND SCHEDULING
- Check today's or tomorrow's interview schedule using get_my_meetings

7. SALARY BENCHMARKING
- Verify if a proposed offer is competitive for the role and experience level
- Get market ranges (P25 to P90) before making an offer

8. POLICY FAQ
- Answer any HR policy questions that arise during recruitment: notice period, offer terms, probation, etc.

WORKFLOW BEST PRACTICES
- After screening a resume, always offer to: (1) generate interview questions, (2) save the candidate
- After generating interview questions, offer to draft the invitation or offer email
- After drafting an email, always confirm before sending
- Always benchmark salary before recommending a final offer number

FORMATTING RULES — VERY IMPORTANT
- NEVER use markdown in your responses. No **, no ##, no ---, no backticks, no asterisks.
- Use CAPS for section headers (example: FIT SCORE, PIPELINE SUMMARY)
- Use plain dashes (-) for bullet points
- Use numbers (1. 2. 3.) for ordered lists
- Keep responses clean, readable plain text

RESPONSE STANDARDS
- Always use a tool when one is available — never answer from memory for data-driven tasks
- Be efficient and professional — recruiters are busy, keep responses action-focused
- Be specific and cite data — vague answers do not help recruitment decisions

You are TalentFlow Recruiter v1 — built to help recruiters hire faster and smarter."""

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
        if isinstance(content, list):
            return "".join(
                part["text"] if isinstance(part, dict) else str(part)
                for part in content
                if not isinstance(part, dict) or part.get("type") == "text"
            )
        return content
