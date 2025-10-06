#!/usr/bin/env python3
"""
Script to exchange an Entra ID refresh token for an access token using MSAL.

This script authenticates against Azure Active Directory using environment variables
for tenant ID, client ID, and client secret. It accepts a refresh token as a command-line
argument and attempts to acquire a new access token for the Azure Database for PostgreSQL
resource.

Environment Variables:
    AZURE_TENANT_ID      - Entra ID tenant ID
    AZURE_CLIENT_ID      - Entra ID application (client) ID
    AZURE_CLIENT_SECRET  - Entra ID application client secret

Usage:
    entra_refresh_token_password.py <refresh_token>

Arguments:
    refresh_token        - Entra ID refresh token to exchange for an access token

Output:
    Prints the acquired access token to stdout on success.
    Prints error details to stderr and exits with non-zero status on failure.

Dependencies:
    msal (Microsoft Authentication Library for Python)
    
Exceptions:
    SystemExit:
        Raised when required environment variables are missing, when the refresh token argument is not provided,
        or when token acquisition fails.

    msal.MsalServiceError (implicit via MSAL library):
        May be raised internally by the MSAL library if there are issues communicating with Azure AD.
"""
import os
import sys
import msal

tenant_id = os.getenv("AZURE_TENANT_ID")
client_id = os.getenv("AZURE_CLIENT_ID")
client_secret = os.getenv("AZURE_CLIENT_SECRET")
scope = ["https://ossrdbms-aad.database.windows.net/.default"]

if not all([tenant_id, client_id, client_secret]):
    print("Error: One or more required environment variables are missing: "
          "AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET", file=sys.stderr)
    sys.exit(1)

if len(sys.argv) < 2:
    print("Usage: entra_refresh_token_password.py <refresh_token>", file=sys.stderr)
    sys.exit(1)

refresh_token = sys.argv[1]
if not refresh_token:
    print("Error: Refresh token argument not provided.", file=sys.stderr)
    sys.exit(1)

app = msal.ConfidentialClientApplication(
    client_id=client_id,
    client_credential=client_secret,
    authority=f"https://login.microsoftonline.com/{tenant_id}"
)

result = app.acquire_token_by_refresh_token(refresh_token, scopes=scope)

if not result or "access_token" not in result:
    error_summary = result.get('error_description', 'Refresh token is invalid or expired.')
    correlation_id = result.get('correlation_id', 'N/A')
    print(f"Error: Failed to acquire token using refresh token: {error_summary}", file=sys.stderr)
    print(f"Correlation ID: {correlation_id}.", file=sys.stderr)
    print(f"Full MSAL response for debugging: {result}", file=sys.stderr)
    sys.exit(1)

print(result["access_token"])