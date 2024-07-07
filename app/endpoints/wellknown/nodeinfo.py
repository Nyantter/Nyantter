from fastapi import APIRouter
from fastapi.responses import JSONResponse

from ...data import DataHandler

import asyncpg

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
        "openRegistratons": DataHandler.register["enableRegister"],
	},
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
        "openRegistratons": DataHandler.register["enableRegister"],
	},
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

@router.get("/.well-known/nodeinfo")
async def get_nodeinfo():
    return JSONResponse(content=nodeinfo_links)

@router.get("/nodeinfo/2.0")
async def get_nodeinfo_2_0():
    return JSONResponse(content=nodeinfo_2_0)

@router.get("/nodeinfo/2.1")
async def get_nodeinfo_2_1():
    return JSONResponse(content=nodeinfo_2_1)
