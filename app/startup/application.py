from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from app.domain_types.miscellaneous.exceptions import add_exception_handlers
from app.startup.client_api_keys import APIManager
from app.startup.router import router
from app.startup.user_seeder import Seeder
from starlette.middleware.base import BaseHTTPMiddleware

#################################################################

class ApiKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        api_key = request.headers.get("x-api-key")
        if not api_key:
            return Response("x-api-key header is missing", status_code=400)
        if api_key not in APIManager._api_keys:
            return Response("Invalid x-api-key", status_code=400)
        # Optionally, you can perform additional checks or actions with the api_key here
        response = await call_next(request)
        return response
    
def start():
    # Load API keys
    APIManager.load_api_keys()
    print('API KEYS ', APIManager._api_keys)

    Seeder.transfer_users_if_not_exists()
    # print('List of users Ids', Seeder._user_id)

    server = FastAPI()

    # Add CORS middleware
    server.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )

    server.add_middleware(ApiKeyMiddleware)

    server.include_router(router)

    return server

# def get_application():
#     APIManager.load_api_keys()
#     print('API KEYS ', APIManager._api_keys)
#     server = FastAPI()

#     # Add CORS middleware
#     server.add_middleware(
#         CORSMiddleware,
#         allow_origins=['*'],
#         allow_credentials=True,
#         allow_methods=['*'],
#         allow_headers=['*'],
#     )

#     server.include_router(router)

#     return server

# app = get_application()

app = start()
#################################################################
add_exception_handlers(app)
#################################################################
