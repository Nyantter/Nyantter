from fastapi import APIRouter
from fastapi.responses import JSONResponse

from ...data import DataHandler

router = APIRouter()

nodeinfo_links = {
    "links": [
        {"rel": "http://nodeinfo.diaspora.software/ns/schema/2.0", "href": "/nodeinfo/2.0"},
        {"rel": "http://nodeinfo.diaspora.software/ns/schema/2.1", "href": "/nodeinfo/2.1"}
    ]
}

nodeinfo_2_0 = {
    "version": "2.0",
    "software": {
        "name": "nyantter",
        "version": "2024.06.26β",
        "repository": "https://github.com/Nyantter/Nyantter"
    },
    # 他の必要なフィールドを追加
}

nodeinfo_2_1 = {
    "version": "2.1",
    "software": {
        "name": "nyantter",
        "version": "2024.06.26β",
        "repository": "https://github.com/Nyantter/Nyantter"
    },
    # 他の必要なフィールドを追加
}

@router.get("/.well-known/nodeinfo")
async def get_nodeinfo():
    return JSONResponse(content=nodeinfo_links)

@router.get("/nodeinfo/2.0")
async def get_nodeinfo_2_0():
    return JSONResponse(content=nodeinfo_2_0)

@router.get("/nodeinfo/2.1")
async def get_nodeinfo_2_1():
    return JSONResponse(content=nodeinfo_2_1)
