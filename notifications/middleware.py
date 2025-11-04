from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware

@database_sync_to_async
def get_user_from_token(token_key: str):
    from django.contrib.auth.models import AnonymousUser  # ایمپورت داخل متد
    from rest_framework.authtoken.models import Token
    """
    بررسی توکن و گرفتن کاربر
    """
    try:
        token = Token.objects.get(key=token_key)
        return token.user
    except Token.DoesNotExist:
        return AnonymousUser()

class TokenAuthMiddleware(BaseMiddleware):
    """
    Middleware امن برای احراز هویت WebSocket با توکن DRF.
    توکن باید در query string به شکل: ?token=xxxx باشد.
    """

    async def __call__(self, scope, receive, send):
        from django.contrib.auth.models import AnonymousUser  # ایمپورت داخل متد
        query_string = scope.get("query_string", b"").decode()
        token_key = None

        # استخراج توکن از query string
        try:
            params = dict(x.split('=') for x in query_string.split("&") if "=" in x)
            token_key = params.get("token")
        except Exception:
            token_key = None

        scope["user"] = await get_user_from_token(token_key) if token_key else AnonymousUser()
                # پرینت واضح برای debug
        if scope["user"].is_authenticated:
            print(f"[Middleware] ✅ Authenticated user: {scope['user'].username} (id={scope['user'].id})")
        else:
            print(f"[Middleware] ❌ AnonymousUser (token={token_key})")
        return await super().__call__(scope, receive, send)
