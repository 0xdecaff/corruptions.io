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
    b64: bool = False

    @classmethod
    def from_json(cls, payload: dict):
        m = Message(**payload)
        contains_b64 = False
        message = m.message.split(" ")
        for word in message:
            if (len(word) > 5 and word.endswith("=")) or len(word) > 30:
                contains_b64 = True
        m.b64 = contains_b64
        return m


def download() -> None:
    """Fetch & save json for all on-chain messages"""

    # TODO: read existing messages from disk, get only latest messages, and update existing data
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
    request = requests.post(
        "https://api.thegraph.com/subgraphs/name/shahruz/corruptions",
        json={"query": query},
    )
    request.raise_for_status()
    messages = request.json().get("data", {}).get("messages", [])
    messages = sorted(messages, key=lambda x: x.get("createdAt"))
    messages = [Message.from_json(x).dict() for x in messages]
    messages_filepath = Path(__file__).parent.parent.parent / "site/data/messages.json"
    with open(messages_filepath, mode="w") as f:
        json.dump({"messages": messages}, f, indent=2, default=str)
