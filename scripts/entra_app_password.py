#!/usr/bin/env python3
import os
import sys
from azure.identity import ClientSecretCredential
from azure.core.exceptions import AzureError

tenant_id = os.getenv("AZURE_TENANT_ID")
client_id = os.getenv("AZURE_CLIENT_ID")
client_secret = os.getenv("AZURE_CLIENT_SECRET")
scope = "https://ossrdbms-aad.database.windows.net/.default"

if not all([tenant_id, client_id, client_secret]):
    print("Error: One or more required environment variables are missing: "
          "AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET", file=sys.stderr)
    sys.exit(1)

try:
    credential = ClientSecretCredential(tenant_id, client_id, client_secret)
    token = credential.get_token(scope)
    if not token or not getattr(token, "token", None):
        print("Error: No access token returned from ClientSecretCredential.", file=sys.stderr)
        sys.exit(1)
    print(token.token)
except AzureError as e:
    print(f"Error: Failed to acquire token using ClientSecretCredential: {e}", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"Unexpected error: {e}", file=sys.stderr)
    sys.exit(1)