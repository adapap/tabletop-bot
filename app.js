const Discord = require("discord.js");
const Evaluator = require("poker-evaluator");
const pokerBot = new Discord.Client();
const prefix = "$";

/*=================
[Variables/Objects]
=================*/

var round = 0,
    dealt = 0,
    eval,
    game = false,
    maxIndex = 0,
    turn = 0;
var nextMsg = "Use **$deal** to start the next round...";
var startGameMsg = "Game has not started. Start a new game with **$new**...";
var endGameMsg = "Please wait for the current game to end.";
var anteMsg = "You cannot do this before or during the ante.";
var allinMsg = false;
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
    blue: "3447003",
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

playerArray = [];
playerCount = 0;

function Player(name, money, username) {
    this.name = name;
    this.username = username;
    this.hand = [];
    this.handVal = 0;
    this.handName = "";
    this.money = money;
    this.bet = 0;
    this.ante = false;
    this.fold = false;
    this.allin = false;
    this.lastRaise = false;
    this.doFold = function(t) {
        if (t) {
            if (!this.fold) {
                this.fold = true;
                return true;
            } else {
                return false;
            }
        } else {
            return "turn";
        }
    }
    this.check = function(t) {
        if (t) {
            if (Poker.curBet == 0 || playerArray[turn].bet == Poker.curBet) {
                return true;
            } else {
                return false;
            }
        } else {
            return "turn";
        }
    }
    this.raise = function(t, amount) {
        if (t) {
            if (amount < playerArray[turn].money) {
                return true;
            } else if (amount >= playerArray[turn].money) {
                return "allin"
            }
        } else {
            return "turn";
        }
    }
    this.call = function(t) {
        if (t) {
            if (Poker.curBet !== playerArray[turn].bet) {
                if (playerArray[turn].money <= (Poker.curBet - playerArray[turn].bet)) {
                    if (Poker.allinCount == playerCount - 1 && playerCount > 1) {
                        return "last-allin";
                    } else {
                        return "allin";
                    }
                } else {
                    if (Poker.allinCount == playerCount - 1 && playerCount > 1) {
                        return "last-call";
                    } else {
                        return true;
                    }
                }
            } else {
                return false;
            }
        } else {
            return "turn";
        }
    }
};

var Poker = {};
Poker.community = [];
Poker.rankArray = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"];
Poker.suitArray = ["c", "d", "h", "s"];
Poker.startMoney = 100;
Poker.pot = 0;
Poker.minBet = 2;
Poker.curBet = 0;
Poker.foldCount = 0;
Poker.allinCount = 0;
Poker.lastCall = false;
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
    for (i = 0; i < playerCount; i++) {
        eval = Evaluator.evalHand(playerArray[i].hand.concat(Poker.community));
        playerArray[i].handVal = eval.value;
        playerArray[i].handName = eval.handName;
    }
    var maxArray = playerArray.map(function(a) {
        return a.handVal
    });
    maxIndex = [maxArray.indexOf(Math.max(...maxArray))];
    return maxIndex;
}

/*================
[Global Functions]
================*/
function findPlayer(user) {
    function getIndex(usr) {
        return usr.name == user;
    }
    return playerArray.findIndex(getIndex);
}

function isTurn(user) {
    var names = playerArray.map(function(a) {
        return a.name;
    });
    if (names.indexOf(user) == turn) {
        return true;
    } else {
        return false;
    }
}

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

pokerBot.on("ready", () => {
    console.log("Poker Bot v1.0 loaded.");
    pokerBot.user.setGame("$help");
    var botGuilds = pokerBot.guilds.array();
    for (i = 0; i < botGuilds.length; i++) {
        botGuilds[i].defaultChannel.sendEmbed({
            title: "Hello, I am *PokerBot*!",
            description: `In Poker, you are dealt 2 cards and must place and call bets.
To see your cards, you will have to pay the 'ante', an entry bet.
*Note*: There are no blind bets with this bot.
Your hand is the best 5 cards that you can play at a time.
The player with the highest ranking hand wins (see $table).
To start a new game, add players with $p and type $new to begin!

Type **$help** to see my commands...`,
            color: colors.red
        });
    }
});

/*================
[List of Commands]
================*/

pokerBot.on("guildMemberAdd", member => {
    member.guild.defaultChannel.sendMessage(`Welcome ${member.user.username}! Type $help to get started...`);
})

pokerBot.on("message", message => {
    /*===================
    [onMessage Functions]
    ===================*/
    var userId = `<@${message.author.id}>`;
    var userName = message.author.username;
    if (message.channel.type === "text") {
        var userNameArray = message.channel.guild.members.array();
    }

    function code(lang, arg) {
        message.channel.sendCode(lang, arg);
    }

    function dm(msg, emb) {
        message.author.send(msg, emb);
    }

    function embed(titleArg, desc, color) {
        return {
            embed: {
                title: titleArg,
                description: desc,
                color: color.replace(/^red$|^green$|^gold$|^black$|^blue$/gi, function(matched) {
                    return colors[matched];
                })
            }
        };
    }

    function purge(amount) {
        if (amount >= 1 && amount < 100) {
            amount++;
            message.delete();
            message.channel.fetchMessages({
                limit: amount || 10
            }).then(messages => message.channel.bulkDelete(messages)).catch(console.error);
        } else {
            send("Invalid amount of messages. Must be between 1-99.");
        }
    }

    function send(msg, embed) {
        message.channel.send(msg, embed);
    }

    function getUserName(id) {
        var userIndex = userNameArray.map(function(a) {
            return `<@${a.user.id}>`;
        }).indexOf(id);
        return userNameArray[userIndex].user.username;
    }

    function isBot(id) {
        var botArray = userNameArray.map(function(a) {
            return a.user.bot;
        });
        var botIndex = userNameArray.map(function(a) {
            return `<@${a.user.id}>`;
        }).indexOf(id);
        return botArray[botIndex];
    }
    /*Game Functions*/
    function balance(user) {
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
    }

    function removePlayer(name) {
        if (findPlayer(name) > -1) {
            playerArray.splice(findPlayer(name), 1);
            send(`${name} was removed from the game.`);
        }
        playerCount = playerArray.length;
    }

    function nextRound() {
        if (round !== 4 && Poker.lastCall === false) {
            send("", embed("Balances", balance("all"), "blue"));
        }
        Poker.curBet = 0;
        for (i = 0; i < playerCount; i++) {
            playerArray[i].bet = 0;
            playerArray[i].lastRaise = false;
        }
        turn = 0;
        round++;
        action();
    }

    function endGame() {
        send("", embed("Balances", balance("all"), "blue"));
        game = false;
        allinMsg = false;
        round = 0;
        turn = 0;
        maxIndex = 0;
        Poker.pot = 0;
        Poker.community = [];
        Poker.curBet = 0;
        Poker.foldCount = 0;
        Poker.allinCount = 0;
        Poker.deck = [];
        Poker.lastCall = 0;
        for (i = 0; i < playerCount; i++) {
            if (playerArray[i].money == 0) {
                removePlayer(playerArray[i].name);
            }
        }
        for (i = 0; i < playerCount; i++) {
            playerArray[i].fold = false;
            playerArray[i].ante = false;
            playerArray[i].allin = false;
            playerArray[i].lastRaise = false;
            playerArray[i].bet = 0;
            playerArray[i].hand = [];
            playerArray[i].handVal = 0;
            playerArray[i].handName = "";
        }
        balance();
        send("Type **$new** to shuffle and start again");
    }

    function roundAction() {
        if (actionAble() === true) {
            send(`${playerArray[turn].name}, it is your turn. **$check**, **$raise**, **$fold**, or **$call**?`);
        } else if (actionAble() === "allin") {
            send(`${playerArray[turn].name}, it is your turn. You must **$fold** or go all in with **$call**.`);
        } else {
            turn++;
            action();
        }
    }

    function actionAble() {
        if (playerArray[turn].fold === true) {
            return false;
        } else if (playerArray[turn].allin === true) {
            return false;
        } else if (playerArray[turn].lastRaise === true) {
            return false;
        } else if (Poker.lastCall) {
            return false;
        } else if (playerArray[turn].money <= Poker.curBet) {
            return "allin";
        } else {
            return true;
        }
    }
    /*=========
    [Game Loop]
    =========*/
    function action() {
        if (Poker.lastCall === true && round < 4) {
            console.log("last call");
            if (!allinMsg) {
                send("All other players are all in! Who will win in the showdown?");
                allinMsg = true;
            }
            nextRound();
        } else if (Poker.foldCount !== playerCount - 1 || Poker.foldCount == 0) {
            if (round == 0) { //Ante
                if (turn == 0) {
                    send("", embed("The Ante - Type **$ante** to receive your cards", "", "gold"));
                    for (i = 0; i < playerCount * 2 - 1; i += 2) {
                        playerArray[i / 2].hand = [Poker.deck[i], Poker.deck[i + 1]];
                    }
                    dealt = 2*playerCount;
                } else if (turn < playerCount && turn > 0) {
                    send(`${playerCount - turn} player(s) remaining to **$ante**...`);
                } else {
                    nextRound();
                }
            } else if (round == 1) { //Pre-Flop Betting
                if (turn == 0 && Poker.curBet == 0) {
                    send("", embed(`Round 1: Pre-Flop | Pot: $${Poker.pot}`, "", "gold"));
                    roundAction();
                } else if (turn == playerCount) {
                    nextRound();
                } else {
                    roundAction();
                }
            } else if (round == 2) { //Flop
                if (turn == 0 && Poker.curBet == 0) {
                    send("", embed(`Round 2: Flop | Pot: $${Poker.pot}`,`${Poker.deckDisplay[dealt]}   ${Poker.deckDisplay[dealt + 1]}   ${Poker.deckDisplay[dealt + 2]}`, "gold"));
                    roundAction();
                } else if (turn == playerCount) {
                    nextRound();
                } else {
                    roundAction();
                }
            } else if (round == 3) {
                if (turn == 0 && Poker.curBet == 0) {
                    send("", embed(`Round 3: Turn | Pot: $${Poker.pot}`, `${Poker.deckDisplay[dealt]}   ${Poker.deckDisplay[dealt + 1]}   ${Poker.deckDisplay[dealt + 2]}   ${Poker.deckDisplay[dealt + 3]}`, "gold"));
                    roundAction();
                } else if (turn == playerCount) {
                    nextRound();
                } else {
                    roundAction();
                }
            } else if (round == 4) {
                if (turn == 0 && Poker.curBet == 0) {
                    send("", embed(`Final Round: River | Pot: $${Poker.pot}`, `${Poker.deckDisplay[dealt]}   ${Poker.deckDisplay[dealt + 1]}   ${Poker.deckDisplay[dealt + 2]}   ${Poker.deckDisplay[dealt + 3]}   ${Poker.deckDisplay[dealt + 4]}`, "gold"));
                    roundAction();
                } else if (turn == playerCount) {
                    nextRound();
                } else {
                    roundAction();
                }
            } else if (round == 5) { //End Game
                for (j = 0; j < 5; j++) {
                    Poker.community[j] = Poker.deck[dealt + j];
                }
                maxIndex = Poker.calcHands();
                if (maxIndex.length == 1) {
                    send(`${playerArray[maxIndex[0]].name} wins $${Poker.pot} with a **${playerArray[maxIndex[0]].handName.replace(/^high card$|^one pair$|^two pairs$|^three of a kind$|^straight$|^flush$|^full house$|^four of a kind$|^straight flush$/gi, function(matched) {
                    return fullname[matched];
                })}**`, embed(playerArray[maxIndex[0]].name + "'s Cards", Poker.deckDisplay[2 * maxIndex[0]] + _s + Poker.deckDisplay[2 * maxIndex[0] + 1], "green"));
                    playerArray[maxIndex[0]].money += Poker.pot;
                }
                endGame();
            }
        } else { //All other players have folded
            var foldArray = playerArray.map(function(a) {
                return a.fold;
            });
            maxIndex = foldArray.indexOf(false);
            send(`${playerArray[maxIndex].name} wins $${Poker.pot}!`);
            playerArray[maxIndex].money += Poker.pot;
            endGame();
        }
    }
    /*==================
    [onMessage Commands]
    ==================*/
    if (message.author.bot) return;
    if (!message.content.startsWith(prefix)) return;
    if (message.channel.type !== "text") {
        send("You must be in a guild channel to use commands.");
        return;
    }

    var command = message.content.split(" ")[0];
    command = command.slice(prefix.length);
    var args = message.content.split(" ").slice(1);

    if (command === "test") {
        console.log("No test command set.");
    }

    if (command === "$clear") {
        purge(args[0]);
    }

    if (command === "$showDeck") {
        embed("Shuffled Deck", Poker.deckDisplay.toString().replace(/,/g, _s));
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
        if (!game) {
            switch (args[0]) {
                case "add":
                    if (typeof args[1] === 'string' && args[1].substr(0, 2) == '<@' && !isBot(args[1])) { //Improvements for username test?
                        playerArray.push(new Player(args[1], Poker.startMoney, getUserName(args[1])));
                        send(`${args[1]} was added to the game.`);
                    } else {
                        send('Invalid username / User is a bot.');
                    }
                    break;
                case "del":
                    if (typeof args[1] === 'string' && args[1].substr(0, 2) == '<@') {
                        removePlayer(args[1]);
                    } else {
                        send('Invalid username.');
                    }
                    break;
                case "clr":
                    playerArray = [];
                    send('Player list cleared.');
                    break;
                case "list":
                    if (playerCount > 0) {
                        send(`Current players: ${playerArray.map(function(a) {return a.name; }).toString().replace(/,/g, ', ')}`);
                    } else {
                        send("No players have been added to the list.");
                    }
                    break;
                default:
                    send("*Note: Players are removed upon losing all of their money*```Fix\n$player/$p [add/del] {name} - Add/remove players to the game```");
                    break;
            }
            playerCount = playerArray.length;
        } else send(endGameMsg);
    }

    if (command === "money") {
        if (!game) {
            if (args[0] >= 20 && args[1] >= 2 || null) {
                Poker.startMoney = args[0];
                Poker.minBet = args[1];
            } else {
                send(`Starting money must be greater than 20, and the minimum bet must be greater than 2.
\`$money {start} {min. bet} - Set the starting balance and minimum bet for all players\``);
            }
        } else {
            send(endGameMsg);
        }
    }

    if (command === "balance" || command === "bal") {
        if (typeof args[0] === 'string' && args[0].substr(0, 2) == '<@') {
            send("", embed("Balance", balance(args[0]), "blue"));
        } else {
            send("", embed("Balances", balance("all"), "blue"));
        }
    }

    if (command === "fold") {
        if (game && round > 0) {
            var foldReturn = playerArray[turn].doFold(isTurn(userId));
            if (foldReturn === true) {
                send(`${playerArray[turn].name} folds!`);
                Poker.foldCount++;
                turn++;
                action();
            } else if (foldReturn === false) {
                send(`${playerArray[turn].name}, you already folded!`);
            } else if (foldReturn === "turn") {
                send(`${userId}, it is not your turn.`);
            }
        } else if (game && round === 0) {
            send(anteMsg);
        } else {
            send(startGameMsg);
        }
    }

    if (command === "check") {
        if (game && round > 0) {
            var checkReturn = playerArray[turn].check(isTurn(userId));
            if (checkReturn === true) {
                send(`${playerArray[turn].name} checks.`);
                turn++;
                action();
            } else if (checkReturn === false) {
                send(`${playerArray[turn].name}, you cannot check because someone has raised.`);
            } else if (checkReturn === "turn") {
                send(`${userId}, it is not your turn.`);
            }
        } else if (game && round === 0) {
            send(anteMsg);
        } else {
            send(startGameMsg);
        }
    }

    if (command === "raise") {
        if (game && round > 0) {
            if (parseInt(args[0]) >= Poker.minBet && parseInt(args[0]) >= 2 * Poker.curBet && parseInt(args[0]) <= 1000) {
                var raiseReturn = playerArray[turn].raise(isTurn(userId), parseInt(args[0]));
                if (raiseReturn === true) {
                    send(`${playerArray[turn].name} raises $${parseInt(args[0])}.`);
                    Poker.pot += parseInt(args[0]);
                    Poker.curBet = parseInt(args[0]);
                    playerArray[turn].money -= parseInt(args[0]);
                    playerArray[turn].bet += parseInt(args[0]);
                    for (i = 0; i < playerCount; i++) {
                        playerArray[i].lastRaise = false;
                    }
                    playerArray[turn].lastRaise = true;
                    turn = 0;
                    action();
                } else if (raiseReturn === "allin") {
                    send(`${playerArray[turn].name} is going all in by raising $${playerArray[turn].money}!`);
                    Poker.pot += playerArray[turn].money;
                    Poker.curBet = playerArray[turn].money;
                    Poker.allinCount++;
                    playerArray[turn].bet += playerArray[turn].money;
                    playerArray[turn].money = 0;
                    playerArray[turn].allin = true;
                    for (i = 0; i < playerCount; i++) {
                        playerArray[i].lastRaise = false;
                    }
                    playerArray[turn].lastRaise = true;
                    turn = 0;
                    action();
                } else if (raiseReturn === "turn") {
                    send(`${userId}, it is not your turn.`);
                }
            } else {
                var minRaise = Math.max(2 * Poker.curBet, Poker.minBet);
                send(`Invalid raise. The minimum bet is currently $${minRaise} and the maximum is $1000.`)
            }
        } else if (game && round === 0) {
            send(anteMsg);
        } else {
            send(startGameMsg);
        }
    }

    if (command === "call") {
        if (game && round > 0) {
            var callReturn = playerArray[turn].call(isTurn(userId));
            var diffBet = Poker.curBet - playerArray[turn].bet;
            if (callReturn === true) {
                send(`${playerArray[turn].name} calls $${diffBet}.`);
                Poker.pot += diffBet;
                playerArray[turn].bet += diffBet;
                playerArray[turn].money -= diffBet;
                turn++;
                action();
            } else if (callReturn === "last-call") {
                send(`${playerArray[turn].name} makes the final call of $${diffBet}.`);
                Poker.pot += diffBet;
                Poker.lastCall = true;
                playerArray[turn].bet += diffBet;
                playerArray[turn].money -= diffBet;
                action();
            } else if (callReturn === "allin") {
                send(`${playerArray[turn].name} is going in by matching $${playerArray[turn].money}!`);
                Poker.pot += playerArray[turn].money;
                Poker.allinCount++;
                playerArray[turn].bet += playerArray[turn].money;
                playerArray[turn].money = 0;
                playerArray[turn].allin = true;
                turn++;
                action();
            } else if (callReturn === "last-allin") {
                send(`${playerArray[turn].name} is the last to go all in with $${playerArray[turn].money}!`);
                Poker.pot += playerArray[turn].money;
                Poker.allinCount++;
                Poker.lastCall = true;
                playerArray[turn].bet += playerArray[turn].money;
                playerArray[turn].money = 0;
                playerArray[turn].allin = true;
                action();
            } else if (callReturn === "turn") {
                send(`${userId}, it is not your turn.`);
            } else {
                send(`${playerArray[turn].name}, there is nothing to call. Did you mean to **$check**?`)
            }
        } else if (game && round === 0) {
            send(anteMsg);
        } else {
            send(startGameMsg);
        }
    }

    if (command === "ante") {
        if (game) {
            var playerIndex = findPlayer(userId);
            if (playerArray[playerIndex].fold === false && playerArray[playerIndex].money >= Poker.minBet && playerArray[playerIndex].ante === false) {
                dm(`Channel: #${message.channel.name} | Server: __${message.guild.name}__`, embed("Your Cards", Poker.deckDisplay[playerIndex * 2] + _s + Poker.deckDisplay[playerIndex * playerIndex * 2 + 1], "green"));
                playerArray[playerIndex].ante = true;
                playerArray[playerIndex].money -= Poker.minBet;
                Poker.pot += Poker.minBet;
                turn++;
                action();
            } else if (playerArray[playerIndex].fold) {
                send(`${userId} has already folded!`);
            } else if (playerArray[playerIndex].money < Poker.minBet && playerArray[playerIndex].money > 0) {
                send(`${userId} is going all in!`);
                playerArray[playerIndex].ante = true;
                playerArray[playerIndex].allin = true;
                Poker.allinCount++;
                Poker.pot += playerArray[playerIndex].money;
                playerArray[playerIndex].money = 0;
                turn++;
                action();
            } else if (playerArray[playerIndex].ante === true) {
                send(`${userId} has already called the ante!`);
            } else {
                send("You cannot ante at this time. Please wait until the game is over.");
            }
        } else {
            send(startGameMsg)
        }
    }

    if (command === "end") {
        if (game) {
            endGame();
            send("Game has been terminated.");
        } else {
            send("Game has not started yet.");
        }
    }

    if (command === "draw") {
        if (game) {
            send("Your card is: ", embed("", Poker.deckDisplay[Math.floor(Math.random() * Poker.deckDisplay.length - 1)], "black"));
        } else {
            send("The deck is not shuffled. Type **$new** to shuffle the deck.")
        }
    }

    if (command === "shutdown") {
        send("*PokerBot shutting down...*");
        pokerBot.destroy();
    }

    if (command === "help" || command === "commands") {
        code("fix", `[Command List]
$help/$commands - Display this command list
$ante - Check the cards dealt to you
$balance/$bal {player} - Shows the balances of all players of a specific player
$call - Match a bet that was made through a raise
$check - Play without raising or folding during a turn
$draw - Draw a random card from the deck
$end - Ends the current game
$fold - Stop playing and lose all money played this game
$money {start} {min. bet} - Set the starting balance and minimum bet for all players
$new - Shuffles the deck and starts a new game
$player/$p [add/del/clr/list] - Add/remove/clear/list players
$raise - Make a bet that other players need to call
$restart - Restarts the bot
$table - Displays a list of hand types in order of rank`);
    }
    if (command === "table") {
        send("", embed("__Hand Ranks (Highest to Lowest)__", `**Royal Flush** - A:clubs: K:clubs: Q:clubs: J:clubs: 10:clubs:

**Straight Flush** - 3:hearts: 4:hearts: 5:hearts: 6:hearts: 7:hearts:

**Four of a Kind** - K:spades: K:diamonds: 3:clubs: K:hearts: K:clubs:

**Full House** - 7:diamonds: 7:spades: 7:hearts: Q:hearts: Q:spades:

**Flush** - 4:diamonds: 7:diamonds: 9:diamonds: J:diamonds: A:diamonds:

**Straight** - 7:spades: 8:diamonds: 9:spades: 10:clubs: J:hearts:

**Three of a Kind** - A:spades: 4:hearts: 2:clubs: 4:diamonds: 4:spades:

**Two Pair** - 2:clubs: J:spades: J:diamonds: 8:hearts: 2:hearts:

**Pair** - 6:spades: 3:spades: 7:clubs: 6:hearts: 4:diamonds:

**High Card** - A:diamonds: 4:hearts: 6:clubs: 3:diamonds: Q:spades: (High Card: Ace)`, "red"));
    }
});

pokerBot.login("MjcxMDgyOTE0NTQyOTExNDkw.C2E3GQ.YPOqT8xC60_cCrxZCoQ-ZrJuPiE");