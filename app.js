const Discord = require("discord.js");
const pokerBot = new Discord.Client();
const prefix = "$";

var numPlayers, turn = 9, dealt = 0;
var nextMsg = "Use $deal to start the next round";

pokerBot.on("ready", () => {
  console.log("Poker Bot v0.4 loaded.");
});

function shuffle(array) { //Shuffle Cards
  var cur = array.length, temp, rand;
  while (0 !== cur) {
    rand = Math.floor(Math.random() * cur);
    cur -= 1;
    temp = array[cur];
    array[cur] = array[rand];
    array[rand] = temp;
  }
  return array;
}

var Poker = {};
  Poker.rankArray = ["2","3","4","5","6","7","8","9","10","J","Q","K","A"];
  Poker.suitArray = [":clubs:",":diamonds:",":hearts:",":spades:"];
  Poker.deck = [];
  Poker.deckDisplay = [];
  Poker.newDeck = function(players) {
    numPlayers = players;
    for(i=0; i<Poker.rankArray.length; i++) {
      for(j=0; j<Poker.suitArray.length; j++) {
      Poker.deck.push(Poker.rankArray[i] + Poker.suitArray[j]);
      }
    }
  }

pokerBot.on("message", message => {
function code(lang, arg) {
  message.channel.sendCode(lang, arg);
}

function embed(titleArg, desc) {
  message.channel.sendEmbed({title: titleArg, description: desc});
}

function msg(arg) {
  message.channel.sendMessage(arg);
}
  if (message.author.bot) return;
  if (!message.content.startsWith(prefix)) return;

  let command = message.content.split(" ")[0];
  command = command.slice(prefix.length);
  
  let args = message.content.split(" ").slice(1);
  
  if (command === "poker") {
    Poker.newDeck(2);
    msg("Shuffling...");
    shuffle(Poker.deck);
    for(i=0; i<Poker.deck.length; i++) {
      Poker.deckDisplay.push("**" + Poker.deck[i] + "**");
    }
    embed("Shuffled Deck",Poker.deckDisplay.toString().replace(/,/g , "   "));
    turn = 0;
  }
  
  if (command === "deal") {
    switch(turn) {
      case 0:
        turn++;
        for(i=0; i<numPlayers*2 - 1; i+=2) {
            embed("Player " + (i/2 + 1) + "'s Cards",Poker.deckDisplay[i] + "   " + Poker.deckDisplay[i+1]);
        }
      case 1:
        turn++;
      case 2:
        turn++;
      case 3:
        turn = 9;
      case 9:
        msg("Use $poker to shuffle and start again");
    }
  }
  
  if (command === "draw") {
    msg("Your card is: ");
    embed(null,Poker.deck[Math.random * Poker.deck.length]);
  }
  
  if (command === "help" || command === "commands") {
    code("fix","$help/$commands - Display this command list\n$deal - Deals cards to all players\n$draw - Draw a random card from the deck\n$poker - Resets the game by shuffling the deck");
  }
});

pokerBot.login("MjcxMDgyOTE0NTQyOTExNDkw.C2E3GQ.YPOqT8xC60_cCrxZCoQ-ZrJuPiE");
