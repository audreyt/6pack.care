"""Shared Google Docs auth helpers for local scripts and workflows."""

from __future__ import annotations

import os

from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import Resource, build


def credentials_from_env() -> Credentials:
    refresh = os.environ.get("GOOGLE_REFRESH_TOKEN")
    client_id = os.environ.get("GOOGLE_CLIENT_ID")
    client_secret = os.environ.get("GOOGLE_CLIENT_SECRET")
    if not all([refresh, client_id, client_secret]):
        raise SystemExit(
            "Missing env: GOOGLE_REFRESH_TOKEN, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET"
        )
    return Credentials(
        token=None,
        refresh_token=refresh,
        client_id=client_id,
        client_secret=client_secret,
        token_uri="https://oauth2.googleapis.com/token",
    )


def _format_refresh_error(exc: RefreshError) -> str:
    message = str(exc)
    if "invalid_grant" in message:
        return (
            "Google Docs auth failed: OAuth refresh was rejected (`invalid_grant`). "
            "Reissue GOOGLE_REFRESH_TOKEN for the same OAuth client, or update "
            "GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET to match the client that "
            "issued the token."
        )
    return f"Google Docs auth failed: {message}"


def build_docs_service() -> Resource:
    creds = credentials_from_env()
    try:
        creds.refresh(Request())
    except RefreshError as exc:
        raise SystemExit(_format_refresh_error(exc)) from exc
    return build("docs", "v1", credentials=creds)
