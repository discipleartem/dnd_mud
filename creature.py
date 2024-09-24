from dataclasses import dataclass

@dataclass
class Creature:
    creature_type: str
    description: str
    size: str
    speed: int