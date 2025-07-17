from fastapi import APIRouter



router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)



@router.post("/upload")
async def upload_document():
    return {"test":"test"}

@router.get("/")
async def get_document():
    return {"test":"test"}