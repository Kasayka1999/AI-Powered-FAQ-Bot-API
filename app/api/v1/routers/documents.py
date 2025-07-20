from fastapi import APIRouter, File, HTTPException, UploadFile

from app.api.dependencies import SessionDep, UserDep
from app.utils.s3 import download_file_from_s3, upload_file_to_s3



router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)


"""
@router.post("/upload")
async def upload_document(session: SessionDep, current_user: UserDep, file: UploadFile = File(...)):
    try:
        url = upload_file_to_s3(file.file, file.filename)
        return {"url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/download")
async def upload_document(session: SessionDep, curret_user: UserDep):
    current_user.
    try:
        url = download_file_from_s3(file.filename)
        return {"url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))"""


