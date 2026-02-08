from accounts.models import User


def get_or_create_local_user_by_sub(*, sub: str, email: str | None = None, name: str | None = None) -> User:
    user = User.objects.filter(cognito_sub=sub).first()
    if user is not None:
        changed = False
        if email and user.email != email:
            user.email = email
            changed = True
        if name and user.name != name:
            user.name = name
            changed = True
        if changed:
            user.save(update_fields=["email", "name", "updated_at"])
        return user

    if not email:
        email = f"{sub}@example.invalid"
    if not name:
        name = ""

    user = User.objects.create(email=email, name=name, cognito_sub=sub)
    return user


def get_current_local_user(request) -> User:
    sub = getattr(request.user, "sub", None)
    if not sub:
        raise ValueError("request.user.sub is missing")
    return get_or_create_local_user_by_sub(sub=sub, email=getattr(request.user, "email", None))
