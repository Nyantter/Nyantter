from fastapi import APIRouter

router = APIRouter()

@router.get(
    "/api",
    summary="APIの生死確認"
)
async def apiIndex():
    """
    APIが生きているか確認します。
    """
    return {
        "status": "alive"
    }