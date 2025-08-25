"""Authentication controller: Google OAuth login, callback, logout."""
from flask import Blueprint, redirect, url_for, request, session, current_app, flash, render_template
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

from app.models import User
from app.services.oauth_service import get_oauth
from app.services.user_service import UserService


auth_bp = Blueprint('auth', __name__)
login_manager = LoginManager()
user_service = UserService()


@login_manager.user_loader
def load_user(user_id: str):
    try:
        return User.get_by_id(int(user_id))
    except Exception:
        return None


@auth_bp.route('/auth/login')
def login():
    oauth = get_oauth()
    next_url = request.args.get('next') or url_for('prompt.index')
    session['next_url'] = next_url
    # Prefer configured redirect URI if provided; fallback to dynamic
    configured = current_app.config.get('OAUTH_GOOGLE_REDIRECT_URI')
    redirect_uri = configured or url_for('auth.callback', _external=True)
    if configured:
        current_app.logger.info('OAuth login: using configured redirect_uri=%s', configured)
    else:
        current_app.logger.info('OAuth login: using dynamic redirect_uri=%s', redirect_uri)
    current_app.logger.info('OAuth login initiated. next_url=%s', next_url)
    return oauth.google.authorize_redirect(redirect_uri=redirect_uri)


@auth_bp.route('/auth/callback')
def callback():
    oauth = get_oauth()
    # Enforce state validation and handle mismatches gracefully
    try:
        token = oauth.google.authorize_access_token()
    except Exception as exc:
        current_app.logger.warning('OAuth callback state/token error: %s', exc)
        flash('Login session expired. Please try again.', 'warning')
        return redirect(url_for('auth.pending'))
    if not token:
        flash('Authorization failed', 'error')
        return redirect(url_for('auth.pending'))

    current_app.logger.info('OAuth callback: token received successfully.')
    userinfo = oauth.google.userinfo()
    profile = userinfo.json() if hasattr(userinfo, 'json') else userinfo

    allowed_hd = current_app.config.get('OAUTH_GOOGLE_ALLOWED_HD')
    try:
        user = user_service.find_or_create_from_google(profile, allowed_hd=allowed_hd)
    except PermissionError:
        flash('This Google account domain is not allowed', 'error')
        return redirect(url_for('prompt.index'))
    except Exception as exc:
        current_app.logger.exception('OAuth callback processing failed: %s', exc)
        flash('Failed to sign in with Google', 'error')
        return redirect(url_for('auth.pending'))
    # Enforce access status
    if user.status == 'pending':
        current_app.logger.info('User pending approval. user_id=%s', getattr(user, 'id', None))
        flash('Access not granted yet. Please wait for administrator approval.', 'warning')
        # Store last attempted email in session to show on pending page (no logging)
        session['last_pending_email'] = user.email
        return redirect(url_for('auth.pending'))
    if user.status == 'disabled':
        current_app.logger.info('User is disabled. user_id=%s', getattr(user, 'id', None))
        flash('Your account is disabled. Contact administrator.', 'error')
        session['last_pending_email'] = user.email
        return redirect(url_for('auth.pending'))

    login_user(user)
    current_app.logger.info('User logged in. user_id=%s', getattr(user, 'id', None))
    dest = session.pop('next_url', None) or url_for('prompt.index')
    return redirect(dest)


@auth_bp.route('/auth/logout')
@login_required
def logout():
    current_app.logger.info('User logged out. user_id=%s', getattr(current_user, 'id', None))
    # Clear Flask-Login session
    logout_user()
    # Clear server-side session data
    session.clear()
    # Build redirect response and explicitly delete auth cookies
    response = redirect(url_for('prompt.index'))
    session_cookie_name = current_app.config.get('SESSION_COOKIE_NAME', 'session')
    remember_cookie_name = current_app.config.get('REMEMBER_COOKIE_NAME', 'remember_token')
    response.delete_cookie(session_cookie_name, path='/' )
    response.delete_cookie(remember_cookie_name, path='/' )
    flash('Signed out', 'info')
    return response


@auth_bp.route('/access/pending')
def pending():
    """Show pending/disabled access page."""
    # Keep it minimal; show a neutral message and last attempted email if present
    return render_template('access/pending.html', last_email=session.get('last_pending_email'))

