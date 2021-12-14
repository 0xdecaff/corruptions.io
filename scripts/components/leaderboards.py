# TODO: evaluate if we even wanna keep leaderboards?
#       feels kinda pointless in a community & lore focused project

import collections
import json
from pathlib import Path
from typing import Dict, List

import jinja2 as j
import requests
import pydantic


class Corruption(pydantic.BaseModel):
    id: int
    lastTransferredBlock: int
    savedXP: int
    insight: int
    precise: float
    multiplier: float

    def save_markdown(self) -> Path:
        # DEBT: TODO: save this as json instead? learned about the json data capabilities after first impl
        site_dir = Path(__file__).parent.parent.parent
        new_file_path = site_dir / "site/content/directory" / f"{self.id}.md"

        env = j.Environment(
            loader=j.FileSystemLoader(site_dir / "templates", encoding="utf8"),
            autoescape=j.select_autoescape(),
        )
        template = env.get_template("corruption.md")
        generated = template.render(**self.dict())
        with open(new_file_path, mode="w") as f:
            f.write(generated)
        return new_file_path


def get_corruptions() -> List[Corruption]:
    resp = requests.get("https://corruptions-scores.vercel.app/api/all-scores")
    resp.raise_for_status()

    corruptions = resp.json()
    return [Corruption(**x) for x in corruptions]


class Team(pydantic.BaseModel):
    name: str
    insight: float


class Division(pydantic.BaseModel):
    name: str
    teams: List[Team]


def teams_from_scorecard(scorecard: Dict[str, int]) -> List[Team]:
    return [Team(name=k, insight=v) for k, v in scorecard.items() if k != ""]


def download() -> None:
    """Fetch & save json download all corruption scores for leaderboards"""
    metadata_file_path = Path(__file__).parent.parent.parent / "site/data/metadata.json"
    with open(metadata_file_path, mode="r") as f:
        metadata = json.load(f)

    corruptions = get_corruptions()
    insight_by_phrase = collections.defaultdict(int)
    insight_by_hidden = collections.defaultdict(int)
    insight_by_border = collections.defaultdict(int)
    insight_by_corruptor = collections.defaultdict(int)
    insight_by_checker = collections.defaultdict(int)
    for c in corruptions:
        _ = c.save_markdown()
        if str(c.id) not in metadata:
            continue
        m = metadata[str(c.id)]
        insight_by_phrase[m.get("phrase")] += c.insight
        insight_by_hidden[m.get("hiddenAttribute")] += c.insight
        insight_by_border[m.get("border")] += c.insight
        insight_by_corruptor[m.get("corruptor")] += c.insight
        insight_by_checker[m.get("checker")] += c.insight

    divisions = [
        Division(name="📰 phrases", teams=teams_from_scorecard(insight_by_phrase)),
        Division(name="🕵 hidden", teams=teams_from_scorecard(insight_by_hidden)),
        Division(name="🖼 borders", teams=teams_from_scorecard(insight_by_border)),
        Division(name="👾 corruptors", teams=teams_from_scorecard(insight_by_corruptor)),
        Division(name="🏁 checkers", teams=teams_from_scorecard(insight_by_checker)),
    ]

    divisions_file_path = Path(__file__).parent.parent.parent / "site/data/divisions.json"
    with open(divisions_file_path, mode="w") as f:
        json.dump({"divisions": [d.dict() for d in divisions]}, f, indent=2)
