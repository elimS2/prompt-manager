"""Business logic for user management and Google OAuth upsert and access policy."""
from datetime import datetime
from typing import Optional, Dict, Any

from flask import current_app
from app.models import User, db
from app.repositories.user_repository import UserRepository
from app.repositories.allowlist_repository import AllowlistRepository


class UserService:
    def __init__(self, user_repository: Optional[UserRepository] = None,
                 allowlist_repository: Optional[AllowlistRepository] = None) -> None:
        self.user_repository = user_repository or UserRepository()
        self.allowlist_repository = allowlist_repository or AllowlistRepository()

    def find_or_create_from_google(self, profile: Dict[str, Any], allowed_hd: Optional[str] = None) -> User:
        """
        Upsert user from Google userinfo profile.

        Expected profile keys: 'sub', 'email', 'name', 'picture', optionally 'hd'.
        """
        google_sub = profile.get('sub')
        email = (profile.get('email') or '').lower()
        name = profile.get('name')
        picture = profile.get('picture')
        hosted_domain = profile.get('hd')

        if not google_sub or not email:
            raise ValueError("Google profile must contain 'sub' and 'email'")

        if allowed_hd and hosted_domain and hosted_domain.lower() != allowed_hd.lower():
            raise PermissionError("Google account domain is not allowed")

        user = self.user_repository.get_by_google_sub(google_sub)
        if not user:
            # First-time login; reconcile by email if exists
            user = self.user_repository.get_by_email(email)

        is_new_user = False
        if user:
            user.google_sub = google_sub
            user.email = email
            user.name = name
            user.picture_url = picture
            user.updated_at = datetime.utcnow()
        else:
            user = User(
                google_sub=google_sub,
                email=email,
                name=name,
                picture_url=picture,
            )
            db.session.add(user)
            is_new_user = True

        # Determine access policy and status
        access_policy = (current_app.config.get('ACCESS_POLICY') or 'allowlist_then_approval').lower()
        admins = set((current_app.config.get('ADMINS') or []))

        is_admin_email = email in admins
        allowlist_entry = self.allowlist_repository.get_by_email(email)
        in_allowlist = allowlist_entry is not None

        # Do not downgrade disabled users implicitly
        if user.status == 'disabled':
            pass
        elif is_admin_email:
            user.role = 'admin'
            user.status = 'active'
        elif in_allowlist:
            user.status = 'active'
            # Optional: respect default_role on first activation
            if is_new_user and allowlist_entry and allowlist_entry.default_role and user.role != 'admin':
                user.role = allowlist_entry.default_role
        else:
            # Not allowlisted
            if is_new_user:
                # First-time login, set pending according to policy
                if access_policy in ('allowlist_strict', 'allowlist_then_approval'):
                    user.status = 'pending'
            else:
                # Existing users: respect prior approval; do not downgrade active to pending
                # If previously pending, keep pending
                # If previously active, keep active
                # No change needed
                pass

        user.last_login_at = datetime.utcnow()
        db.session.commit()
        return user

    def approve_user(self, user_id: int, approver_user_id: Optional[int] = None, role: Optional[str] = None) -> User:
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        if role:
            user.role = role
        user.status = 'active'
        user.approved_by_user_id = approver_user_id
        user.approved_at = datetime.utcnow()
        db.session.commit()
        return user

    def disable_user(self, user_id: int) -> User:
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        user.status = 'disabled'
        db.session.commit()
        return user

    def list_pending_users(self):
        return self.user_repository.list_by_status('pending')

 