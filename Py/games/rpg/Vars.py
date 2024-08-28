import textFile as textFile

PlayerName = 'Default-Name'
PlayerHealth = [100, 'Max']
current_choice = 0
TextFile = textFile.TextFile
TextChoices = textFile.TextChoices
indexing = textFile.indexing
audioIsPlaying = 0

class player:
    walking: int
    casting: int
    active: int
    talking: int
    fighting: int
    alive: int
    age: int