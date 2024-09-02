from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from app.modules.data_sync.data_synchronizer import DataSynchronizer
from app.startup.router import router
from starlette.middleware.base import BaseHTTPMiddleware

###############################################################################

class ClientAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        api_key = request.headers.get("x-api-key")
        if not api_key:
            return Response("x-api-key header is missing", status_code=400)
        client_app = DataSynchronizer._api_keys_cache.get(api_key)
        if not client_app:
            return Response("Invalid x-api-key", status_code=400)
        request.state.client_name = client_app['ClientName']
        request.state.client_code = client_app['ClientCode']
        request.state.is_privileged = True if client_app['IsPrivileged'] == 0 else False
        # Optionally, you can perform additional checks or actions with the api_key here
        response = await call_next(request)
        return response
