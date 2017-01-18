const Discord = require("discord.js");
const pokerBot = new Discord.Client();
const prefix = "$";

var numPlayers = 0, turn = 9, dealt = 0, flop;
var nextMsg = "Use **$deal** to start the next round";
var _s = "   ";

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
  Poker.newDeck = function(players) {
    Poker.deck = [];
    Poker.deckDisplay = [];
    numPlayers = players;
    for(i=0; i<Poker.rankArray.length; i++) {
      for(j=0; j<Poker.suitArray.length; j++) {
      Poker.deck.push(Poker.rankArray[i] + Poker.suitArray[j]);
      }
    }
  }
  
var Player = {};
  Poker.players = [];

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

  var command = message.content.split(" ")[0];
  command = command.slice(prefix.length);
  
  var args = message.content.split(" ").slice(1);
  
  if (command === "poker") {
    if (players >= 2) {
      Poker.newDeck(players.length);
      msg("Shuffling...");
      shuffle(Poker.deck);
      for(i=0; i<Poker.deck.length; i++) {
        Poker.deckDisplay.push("**" + Poker.deck[i] + "**");
      }
      embed("Shuffled Deck",Poker.deckDisplay.toString().replace(/,/g , _s));
      turn = dealt = 0;
    }
  }
  
  if (command === "player") {
    console.log(args);
    switch(args[0]) {
      case "add":
        Player.players.push(args[1]);
        break;
      case "del":
        if (Player.players.indexOf(args[1] > -1) {
            array.splice(index, 1);
                  }
        break;
      case "clr":
        Player.players = [];
        break;
                  }
  }
  
  if (command === "deal") {
    switch(turn) {
      case 0:
        turn++;
        for(i=0; i<numPlayers*2 - 1; i+=2) {
          embed("Player " + (i/2 + 1) + "'s Cards",Poker.deckDisplay[i] + _s + Poker.deckDisplay[i+1]);
        }
        embed("Pre-Flop");
        msg(nextMsg);
        dealt = 3;
        break;
      case 1:
        turn++;
        flop = Poker.deckDisplay[dealt] + _s + Poker.deckDisplay[dealt+1] + _s + Poker.deckDisplay[dealt+2];
        embed("Flop",flop);
        msg(nextMsg);
        break;
      case 2:
        turn++;
        embed("Turn",flop + _s + Poker.deckDisplay[dealt+3]);
        msg(nextMsg);
        break;
      case 3:
        turn = 9;
        embed("River",flop + _s + Poker.deckDisplay[dealt+3] + _s + Poker.deckDisplay[dealt+4]);
        break;
      case 9:
        msg("Use **$poker** to shuffle and start again");
        break;
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
