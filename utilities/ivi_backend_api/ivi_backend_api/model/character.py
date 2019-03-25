from dataclasses import dataclass
from dataclasses_json import dataclass_json


@dataclass_json  # TODO: remove it (((((
@dataclass
class Character:
    name: str
    universe: str
    education: str
    weight: float
    height: int
    identity: str
    other_aliases: str
