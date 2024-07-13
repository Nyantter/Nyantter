from fastapi import APIRouter, Response
from fastapi.responses import JSONResponse
from ...services import UserService
from ...data import DataHandler

router = APIRouter()


@router.get("/user/{user_id:int}")
async def user(user_id: int):
    user = await UserService.getUserFromID(user_id)
    if not user or user.domain:
        return Response(status_code=404)
    attachments = []
    for info in user.info:
        attachments.append(
            {
                "type": "PropertyValue",
                "name": info["name"],
                "value": info["value"],
            }
        )
    data = {
        "@context": [
            "https://www.w3.org/ns/activitystreams",
            "https://w3id.org/security/v1",
            {
                "manuallyApprovesFollowers": "as:manuallyApprovesFollowers",
                "toot": "http://joinmastodon.org/ns#",
                "discoverable": "toot:discoverable",
                "schema": "http://schema.org#",
                "PropertyValue": "schema:PropertyValue",
            },
        ],
        "followers": f"{DataHandler.server['url']}/user/{user.id}/followers",
        "following": f"{DataHandler.server['url']}/user/{user.id}/following",
        "icon": {"type": "Image", "url": user.icon_url},
        "id": f"{DataHandler.server['url']}/user/{user.id}",
        "inbox": f"{DataHandler.server['url']}/user/{user.id}/inbox",
        "name": user.display_name if user.display_name else user.handle,
        "outbox": f"{DataHandler.server['url']}/user/{user.id}/outbox",
        "preferredUsername": user.handle,
        "publicKey": {
            "id": f"{DataHandler.server['url']}/user/{user.id}#main-key",
            "owner": f"{DataHandler.server['url']}/user/{user.id}",
            "publicKeyPem": user.public_key,
            "type": "Key",
        },
        "attachment": attachments,
        "manuallyApprovesFollowers": False,
        "discoverable": None,
        "summary": user.description,
        "type": "Person",
        "url": f"{DataHandler.server['url']}/@{user.handle}",
    }
    return JSONResponse(
        content=data, media_type="application/activity+json; charset=utf8"
    )
