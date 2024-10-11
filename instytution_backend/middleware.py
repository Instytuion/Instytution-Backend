from rest_framework_simplejwt.authentication import JWTAuthentication
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser

@database_sync_to_async
def get_user(token):
    try:
        jwt_auth = JWTAuthentication()
        validated_token = jwt_auth.get_validated_token(token)
        user = jwt_auth.get_user(validated_token)
        return user
    except Exception as e:
        print('error at get user inside middleware - ', str(e))
        return AnonymousUser()
    
class WSJWTAuthMiddleware:
    
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        token = None
        
        # Extract the token from subprotocols passed in the ws request.
        subprotocols = scope.get('subprotocols', [])
        
        if len(subprotocols) > 1 and subprotocols[0] == 'jwt':
            token = subprotocols[1] 

        if token:
            scope['user'] = await get_user(token)
        else:
            scope['user'] = AnonymousUser()

        return await self.inner(scope, receive, send)
