from datetime import datetime, timedelta
from typing import Optional
import jwt
from jwt.exceptions import InvalidTokenError


class JWTHandler:
    """Handle JWT token creation and validation"""

    def __init__(self, secret_key: str, algorithm: str = "HS256", expiration_hours: int = 24):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.expiration_hours = expiration_hours

    def create_token(self, email: str) -> str:
        """Create a JWT token for a user"""
        expiration = datetime.utcnow() + timedelta(hours=self.expiration_hours)
        payload = {
            "sub": email,
            "exp": expiration,
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, token: str) -> Optional[str]:
        """
        Verify a JWT token and return the email if valid.
        Returns None if token is invalid or expired.
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            email: str = payload.get("sub")
            return email
        except InvalidTokenError:
            return None
