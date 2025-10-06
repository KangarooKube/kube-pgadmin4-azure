#!/usr/bin/env python3
"""
Script to acquire an Entra ID access token for Azure Database for PostgreSQL using
Azure Workload Identity (azure.identity.WorkloadIdentityCredential).

This script relies on the Kubernetes pod being configured for Azure Workload Identity
(or another OIDC-based federated credential) so that the Azure SDK can obtain a token
without a client secret.

Environment Variables (optional / provider specific):
    AZURE_CLIENT_ID        - (optional) client id to identify the federated credential
    AZURE_TENANT_ID        - (optional) tenant id for authority resolution
    AZURE_FEDERATED_TOKEN_FILE - (optional) path set by some providers

Note: In many workload identity setups no env vars are required; the platform injects
the required metadata for the SDK.

Usage:
    entra_workload_identity_password.py

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
    General exceptions:
        Any unexpected errors will be printed and cause a non-zero exit.
"""
import sys
from azure.identity import WorkloadIdentityCredential
from azure.core.exceptions import AzureError

# The scope for Azure Database PostgreSQL
scope = "https://ossrdbms-aad.database.windows.net/.default"

try:
    # Create the credential using environment/platform-provided configuration
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