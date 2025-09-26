#!/usr/bin/env python3
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