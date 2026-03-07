"""
calendar_service.py
Google Calendar interview scheduling for TalentFlow HR.

Two modes:
  1. API mode  — Creates a real Google Calendar event server-side.
               Requires a Service Account with Calendar API enabled.
               Set in .env:
                 GOOGLE_CALENDAR_CREDENTIALS_JSON=src/credentials.json
                 GOOGLE_CALENDAR_ID=primary   (or a calendar ID)

  2. Link mode — Returns a pre-filled Google Calendar "quick add" URL
               that the recruiter can open to save the event.
               No credentials required.
"""

import os
import logging
import urllib.parse
from datetime import datetime, timedelta
from typing import Optional

logger = logging.getLogger("talentflow.calendar")

CREDENTIALS_PATH = os.getenv("GOOGLE_CALENDAR_CREDENTIALS_JSON", "")
CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID", "primary")
CALENDAR_TIMEZONE = os.getenv("GOOGLE_CALENDAR_TIMEZONE", "Asia/Kolkata")


def _format_google_datetime(dt: datetime) -> str:
    """Format a datetime for Google Calendar API (RFC3339)."""
    return dt.strftime("%Y-%m-%dT%H:%M:%S")


def _build_calendar_url(
    title: str,
    start_dt: datetime,
    end_dt: datetime,
    description: str = "",
    attendee_email: str = "",
    location: str = "Video Call (Google Meet)",
) -> str:
    """
    Build a Google Calendar 'add event' URL.
    Opens in browser, no credentials required.
    """
    fmt = "%Y%m%dT%H%M%S"  # Google Calendar URL format
    dates = f"{start_dt.strftime(fmt)}/{end_dt.strftime(fmt)}"

    params = {
        "action": "TEMPLATE",
        "text": title,
        "dates": dates,
        "details": description,
        "location": location,
    }
    if attendee_email:
        params["add"] = attendee_email

    base = "https://calendar.google.com/calendar/render"
    return f"{base}?{urllib.parse.urlencode(params)}"


def schedule_interview_link(
    candidate_name: str,
    role: str,
    interviewer_email: str = "",
    interview_datetime_iso: str = "",
    duration_minutes: int = 60,
    notes: str = "",
) -> dict:
    """
    Generate a Google Calendar quick-add link for an interview.

    No credentials required. Returns the URL for the recruiter to open.

    Args:
        candidate_name: Name of the candidate
        role: Role being interviewed for
        interviewer_email: Interviewer's email (added as attendee)
        interview_datetime_iso: ISO datetime string (e.g. "2025-02-15T14:00:00")
                                Defaults to tomorrow at 10:00 AM if not provided.
        duration_minutes: Interview duration (default 60 min)
        notes: Additional notes for the calendar event

    Returns:
        dict with 'calendar_url', 'event_title', 'start_time', 'end_time'
    """
    try:
        if interview_datetime_iso:
            start_dt = datetime.fromisoformat(interview_datetime_iso.replace("Z", ""))
        else:
            # Default: tomorrow at 10:00 AM
            tomorrow = datetime.now() + timedelta(days=1)
            start_dt = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0)

        end_dt = start_dt + timedelta(minutes=duration_minutes)

        title = f"Interview: {candidate_name} – {role}"
        description = (
            f"TalentFlow HR Interview\n\n"
            f"Candidate: {candidate_name}\n"
            f"Role: {role}\n"
            f"Duration: {duration_minutes} minutes\n"
        )
        if notes:
            description += f"\nNotes: {notes}"
        description += "\n\nScheduled via TalentFlow HR Agent 🤖"

        url = _build_calendar_url(
            title=title,
            start_dt=start_dt,
            end_dt=end_dt,
            description=description,
            attendee_email=interviewer_email,
        )

        return {
            "success": True,
            "mode": "link",
            "calendar_url": url,
            "event_title": title,
            "start_time": start_dt.isoformat(),
            "end_time": end_dt.isoformat(),
            "message": "Calendar link generated. Open the URL to save the event.",
        }

    except Exception as e:
        logger.error(f"Calendar link generation error: {e}", exc_info=True)
        return {"success": False, "error": f"Failed to generate calendar link: {str(e)}"}


def schedule_interview_api(
    candidate_name: str,
    role: str,
    candidate_email: str = "",
    interviewer_email: str = "",
    interview_datetime_iso: str = "",
    duration_minutes: int = 60,
    notes: str = "",
) -> dict:
    """
    Create a real Google Calendar event using the Calendar API.
    Requires GOOGLE_CALENDAR_CREDENTIALS_JSON pointing to a service account key file.

    The calendar must be shared with the service account email.
    """
    if not CREDENTIALS_PATH or not os.path.exists(CREDENTIALS_PATH):
        logger.info("No Calendar API credentials found — falling back to link mode.")
        return schedule_interview_link(
            candidate_name=candidate_name,
            role=role,
            interviewer_email=interviewer_email or candidate_email,
            interview_datetime_iso=interview_datetime_iso,
            duration_minutes=duration_minutes,
            notes=notes,
        )

    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build

        credentials = service_account.Credentials.from_service_account_file(
            CREDENTIALS_PATH,
            scopes=["https://www.googleapis.com/auth/calendar"],
        )

        service = build("calendar", "v3", credentials=credentials)

        if interview_datetime_iso:
            start_dt = datetime.fromisoformat(interview_datetime_iso.replace("Z", ""))
        else:
            tomorrow = datetime.now() + timedelta(days=1)
            start_dt = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0)

        end_dt = start_dt + timedelta(minutes=duration_minutes)

        attendees = []
        if candidate_email:
            attendees.append({"email": candidate_email})
        if interviewer_email:
            attendees.append({"email": interviewer_email})

        description = (
            f"TalentFlow HR Interview\n\n"
            f"Candidate: {candidate_name}\nRole: {role}\n"
        )
        if notes:
            description += f"Notes: {notes}\n"
        description += "\nScheduled via TalentFlow HR Agent 🤖"

        event_body = {
            "summary": f"Interview: {candidate_name} – {role}",
            "description": description,
            "start": {
                "dateTime": _format_google_datetime(start_dt),
                "timeZone": CALENDAR_TIMEZONE,
            },
            "end": {
                "dateTime": _format_google_datetime(end_dt),
                "timeZone": CALENDAR_TIMEZONE,
            },
            "attendees": attendees,
            "conferenceData": {
                "createRequest": {
                    "requestId": f"talentflow-{candidate_name.replace(' ', '-').lower()}-{int(start_dt.timestamp())}",
                    "conferenceSolutionKey": {"type": "hangoutsMeet"},
                }
            },
            "reminders": {
                "useDefault": False,
                "overrides": [
                    {"method": "email", "minutes": 60},
                    {"method": "popup", "minutes": 15},
                ],
            },
        }

        event = service.events().insert(
            calendarId=CALENDAR_ID,
            body=event_body,
            conferenceDataVersion=1,
            sendUpdates="all",
        ).execute()

        meet_link = event.get("hangoutLink", "")
        event_link = event.get("htmlLink", "")

        logger.info(f"Calendar event created: {event.get('id')} for {candidate_name}")
        return {
            "success": True,
            "mode": "api",
            "event_id": event.get("id"),
            "event_link": event_link,
            "meet_link": meet_link,
            "calendar_url": event_link,
            "start_time": start_dt.isoformat(),
            "end_time": end_dt.isoformat(),
            "message": (
                f"Interview scheduled! "
                + (f"Google Meet: {meet_link}" if meet_link else f"Event link: {event_link}")
            ),
        }

    except ImportError:
        logger.warning("google-api-python-client not installed — falling back to link mode.")
        return schedule_interview_link(
            candidate_name=candidate_name,
            role=role,
            interviewer_email=interviewer_email or candidate_email,
            interview_datetime_iso=interview_datetime_iso,
            duration_minutes=duration_minutes,
            notes=notes,
        )
    except Exception as e:
        logger.error(f"Google Calendar API error: {e}", exc_info=True)
        # Graceful fallback to link mode
        fallback = schedule_interview_link(
            candidate_name=candidate_name,
            role=role,
            interviewer_email=interviewer_email or candidate_email,
            interview_datetime_iso=interview_datetime_iso,
            duration_minutes=duration_minutes,
            notes=notes,
        )
        fallback["warning"] = f"Calendar API failed ({str(e)}). Returned quick-add link instead."
        return fallback


def schedule_interview(
    candidate_name: str,
    role: str,
    candidate_email: str = "",
    interviewer_email: str = "",
    interview_datetime_iso: str = "",
    duration_minutes: int = 60,
    notes: str = "",
) -> dict:
    """
    Main entry point. Uses API mode if credentials exist, otherwise link mode.
    Always succeeds — falls back to link mode on any API failure.
    """
    return schedule_interview_api(
        candidate_name=candidate_name,
        role=role,
        candidate_email=candidate_email,
        interviewer_email=interviewer_email,
        interview_datetime_iso=interview_datetime_iso,
        duration_minutes=duration_minutes,
        notes=notes,
    )
