"""
A utility script to manually run after a new deviation drop mints out
and we have the deviated IDs indexed from the blockchain already.

TODO: eventually do this automatically in CD pipeline
"""

import json
import requests
from pathlib import Path
from typing import List


def download_deviations(ids: List[int]):
    for id in ids:
        resp = requests.get(
            f"https://corruption-api.vercel.app/api/corruptionImage/{id}"
        )
        new_file_path = (
            Path(__file__).parent / "site/static/assets/corruptions" / f"{id}.svg"
        )
        if new_file_path.exists():
            continue

        # TODO: When the API supports returning PNGs, modify to support that here
        svg = resp.text.replace('<div style="width: 500px;">', "").replace("</div>", "")
        with open(new_file_path, mode="w") as f:
            f.write(svg)
        print(f"saved {new_file_path}")


all_ids = range(4196)
deviation_filepath = Path(__file__).parent / "site/data/deviations.json"
with open(deviation_filepath, mode="r") as f:
    deviations = json.load(f)


download_deviations([4144])
