import datetime
import json
from pathlib import Path

import requests
import pydantic


class Message(pydantic.BaseModel):
    id: str
    createdAt: datetime.datetime
    channel: str
    message: str
    chapter: str = ""
    prefix: str = ""
    image: str = ""


def download() -> None:
    """Fetch & save json for all on-chain messages"""

    # TODO: get only latest messages
    query = """
    {
    messages(first: 250) {
        id
        createdAt
        channel
        message
    }
    }
    """
    # Get existing messages, and only add the new ones
    messages_filepath = Path(__file__).parent.parent.parent / "site/data/messages.json"
    with open(messages_filepath, mode="r") as f:
        messages = json.load(f)
        messages = messages["messages"]

    existing_messages = {k.get("id") for k in messages}

    request = requests.post(
        "https://api.thegraph.com/subgraphs/name/shahruz/corruptions",
        json={"query": query},
    )
    request.raise_for_status()
    # TODO: sort in db
    new_messages = request.json().get("data", {}).get("messages", [])
    new_messages = sorted(new_messages, key=lambda x: x.get("createdAt"))
    new_messages = [Message(**x).dict() for x in new_messages if x.get("id") not in existing_messages]
    with open(messages_filepath, mode="w") as f:
        json.dump({"messages": messages + new_messages}, f, indent=2, default=str)
