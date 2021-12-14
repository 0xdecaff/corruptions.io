import datetime
import json
from pathlib import Path

import requests
import pydantic


class DeviationInfo(pydantic.BaseModel):
    id: str
    created: datetime.datetime
    index: int
    name: str
    contractAddress: str
    extraData: int


def download() -> None:
    """Fetch & save json for all deviation contracts registered on-chain."""

    query = """
    {
    deviationInfos(first: 64) {
        id
        created
        index
        name
        contractAddress
        extraData
    }
    }
    """
    request = requests.post(
        "https://api.thegraph.com/subgraphs/name/0xdecaff/deviations" "",
        json={"query": query},
    )
    request.raise_for_status()
    # TODO: remove dupes from multiple setValue calls
    deviations = request.json().get("data", {}).get("deviationInfos", [])
    deviations = sorted(deviations, key=lambda x: x.get("created"))
    deviations = [DeviationInfo(**x).dict() for x in deviations]
    deviation_registry_filepath = (
        Path(__file__).parent.parent.parent / "site/data/deviation_registry.json"
    )
    with open(deviation_registry_filepath, mode="w") as f:
        json.dump({"deviations": deviations}, f, indent=2, default=str)
