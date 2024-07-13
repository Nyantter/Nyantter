from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get("/api", response_class=JSONResponse, summary="APIの生死確認")
async def apiIndex():
    """
    APIが生きているか確認します。
    """
    return {"status": "alive"}
