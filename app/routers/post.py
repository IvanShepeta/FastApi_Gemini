from fastapi import APIRouter
from starlette import status

from app.schemas import ChatRequest

router = APIRouter(
    prefix="/requests",
    tags=['Requests'],
)

# @router.get("/")
# def get_my_requests(request: Request):
#     user_ip_address = request.client.host
#     print(f"{user_ip_address=}")
#     user_requests = get_user_requests(ip_address=user_ip_address)
#     return jsonable_encoder(user_requests)
#
#
# @router.post("/")
# def send_prompt(
#         request: Request,
#         prompt: str = Body(embed=True),
# ):
#     user_ip_address = request.client.host
#     answer = get_answer_from_gemini(prompt)
#     add_request_data(
#         ip_address=user_ip_address,
#         prompt=prompt,
#         response=answer,
#     )
#     return {"answer": answer}