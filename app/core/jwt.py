from datetime import datetime, timedelta, timezone
from jose import jwt

# Secret key used to sign tokens
# In real projects it should come from environment variables
SECRET_KEY = "super-secret-key"

# Algorithm used for token signing
ALGORITHM = "HS256"

# Token lifetime in minutes
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: dict):
    """
    Creates JWT access token.
    Accepts payload data (usually user id / role).
    """

    # Copy payload so original dict is not modified
    to_encode = data.copy()

    # Calculate token expiration time
    expire = datetime.now(timezone.utc) + timedelta(
    minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
   
    # Add expiration claim to payload
    to_encode.update({"exp": expire})

    # Encode payload into JWT token
    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    return encoded_jwt


def verify_access_token(token: str):
    """
    Decodes JWT token and validates signature.
    Raises error if token is invalid or expired.
    """

    payload = jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHM],
    )

    return payload