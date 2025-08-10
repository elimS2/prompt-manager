"""OAuth client setup for Google using Authlib."""
from typing import Optional
from flask import current_app
from authlib.integrations.flask_client import OAuth


_oauth: Optional[OAuth] = None


def get_oauth() -> OAuth:
    global _oauth
    if _oauth is not None:
        return _oauth

    oauth = OAuth(current_app)
    client_id = current_app.config.get('GOOGLE_CLIENT_ID')
    client_secret = current_app.config.get('GOOGLE_CLIENT_SECRET')
    redirect_uri = current_app.config.get('OAUTH_GOOGLE_REDIRECT_URI') or None

    oauth.register(
        name='google',
        client_id=client_id,
        client_secret=client_secret,
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile'},
        redirect_uri=redirect_uri,
    )

    _oauth = oauth
    return oauth


