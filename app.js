const Discord = require("discord.js");
const pokerBot = new Discord.CLient();
const prefix = "$";

var numPlayers, turn = 9, dealt = 0;
var nextMsg = "Use $deal to start the next round";

bot.on("ready", () => {
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

function code(lang, arg) {
  message.channel.sendCode(lang, arg);
}

function embed(titleArg, desc) {
  message.channel.sendEmbed({title: titleArg, description: desc});
}

function msg(arg) {
  message.channel.sendMessage(arg);
}

var Poker = {};
  Poker.rankArray = ["2","3","4","5","6","7","8","9","10","J","Q","K","A"];
  Poker.suitArray = [":clubs:",":diamonds:",":hearts:",":spades:"];
  Poker.deck = [];
  Poker.deckDisplay = [];
  Poker.newDeck = function(players) {
    numPlayers = players;
    for(i=0; i<rankArray.length; i++) {
      for(j=0; j<suitArray.length; j++) {
      Poker.deck.push(rankArray[i] + suitArray[j]);
      }
    }
  }

bot.on("message", message => {
  if (message.author.bot) return;
  if (!message.content.startWith(prefix)) return;

  let command = message.content.split(" ")[0];
  command = command.slice(prefix.length);
  
  let args = message.content.split(" ").slice(1);
  
  if (command === "poker") {
    msg("Shuffling...");
    shuffle(Poker.deck);
    for(i=0; i<Poker.deck.length; i++) {
      Poker.deckDisplay.push("**" + Poker.deck[i] + "**");
    }
    embed("Shuffled Deck",Poker.deckDisplay.toString().replace(/,/g , "   "));
    turn = 0;
  }
  
  if (command === "deal") {
    msg("Deal with it");
    switch(turn) {
      case 0:
        turn++;
      case 1:
        turn++;
      case 2:
      case 3:
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
