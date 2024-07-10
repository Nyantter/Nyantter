from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
import asyncpg
import asyncio

from ...data import DataHandler

router = APIRouter()

nodeinfo_links = {
    "links": [
        {"rel": "http://nodeinfo.diaspora.software/ns/schema/2.0", "href": f"{DataHandler.server['url']}/nodeinfo/2.0"},
        {"rel": "http://nodeinfo.diaspora.software/ns/schema/2.1", "href": f"{DataHandler.server['url']}/nodeinfo/2.1"}
    ]
}

nodeinfo_2_0 = {
    "version": "2.0",
    "software": {
        "name": "nyantter",
        "version": "2024.06.26β",
    },
    "protocols": ["activitypub"],
    "services": {
        "inbound": [],
        "outbound": [
            "atom1.0",
            "rss2.0",
        ],
    },
    "openRegistratons": DataHandler.register["enableRegister"],
    "usage": {
        "users": {
            "total": 0,
            "activeHalfyear": None,
            "activeMonth": None,
        },
        "localPosts": 0,
        "localComments": 0,
    },
    "metadata": {
        "nodeName": DataHandler.server["name"],
        "nodeDescription": DataHandler.server["description"],
        "nodeAdmins": DataHandler.server["admins"],
        "maintainer": {
            "name": "Nyantter",
            "email": "nennneko5787+nyantter@gmail.com",
        }
    }
}

nodeinfo_2_1 = {
    "version": "2.1",
    "software": {
        "name": "nyantter",
        "version": "2024.06.26β",
        "repository": "https://github.com/Nyantter/Nyantter"
    },
    "protocols": ["activitypub"],
    "services": {
        "inbound": [],
        "outbound": [
            "atom1.0",
            "rss2.0",
        ],
    },
    "openRegistratons": DataHandler.register["enableRegister"],
    "usage": {
        "users": {
            "total": 0,
            "activeHalfyear": None,
            "activeMonth": None,
        },
        "localPosts": 0,
        "localComments": 0,
    },
    "metadata": {
        "nodeName": DataHandler.server["name"],
        "nodeDescription": DataHandler.server["description"],
        "nodeAdmins": DataHandler.server["admins"],
        "maintainer": {
            "name": "Nyantter",
            "email": "nennneko5787+nyantter@gmail.com",
        }
    }
}

async def get_db_connection():
    conn = await asyncpg.connect(
        host=DataHandler.database["host"],
        port=DataHandler.database["port"],
        user=DataHandler.database["user"],
        password=DataHandler.database["pass"],
        database=DataHandler.database["name"]
    )
    return conn

@router.get("/.well-known/nodeinfo")
async def get_nodeinfo():
    return JSONResponse(content=nodeinfo_links)

@router.get("/nodeinfo/2.0")
async def get_nodeinfo_2_0():
    conn = await asyncpg.connect(
        host=DataHandler.database["host"],
        port=DataHandler.database["port"],
        user=DataHandler.database["user"],
        password=DataHandler.database["pass"],
        database=DataHandler.database["name"]
    )

    prefix = DataHandler.database["prefix"]
    
    local_users_count = await conn.fetchval(f"SELECT COUNT(*) FROM {prefix}users WHERE domain IS NULL")
    nodeinfo_2_0["usage"]["users"]["total"] = local_users_count
    
    local_letter_count = await conn.fetchval(f"SELECT count(*) FROM {prefix}letters WhERE domain IS NULL")
    nodeinfo_2_0["usage"]["localPosts"] = local_letter_count
    
    return JSONResponse(content=nodeinfo_2_0, media_type="application/json; charset=utf-8")

@router.get("/nodeinfo/2.1")
async def get_nodeinfo_2_1():
    conn = await asyncpg.connect(
        host=DataHandler.database["host"],
        port=DataHandler.database["port"],
        user=DataHandler.database["user"],
        password=DataHandler.database["pass"],
        database=DataHandler.database["name"]
    )

    prefix = DataHandler.database["prefix"]
    
    local_users_count = await conn.fetchval(f"SELECT COUNT(*) FROM {prefix}users WHERE domain IS NULL")
    nodeinfo_2_1["usage"]["users"]["total"] = local_users_count
    
    local_letter_count = await conn.fetchval(f"SELECT count(*) FROM {prefix}letters WhERE domain IS NULL")
    nodeinfo_2_1["usage"]["localPosts"] = local_letter_count
    
    return JSONResponse(content=nodeinfo_2_1, media_type="application/json; charset=utf-8")
