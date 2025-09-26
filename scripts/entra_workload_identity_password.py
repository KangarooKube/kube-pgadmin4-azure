#!/usr/bin/env python3
import sys
from azure.identity import WorkloadIdentityCredential
from azure.core.exceptions import AzureError

# The scope for Azure Database for PostgreSQL
scope = "https://ossrdbms-aad.database.windows.net/.default"

try:
    # Create the credential using environment variables set by Azure Workload Identity
    credential = WorkloadIdentityCredential()
    # Request the access token for the PostgreSQL scope
    token = credential.get_token(scope)
    if not token or not getattr(token, "token", None):
        print("Error: No access token returned from WorkloadIdentityCredential.", file=sys.stderr)
        sys.exit(1)
    print(token.token)
except AzureError as e:
    print(f"Error: Failed to acquire token using WorkloadIdentityCredential: {e}", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"Unexpected error: {e}", file=sys.stderr)
    sys.exit(1)