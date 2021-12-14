import datetime
import json
from pathlib import Path

import requests
import pydantic


class CompendiumRecord(pydantic.BaseModel):
    id: str
    created: datetime.datetime
    topic: str
    content: str


def download() -> None:
    """Fetch & save json for all compendium records currently registered"""

    # TODO: when entry count gets high, bump this or refactor to only fetch latest
    query = """
    {
    records(first: 50) {
        id
        created
        topic
        content
    }
    revokes(first: 50) {
        id
        created
        topic
    }
    }
    """
    request = requests.post(
        "https://api.thegraph.com/subgraphs/name/0xdecaff/compendium",
        json={"query": query},
    )
    request.raise_for_status()

    # TODO: offload sorting to the query above, too lazy to look it up rn
    records = request.json().get("data", {}).get("records", [])
    records = sorted(records, key=lambda x: x.get("created"))

    revokes = request.json().get("data", {}).get("revokes", [])
    revokes = sorted(revokes, key=lambda x: x.get("created"))
    revokes = {x.get("topic") for x in revokes}

    processed_records = {}
    for x in records:
        topic = x.get("topic")
        # HACK: just revoke something if its part of the revoke set, regardless of order
        if topic in revokes:
            del processed_records[topic]
        processed_records[topic] = CompendiumRecord(**x).dict()

    compendium_filepath = Path(__file__).parent.parent.parent / "site/data/compendium.json"
    with open(compendium_filepath, mode="w") as f:
        json.dump(
            {"records": list(processed_records.values())}, f, indent=2, default=str
        )
