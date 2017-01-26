module.exports = {
    Cards: {
        rankArray: ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"],
        suitArray: ["c", "d", "h", "s"],
        dealt: 0,
        newDeck: = function(obj) {
            obj.deck = [];
            obj.deckDisplay = [];
            for (i = 0; i < Cards.rankArray.length; i++) {
                for (j = 0; j < Cards.suitArray.length; j++) {
                    obj.deck.push(Cards.rankArray[i] + Cards.suitArray[j]);
                }
            }
        }
    }
}