import re
from typing import Optional

from fastapi import APIRouter, Response

from ...data import DataHandler
from ...services import UserService

router = APIRouter()


@router.get("/.well-known/webfinger")
async def webfinger(resource: Optional[str] = ""):
    if not resource:
        return Response(status_code=400)

    # 正規表現パターン
    pattern = r"acct:(.*)@(.*)"

    # 正規表現にマッチする部分を探す
    match = re.match(pattern, resource)

    if match:
        username = match.group(1)
        domain = match.group(2)
        if domain != DataHandler.server["remoteDomain"]:
            return Response(status_code=404)
        user = await UserService.getUser(
            username,
            domain=None,
        )
        if not user:
            return Response(status_code=404)
        return {
            "subject": f"acct:{user.handle}@{DataHandler.server['remoteDomain']}",
            "links": [
                {
                    "rel": "self",
                    "type": "application/activity+json",
                    "href": f"{DataHandler.server['url']}/user/{user.id}",
                },
                {
                    "rel": "http://webfinger.net/rel/profile-page",
                    "type": "text/html",
                    "href": f"{DataHandler.server['url']}/@{user.handle}",
                },
            ],
        }
    else:
        return Response(status_code=404)
