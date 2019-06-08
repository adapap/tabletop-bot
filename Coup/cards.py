from Card import BasicCard
class CharacterCard(BasicCard):
    def __repr__(self):
        return self.name

Duke = CharacterCard(name='Duke', image='')
Assassin = CharacterCard(name='Assassin', image='')
Captain = CharacterCard(name='Captain', image='')
Ambassador = CharacterCard(name='Duke', image='')
Contessa = CharacterCard(name='Contessa', image='')