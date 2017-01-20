const Discord = require("discord.js");
const Evaluator = require("poker-evaluator");
const pokerBot = new Discord.Client();
const prefix = "$";

var round = -1,
    dealt = 0,
    startMoney = 100,
    eval,
    game = false,
    maxIndex = 0,
    turn = -1,
    flop;
var nextMsg = "Use **$deal** to start the next round...";
var _s = "   ";

var shorthand = {
    T: "10",
    c: ":clubs:",
    d: ":diamonds:",
    h: ":hearts:",
    s: ":spades:"
};
var colors = {
    red: "15158332",
    green: "2667619",
    gold: "15844367",
    black: "1"
}
var fullname = {
    "high card": "High Card :top:",
    "one pair": "Pair :pear:",
    "two pairs": "Two Pair :pear::pear:",
    "three of a kind": "Three of a Kind :slot_machine:",
    "straight": "Straight :heart::yellow_heart::green_heart::blue_heart::purple_heart:",
    "flush": "Flush :toilet:",
    "full house": "Full House :house_with_garden:",
    "four of a kind": "Four of a Kind :dart::dart::dart::dart:",
    "straight flush": "Straight/Royal Flush :dollar::crown::moneybag:"
}

pokerBot.on("ready", () => {
    console.log("Poker Bot v0.9 loaded.");
    pokerBot.user.setGame("$help");
    botChannels = pokerBot.channels.array();
    for (i=0; i < botChannels.length; i++) {
        if (botChannels[i].type == "text") {
        botChannels[i].sendEmbed({title: "Hello, I am *PokerBot*!",description: `In Poker, you are dealt 2 cards and must place and call bets.
To see your cards, you will have to pay the 'ante', an entry bet.
*Note*: Currently, there are no blind bets through this bot.
The player with the highest ranking hand wins (see $table).
To start a new game, add players with $p and type $new to begin!

Type **$help** to see my commands`,color: colors.red});
        }
    }
});

function shuffle(array) { //Shuffle Cards
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
}

playerArray = [];
playerCount = 0;

function Player(name, money) {
    this.name = name;
    this.hand = [];
    this.handVal = 0;
    this.handName = "";
    this.money = money;
    this.ante = false;
    this.fold = false;
    this.doFold = function(t) {
        if (t) {
            turn++;
            this.fold = true;
        }
    }
    this.check = function(t) {
        if (t) { turn++; }
    }
    this.raise = function(t) {
        if (t) {
            //Raise Function with Poker.raise
        }
    }
    this.call = function(t) {
        if (t) {
            //Call Function from Poker.raise
        }
    }
};

function findPlayer(user) {
    function getIndex(usr) {
        return usr.name == user;
    }
    return playerArray.findIndex(getIndex);
}

function isTurn(play) {
    if (playerArray.indexOf(play) == turn) {return true;}
    else { return false; }
}

function getChannels() {
}

var Poker = {};
Poker.community = [];
Poker.rankArray = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"];
Poker.suitArray = ["c", "d", "h", "s"];
Poker.pot = 0;
Poker.minBet = 0;
Poker.raise = 0;
Poker.newDeck = function() {
    Poker.deck = [];
    Poker.deckDisplay = [];
    for (i = 0; i < Poker.rankArray.length; i++) {
        for (j = 0; j < Poker.suitArray.length; j++) {
            Poker.deck.push(Poker.rankArray[i] + Poker.suitArray[j]);
        }
    }
}
Poker.calcHands = function() {
    for(i=0; i < playerCount; i++) {
        eval = Evaluator.evalHand(playerArray[i].hand.concat(Poker.community));
        playerArray[i].handVal = eval.value;
        playerArray[i].handName = eval.handName;
    }
    var maxArray = playerArray.map(function(a) {return a.handVal});
    maxIndex = maxArray.indexOf(Math.max(...maxArray));
    return maxIndex;
}

pokerBot.on("guildMemberAdd", guild => {
    member.guild.defaultChannel.sendMessage(`Welcome ${member.user.username}! Type $help to get started...`);
})

pokerBot.on("message", message => {
    function code(lang, arg) {
        message.channel.sendCode(lang, arg);
    }
    function dm(msg, emb) {
        message.author.send(msg, emb);
    }
    function embed(titleArg, desc, color) {
        return {embed: {title: titleArg,
            description: desc,
            color: color.replace(/^red$|^green$|^gold$|^black$/gi, function(matched) {return colors[matched];})
        }};
    }
    function purge(amount) {
        message.channel.fetchMessages({limit: amount || 10}).then(messages => message.channel.bulkDelete(messages)).catch(console.error);
    }
    function send(msg, embed) {
        message.channel.send(msg, embed);
    }
    
    if (message.author.bot) return;
    if (!message.content.startsWith(prefix)) return;
    if (message.channel.type !== "text") { send("You must be in a guild channel to use commands."); return; }

    var command = message.content.split(" ")[0];
    command = command.slice(prefix.length);

    var args = message.content.split(" ").slice(1);
    
    if (command === "test") {
        
    }
    
    if (command === "$clear") {
        purge(args[0]);
    }

    if (command === "new") {
        if (playerCount >= 1 && playerCount <= 9) {
            Poker.newDeck(Player.count, args[0]);
            shuffle(Poker.deck);
            for (i = 0; i < Poker.deck.length; i++) {
                Poker.deckDisplay.push("**" + Poker.deck[i].replace(/T|c|d|h|s/gi, function(matched) {
                    return shorthand[matched];
                }) + "**");
            }
            //embed("Shuffled Deck", Poker.deckDisplay.toString().replace(/,/g, _s));
            round = 0;
            turn = 0;
            dealt = 0;
            send("Deck shuffled. Please wait until all cards are dealt...");
            game = true;
            action();
        } else {
            send("You need 2-9 players to start a game. Type **$player** for more info...");
        }
    }

    if (command === "player" || command === "p") {
        switch (args[0]) {
            case "add":
                if (typeof args[1] === 'string' && args[1].substr(0,2) == '<@') { //Better test for username needed
                    playerArray.push(new Player(args[1], startMoney));
                    send(`${args[1]} was added to the game.`);
                } else {
                    send('Invalid username.');
                }
                break;
            case "del":
                if (typeof args[1] === 'string' && args[1].substr(0,2) == '<@') {
                    if (findPlayer(args[1]) > -1) {
                        playerArray.splice(args[1], 1);
                        send(`${args[1]} was removed to the game.`);
                    }
                } else {
                    send('Invalid username.');
                }
                break;
            case "clr":
                playerArray = [];
                send('Players reset.');
                break;
            case "list":
                if (playerCount > 0) {
                    send(`Current players: ${playerArray.map(function(a) {return a.name; }).toString().replace(/,/g, ', ')}`);
                }
                else {
                    send("No players have been added to the list.");
                }
                break;
            default:
                send("```Fix\n$player/$p [add/del] {name} - Add/remove players to the game```");
                break;
        }
        playerCount = playerArray.length;
    }
    
    function action() {
        if (round == 0) { //Pre-Flop
            if (turn == 0) {
                send("",embed("Round 1: Pre-Flop"," ","gold"));
                for (i = 0; i < playerCount * 2 - 1; i += 2) {
                    playerArray[i / 2].hand = [Poker.deck[i], Poker.deck[i + 1]];
                }
                send("Type **$ante** to receive your cards");
                dealt = 4;
            }
            else if (turn < playerCount && turn > 0) {
                send(`${playerCount - turn} player(s) need to **$ante**...`);
            }
            else {
                round++;
                turn = 0;
                send(nextMsg);
            }
        }
        else if (round == 1) { //Pre-Flop Bet
        }
        else if (round == 9) { //End Game
            for (j=0; j < 5; j++) {
                    Poker.community[j] = Poker.deck[dealt + j];
            }
            maxIndex = Poker.calcHands();
            send(`${playerArray[maxIndex].name} wins with a **${playerArray[maxIndex].handName.replace(/^high card$|^one pair$|^two pairs$|^three of a kind$|^straight$|^flush$|^full house$|^four of a kind$|^straight flush$/gi, function(matched) {
                return fullname[matched];
            })}**`,embed(playerArray[maxIndex].name + "'s Cards", Poker.deckDisplay[2*maxIndex] + _s + Poker.deckDisplay[2*maxIndex + 1],"green"));
            game = false;
            round = -1;
            turn = -1;
            Poker.pot = 0;
            for (i=0; i < playerCount; i++) {
                playerArray[i].fold = false;
                playerArray[i].ante = false;
            }
            send("Type **$new** to shuffle and start again");
        }
    }
    
    if (command === "ante") {
        if (game) {
            var playerIndex = findPlayer(`<@${message.author.id}>`);
            if (playerArray[playerIndex].fold == false && playerArray[playerIndex].money >= Poker.minBet)
            dm(`Channel: #${message.channel.name} | Server: __${message.guild.name}__`,embed("Your Cards",Poker.deckDisplay[playerIndex * 2] + _s + Poker.deckDisplay[playerIndex * playerIndex * 2 + 1],"green"));
            if (!playerArray[playerIndex].ante) {playerArray[playerIndex].ante; turn++;}
            action();
        }
        else {
            send("Game has not started. Start a new game with **$new**...")
        }
    }
    if (command === "deal") {
        switch (round) {
            case 1:
                round++;
                flop = Poker.deckDisplay[dealt] + _s + Poker.deckDisplay[dealt + 1] + _s + Poker.deckDisplay[dealt + 2];
                send(nextMsg, embed("Round 2: Flop", flop, "gold"));
                break;
            case 2:
                round++;
                send(nextMsg, embed("Round 3: Turn", `${flop}   ${Poker.deckDisplay[dealt + 3]}`,"gold"));
                break;
            case 3:
                round = 9;
                send("",embed("Final Round: River", `${flop}   ${Poker.deckDisplay[dealt + 3]}   ${Poker.deckDisplay[dealt + 4]}`,"gold"));
                action();
                break;
        }
    }

    if (command === "draw") {
        if (game) { send("Your card is: ",embed(null, Poker.deck[Math.random * Poker.deck.length],"black")); }
        else { send("The deck is not shuffled. Type **$new** to shuffle the deck.")}
    }

    if (command === "help" || command === "commands") {
        code("fix",`[Command List]
$help/$commands - Display this command list
$ante - Check the cards dealt to you
$deal - Begins the next round of the game (temporary)
$draw - Draw a random card from the deck
$money {amount} - Set the starting balance for each player
$new - Shuffles the deck and starts a new game
$player/$p [add/del/clr/list] - Add/remove/clear/list players
$table - Displays a list of hand types in order of rank`);
    }
    if (command === "table") {
        send("",embed("__Hand Ranks__ (Highest to Lowest)",`**Royal Flush** - A:clubs: K:clubs: Q:clubs: J:clubs: 10:clubs:

**Straight Flush** - 3:hearts: 4:hearts: 5:hearts: 6:hearts: 7:hearts:

**Four of a Kind** - K:spades: K:diamonds: 3:clubs: K:hearts: K:clubs:`,"red"));
    }
});

pokerBot.login("MjcxMDgyOTE0NTQyOTExNDkw.C2E3GQ.YPOqT8xC60_cCrxZCoQ-ZrJuPiE");
