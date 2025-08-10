"""Business logic for user management and Google OAuth upsert."""
from datetime import datetime
from typing import Optional, Dict, Any

from app.models import User, db
from app.repositories.user_repository import UserRepository


class UserService:
    def __init__(self, user_repository: Optional[UserRepository] = None) -> None:
        self.user_repository = user_repository or UserRepository()

    def find_or_create_from_google(self, profile: Dict[str, Any], allowed_hd: Optional[str] = None) -> User:
        """
        Upsert user from Google userinfo profile.

        Expected profile keys: 'sub', 'email', 'name', 'picture', optionally 'hd'.
        """
        google_sub = profile.get('sub')
        email = profile.get('email')
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

        user.last_login_at = datetime.utcnow()
        db.session.commit()
        return user

 