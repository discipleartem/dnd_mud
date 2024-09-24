from dataclasses import dataclass
from creature import Creature


@dataclass
class Player(Creature):
    race: str