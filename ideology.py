from dataclasses import dataclass

@dataclass
class Ideology:
    vector: str       # E.g., 'law', 'chaotic', 'neutral'
    name: str         # Full name of the ideology
    short_name: str   # Abbreviated name (e.g., 'lg' for "Lawful Good")
    description: str  # Detailed description of the ideology

# Example instance
lawful_good = Ideology(
    vector='law',
    name='Законно-Добрые',
    short_name='lg',
    description=(
                    """
                    
                    """
    )
)

IDEOLOGY = []
IDEOLOGY_DICT = {ideology.short_name: ideology for ideology in IDEOLOGY}