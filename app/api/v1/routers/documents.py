from fastapi import APIRouter, UploadFile



router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)



@router.post("/upload")
async def upload_document(file: UploadFile):
    contents = await file.read()
    
    return {"filename":file.filename, "type": file.content_type}

@router.get("/")
async def get_document():
    return {"test":"test"}