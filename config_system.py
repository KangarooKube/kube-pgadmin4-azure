import os

client_id = os.getenv('AZURE_CLIENT_ID')
client_secret = os.getenv('AZURE_CLIENT_SECRET')
tenant_id = os.getenv('AZURE_TENANT_ID')
if not all([client_id, client_secret, tenant_id]):
    raise Exception("Error: One or more required Entra environment variables are missing: "
                    "AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID")

group_id = os.getenv('OAUTH2_GROUP_ID')

enable_refresh_token = os.getenv('ENABLE_SERVER_PASS_EXEC_REFRESH_TOKEN', 'false').lower() == 'true'
base_scope = "openid email profile"
scope = f"{base_scope}{' offline_access' if enable_refresh_token else ''}"

SESSION_DIGEST_METHOD = 'hashlib.sha256'

MASTER_PASSWORD_HOOK = './master_password_hook.py'

ENABLE_SERVER_PASS_EXEC_REFRESH_TOKEN = enable_refresh_token

AUTHENTICATION_SOURCES = ['oauth2']

ENABLE_SERVER_PASS_EXEC_CMD = True

PGADMIN_CONFIG_SERVER_MODE = True

OAUTH2_CONFIG = [
  {
    "OAUTH2_NAME": "entra",
    "OAUTH2_DISPLAY_NAME": "EntraID",
    "OAUTH2_AUTO_CREATE_USER": "True",
    "OAUTH2_SCOPE": scope,
    "OAUTH2_CLIENT_ID": client_id,
    "OAUTH2_CLIENT_SECRET": client_secret,
    "OAUTH2_TOKEN_URL": f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token",
    "OAUTH2_AUTHORIZATION_URL": f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/authorize",
    "OAUTH2_API_BASE_URL": "https://graph.microsoft.com/v1.0",
    "OAUTH2_USERINFO_ENDPOINT": "https://graph.microsoft.com/oidc/userinfo",
    "OAUTH2_SERVER_METADATA_URL": f"https://login.microsoftonline.com/{tenant_id}/v2.0/.well-known/openid-configuration",
    "OAUTH2_BUTTON_NAME": "Login with Entra ID",
    "OAUTH2_ICON": "fa-microsoft",
    "OAUTH2_BUTTON_COLOR": "#0078D4",
    **({"OAUTH2_ADDITIONAL_CLAIMS": {"groups": [f"{group_id}"]}} if group_id else {})
  }
]
