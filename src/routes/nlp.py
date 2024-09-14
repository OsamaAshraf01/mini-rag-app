from fastapi import APIRouter

nlp_router = APIRouter(
    prefix='/api/v1/nlp'
)

@nlp_router.post("/index/push/{project_id}")
def push(project_id):
    pass