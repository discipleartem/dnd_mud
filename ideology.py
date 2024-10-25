@dataclass
class Ideology:
    vector: str       # E.g., 'law', 'chaotic', 'neutral'
    name: str         # Full name of the ideology
    short_name: str   # Abbreviated name (e.g., 'lg' for "Lawful Good")
    description: str  # Detailed description of the ideology

# Example instance
lawful_good = Ideology(
    vector='',
    name='Законно-Добрые',
    short_name='',
    description=(
        'Существа совершают поступки, считающиеся в обществе как правильные. '
        'Золотые драконы, паладины и большинство дварфов являются законно-добрыми.'
    )
)

IDEOLOGY = []
IDEOLOGY_DICT = {ideology.short_name: ideology for ideology in IDEOLOGY}