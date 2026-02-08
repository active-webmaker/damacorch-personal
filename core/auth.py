from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Any, Optional

import requests
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from jose import jwt
from jose.exceptions import JWTError
from rest_framework import authentication
from rest_framework import exceptions


@dataclass(frozen=True)
class CognitoUser:
    sub: str
    email: Optional[str] = None

    @property
    def is_authenticated(self) -> bool:
        return True


_jwks_cache: dict[str, Any] | None = None
_jwks_cache_expires_at: float = 0


def _get_jwks() -> dict[str, Any]:
    global _jwks_cache, _jwks_cache_expires_at

    now = time.time()
    if _jwks_cache is not None and now < _jwks_cache_expires_at:
        return _jwks_cache

    region = getattr(settings, "COGNITO_REGION", "")
    user_pool_id = getattr(settings, "COGNITO_USER_POOL_ID", "")
    if not region or not user_pool_id:
        raise exceptions.AuthenticationFailed(_("Cognito settings are not configured."))

    url = f"https://cognito-idp.{region}.amazonaws.com/{user_pool_id}/.well-known/jwks.json"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    _jwks_cache = resp.json()
    _jwks_cache_expires_at = now + 3600
    return _jwks_cache


class CognitoJWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth = authentication.get_authorization_header(request).decode("utf-8")
        if not auth:
            return None
        if not auth.lower().startswith("bearer "):
            return None

        token = auth.split(" ", 1)[1].strip()

        if getattr(settings, "COGNITO_USE_DUMMY", False):
            sub = token
            email = None
            if token.startswith("dummy-"):
                email = token.removeprefix("dummy-")
            user = CognitoUser(sub=sub, email=email)
            return (user, token)

        try:
            jwks = _get_jwks()
            issuer = f"https://cognito-idp.{settings.COGNITO_REGION}.amazonaws.com/{settings.COGNITO_USER_POOL_ID}"
            claims = jwt.decode(
                token,
                jwks,
                algorithms=["RS256"],
                audience=settings.COGNITO_APP_CLIENT_ID or None,
                issuer=issuer,
                options={"verify_aud": bool(settings.COGNITO_APP_CLIENT_ID)},
            )
        except (requests.RequestException, JWTError) as exc:
            raise exceptions.AuthenticationFailed(_("Invalid token.")) from exc

        sub = claims.get("sub")
        if not sub:
            raise exceptions.AuthenticationFailed(_("Token missing sub claim."))

        email = claims.get("email")
        user = CognitoUser(sub=sub, email=email)
        return (user, token)
