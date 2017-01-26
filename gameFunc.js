module.exports = {
    balance: function(user) {
        if (user !== "all") {
            if (findPlayer(user) == -1) {
                return `${user} is not currently playing. Type **$p** to learn how to add players!`;
            } else {
                return `${playerArray[findPlayer(user)].username} - $${playerArray[findPlayer(user)].money}`;
            }
        } else {
            if (playerCount == 0) {
                return `There are no players in the game. Type **$p** to learn how to add players!`;
            } else {
                var balance = [];
                for (i = 0; i < playerCount; i++) {
                    balance.push(`${playerArray[i].username} - $${playerArray[i].money}\n`);
                }
                return balance.sort().toString().replace(/,/g, "");
            }
        }
    },
    removePlayer: function(name) {
        if (findPlayer(name) > -1) {
            playerArray.splice(findPlayer(name), 1);
            send(`${name} was removed from the game.`);
        }
        playerCount = playerArray.length;
    }
}