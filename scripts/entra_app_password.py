#!/usr/bin/env python3
"""
Script to acquire an Entra ID access token for Azure Database for PostgreSQL using
Client Credentials (azure.identity.ClientSecretCredential).

This script reads tenant/client credentials from environment variables and requests
an access token for the PostgreSQL scope.

Environment Variables (required):
    AZURE_TENANT_ID     - Azure tenant (directory) id
    AZURE_CLIENT_ID     - Service principal / app client id
    AZURE_CLIENT_SECRET - Service principal / app client secret

Usage:
    entra_app_password.py

Arguments:
    None

Output:
    Prints the acquired access token to stdout on success.
    Prints error details to stderr and exits with non-zero status on failure.

Dependencies:
    azure-identity
    azure-core

Exceptions:
    AzureError:
        Raised by azure.core.exceptions when token acquisition fails.
    SystemExit:
        Raised when the script exits with non-zero status on failure.
    General exceptions:
        Any unexpected errors will be printed and cause a non-zero exit.
"""
import os
import sys
from azure.identity import ClientSecretCredential
from azure.core.exceptions import AzureError

# The scope for Azure Database for PostgreSQL
scope = "https://ossrdbms-aad.database.windows.net/.default"

tenant_id = os.getenv("AZURE_TENANT_ID")
client_id = os.getenv("AZURE_CLIENT_ID")
client_secret = os.getenv("AZURE_CLIENT_SECRET")

if not all([tenant_id, client_id, client_secret]):
    print(
        "Error: One or more required environment variables are missing: "
        "AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET",
        file=sys.stderr,
    )
    sys.exit(1)

try:
    credential = ClientSecretCredential(tenant_id=tenant_id, client_id=client_id, client_secret=client_secret)
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