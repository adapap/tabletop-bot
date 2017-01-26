module.exports = {
    Cards: {
        rankArray: ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"],
        suitArray: ["c", "d", "h", "s"],
        dealt: 0,
        shuffle: function(array) { //Shuffle Cards
            var cur = array.length,
            temp, rand;
            while (0 !== cur) {
                rand = Math.floor(Math.random() * cur);
                cur -= 1;
                temp = array[cur];
                array[cur] = array[rand];
                array[rand] = temp;
            }
            return array;
        },
        newDeck: function(obj) {
            obj.deck = [];
            obj.deckDisplay = [];
            for (i = 0; i < this.rankArray.length; i++) {
                for (j = 0; j < this.suitArray.length; j++) {
                    obj.deck.push(this.rankArray[i] + this.suitArray[j]);
                }
            }
            this.shuffle(obj.deck);
            this.dealt = 0;
        }
    }
}