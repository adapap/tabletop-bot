const Discord = require("discord.js");
const Evaluator = require("poker-evaluator");
const cardBot = new Discord.Client();
const prefix = "$";

/*=================
[Importing Modules]
=================*/

//Player & Cards
var Player = require("./player.js").Player;
var Cards = require("./cards.js").Cards;

//Shorthand
var shorthand = require("./shorthand.js").shorthand;
var colors = require("./shorthand.js").colors;
var fullname = require("./shorthand.js").fullname;
var blackjackVal = require("./shorthand.js").blackjackVal;

/*=================
[Variables/Objects]
=================*/

var eval,
    game = false,
    gameType = null,
    maxIndex = 0,
    startMoney = 100,
    minBet = 2;

var startGameMsg = "Game has not started. Start a new game with **$poker** or **$blackjack** (W.i.p)...",
    shuffledMsg = "Deck shuffled. Please wait until all cards are dealt...",
    endGameMsg = "Please wait for the current game to end.",
    anteMsg = "You cannot do this before or during the ante.",
    allinMsg = false,
    _s = "   ";

var playerArray = [];
var playerCount = 0;

var Poker = {
    community: [],
    round: 0,
    turn: 0,
    pot: 0,
    curBet: 0,
    foldCount: 0,
    allinCount: 0,
    lastCall: false,
    calcHands: function() {
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
};

var Blackjack = {
    turn: 0,
    pot: 0,
    dealer: {
        hand: [],
        handDisplay: [],
        handVal: 0
    },
    calcHand: function(obj, hand) {
        var aceCount = 0;
        for (i = 0; i < obj.hand.length; i++) {
            var rank = obj.hand[i].substr(0, 1);
            if (rank === "A") {
                aceCount++;
            }
            obj.handVal += blackjackVal[rank];
        }
        while (obj.handVal > 21 && aceCount > 0) {
            obj.handVal -= 10;
            aceCount--;
        }
    },
    calcWin: function() {
        for (i = 0; i < playerCount; i++) {
            //Todo
        }
    }
};

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
    if (names.indexOf(user) == Poker.turn) {
        return true;
    } else {
        return false;
    }
}

cardBot.on("ready", () => {
    console.log("Card Bot v1.2 loaded.");
    cardBot.user.setGame("$help");
});

/*================
[List of Commands]
================*/

cardBot.on("guildMemberAdd", member => {
    member.guild.defaultChannel.sendMessage(`Welcome to the server, ${member.user.username}! Type $help to get started...`);
})

cardBot.on("message", message => {
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

    function embed(titleArg, desc, color = "white") {
        return {
            embed: {
                title: titleArg,
                description: desc,
                color: color.replace(/^red$|^green$|^gold$|^black$|^blue$|^white$/gi, function(matched) {
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
    var balance = require("./gameFunc.js").balance;
    var removePlayer = require("./gameFunc.js").removePlayer;

    function nextRound() {
        if (Poker.round !== 4 && Poker.lastCall === false) {
            send("", embed("Balances", balance("all"), "blue"));
        }
        Poker.curBet = 0;
        for (i = 0; i < playerCount; i++) {
            playerArray[i].bet = 0;
            playerArray[i].lastRaise = false;
        }
        Poker.turn = 0;
        Poker.round++;
        action("Poker");
    }

    function endGame() {
        send("", embed("Balances", balance("all"), "blue"));
        game = false;
        gameType = null;
        allinMsg = false;
        maxIndex = 0;
        Poker.turn = 0;
        Poker.round = 0;
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
        if (playerCount > 1) {
            playerArray = playerArray.concat(playerArray.splice(0,1));
        }
        playerCount = playerArray.length;
        balance();
        send("Start a new game to play again!");
    }

    function roundAction() {
        if (actionAble() === true) {
            send(`${playerArray[Poker.turn].name}, it is your turn. **$check**, **$raise**, **$fold**, or **$call**?`);
        } else if (actionAble() === "allin") {
            send(`${playerArray[Poker.turn].name}, it is your turn. You must **$fold** or go all in with **$call**.`);
        } else {
            Poker.turn++;
            action("Poker");
        }
    }

    function actionAble() {
        if (playerArray[Poker.turn].fold === true) {
            return false;
        } else if (playerArray[Poker.turn].allin === true) {
            return false;
        } else if (playerArray[Poker.turn].lastRaise === true) {
            return false;
        } else if (Poker.lastCall) {
            return false;
        } else if (playerArray[Poker.turn].money <= Poker.curBet) {
            return "allin";
        } else {
            return true;
        }
    }
    /*=========
    [Game Loop]
    =========*/
    function action(game) {
        switch(game) {
            case "Poker": //Poker Handler
            if (Poker.lastCall === true && Poker.round < 4) {
                if (!allinMsg) {
                    send("All other players are all in! Who will win in the showdown?");
                    allinMsg = true;
                }
                nextRound();
            } else if (Poker.foldCount !== playerCount - 1 || Poker.foldCount == 0) {
                if (Poker.round == 0) { //Ante
                    if (Poker.turn == 0) {
                        send("", embed("The Ante - Type **$ante** to receive your cards", "", "gold"));
                        for (i = 0; i < playerCount * 2 - 1; i += 2) {
                            playerArray[i / 2].hand = [Poker.deck[i], Poker.deck[i + 1]];
                        }
                        Cards.dealt = 2*playerCount;
                    } else if (Poker.turn < playerCount && Poker.turn > 0) {
                        send(`${playerCount - Poker.turn} player(s) remaining to **$ante**...`);
                    } else {
                        nextRound();
                    }
                } else if (Poker.round == 1) { //Pre-Flop Betting
                    if (Poker.turn == 0 && Poker.curBet == 0) {
                        send("", embed(`Round 1: Pre-Flop | Pot: $${Poker.pot}`, "", "gold"));
                        roundAction();
                    } else if (Poker.turn == playerCount) {
                        nextRound();
                    } else {
                        roundAction();
                    }
                } else if (Poker.round == 2) { //Flop
                    if (Poker.turn == 0 && Poker.curBet == 0) {
                        send("", embed(`Round 2: Flop | Pot: $${Poker.pot}`,`${Poker.deckDisplay[Cards.dealt]}   ${Poker.deckDisplay[Cards.dealt + 1]}   ${Poker.deckDisplay[Cards.dealt + 2]}`, "gold"));
                        roundAction();
                    } else if (Poker.turn == playerCount) {
                        nextRound();
                    } else {
                        roundAction();
                    }
                } else if (Poker.round == 3) {
                    if (Poker.turn == 0 && Poker.curBet == 0) {
                        send("", embed(`Round 3: Turn | Pot: $${Poker.pot}`, `${Poker.deckDisplay[Cards.dealt]}   ${Poker.deckDisplay[Cards.dealt + 1]}   ${Poker.deckDisplay[Cards.dealt + 2]}   ${Poker.deckDisplay[Cards.dealt + 3]}`, "gold"));
                        roundAction();
                    } else if (Poker.turn == playerCount) {
                        nextRound();
                    } else {
                        roundAction();
                    }
                } else if (Poker.round == 4) {
                    if (Poker.turn == 0 && Poker.curBet == 0) {
                        send("", embed(`Final Round: River | Pot: $${Poker.pot}`, `${Poker.deckDisplay[Cards.dealt]}   ${Poker.deckDisplay[Cards.dealt + 1]}   ${Poker.deckDisplay[Cards.dealt + 2]}   ${Poker.deckDisplay[Cards.dealt + 3]}   ${Poker.deckDisplay[Cards.dealt + 4]}`, "gold"));
                        roundAction();
                    } else if (Poker.turn == playerCount) {
                        nextRound();
                    } else {
                        roundAction();
                    }
                } else if (Poker.round == 5) { //End Game
                    for (j = 0; j < 5; j++) {
                        Poker.community[j] = Poker.deck[Cards.dealt + j];
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
            break;

            case "Blackjack": //Blackjack Handler
                if (Cards.dealt == 0) {
                    for (i = 0; i < playerCount * 2 - 1; i += 2) {
                            playerArray[i / 2].hand = [Blackjack.deck[i], Blackjack.deck[i + 1]];
                        }
                    Cards.dealt = 2*playerCount;
                    Blackjack.dealer.hand = [Blackjack.deck[Cards.dealt], Blackjack.deck[Cards.dealt + 1]];
                    Blackjack.calcHand(Blackjack.dealer, Blackjack.dealer.hand);
                    var dealerCard = Cards.dealt + 2;
                    while (Blackjack.dealer.handVal < 17 && Blackjack.dealer.hand.length < 5) {
                        Blackjack.dealer.hand.push(Blackjack.deck[dealerCard]);
                        dealerCard++;
                        Blackjack.calcHand(Blackjack.dealer, Blackjack.dealer.hand);
                    }
                    for (i = 0; i < Blackjack.dealer.hand.length; i++) {
                        Blackjack.dealer.handDisplay.push("**" + Blackjack.dealer.hand[i].replace(/T|c|d|h|s/gi, function(matched) {
                        return shorthand[matched]; }) + "**");
                    };
                    send("",embed("Dealer's Card",`${Blackjack.dealer.handDisplay[0]}`,"black"));
                    action("Blackjack");
                }
                else if (Blackjack.turn == playerCount) {
                    send("Game is over.");
                }
                else {
                    if (findPlayer(userId) == Blackjack.turn) {
                        var playerIndex = findPlayer(userId);
                        Blackjack.calcHand(playerArray[Blackjack.turn], playerArray[Blackjack.turn].hand);
                        send("",embed(`${playerArray[Blackjack.turn].name}'s Cards | Value: ${playerArray[Blackjack.turn].handVal}`,`${Blackjack.deckDisplay[playerIndex * 2]}   ${Blackjack.deckDisplay[playerIndex * 2 + 1]}`,"green"));
                        send(`${playerArray[Blackjack.turn].name}, it is your turn. Yay!`);
                        /* To-Do:
                        -Go through all player turns
                        -Create a "hit" command
                        -Create a "stay" command
                        -Determine a winner of the game
                        --Implement a betting system to win money (shared with Poker)
                        --Make a split and insurance option during the turn */
                    }
                    else {
                        send(`${playerArray[Blackjack.turn].name}, it is not your turn.`);
                    }
                }
            break;
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

    //Roles
    var cardmaster = message.guild.roles.find("name", "Cardmaster") || false;

    var command = message.content.split(" ")[0];
    command = command.slice(prefix.length);
    var args = message.content.split(" ").slice(1);

    if (command === "test") {
        console.log("No test command set.");
    }

    if (command === "$clear") {
        if (message.member.roles.has(cardmaster.id)) {
            purge(args[0]);
        }
        else {
            send("Gamblers cannot erase their mistakes. Only a __Cardmaster__ can.");
        }
    }

    if (command === "$showDeck") {
        if (message.member.roles.has(cardmaster.id)) {
            embed("Shuffled Deck", Poker.deckDisplay.toString().replace(/,/g, _s));
        } else { return; }
    }

    if (command === "poker") {
        if (playerCount >= 2 && playerCount <= 9) {
            Cards.newDeck(Poker);
            for (i = 0; i < Poker.deck.length; i++) {
                Poker.deckDisplay.push("**" + Poker.deck[i].replace(/T|c|d|h|s/gi, function(matched) {
                return shorthand[matched];
                }) + "**");
            };
            Poker.round = 0;
            Poker.turn = 0;
            send(shuffledMsg);
            game = true;
            gameType = "Poker";
            action("Poker");
        } else { send("You need 2-9 players to play Poker. Type **$player** for more info..."); }
    }

    if (command === "blackjack") {
        if (playerCount > 0 && playerCount <= 8) {
            Cards.newDeck(Blackjack);
            for (i = 0; i < Blackjack.deck.length; i++) {
                Blackjack.deckDisplay.push("**" + Blackjack.deck[i].replace(/T|c|d|h|s/gi, function(matched) {
                return shorthand[matched];
                }) + "**");
            };
            Blackjack.turn = 0;
            send(shuffledMsg);
            game = true;
            gameType = "Blackjack";
            action("Blackjack");
        }
        else { send("You need 1-8 players to play Blackjack. Type **$player** for more info..."); }
    }

    if (command === "player" || command === "p") {
        if (!game) {
            switch (args[0]) {
                case "add":
                    if (typeof args[1] === 'string' && args[1].substr(0, 2) == '<@' && !isBot(args[1])) { //Improvements for username test?
                        if (findPlayer(args[1]) == -1) {
                            playerArray.push(new Player(args[1], startMoney, getUserName(args[1])));
                            send(`${args[1]} was added to the game.`);
                        }
                        else { send(`${args[1]} is already in the game!`); }
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
            if (args[0] >= 20 && (args[1] >= 2 || args[1] === null)) {
                startMoney = args[0];
                minBet = args[1];
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
        if (game && Poker.round > 0 && gameType === "Poker") {
            var foldReturn = playerArray[Poker.turn].Poker.doFold(isTurn(userId));
            if (foldReturn === true) {
                send(`${playerArray[Poker.turn].name} folds!`);
                Poker.foldCount++;
                Poker.turn++;
                action("Poker");
            } else if (foldReturn === false) {
                send(`${playerArray[Poker.turn].name}, you already folded!`);
            } else if (foldReturn === "turn") {
                send(`${userId}, it is not your turn.`);
            }
        } else if (game && Poker.round === 0) {
            send(anteMsg);
        } else if (gameType !== "Poker") { return; }
        else {
            send(startGameMsg);
        }
    }

    if (command === "check") {
        if (game && Poker.round > 0 && gameType === "Poker") {
            var checkReturn = playerArray[turn].Poker.check(isTurn(userId));
            if (checkReturn === true) {
                send(`${playerArray[Poker.turn].name} checks.`);
                Poker.turn++;
                action("Poker");
            } else if (checkReturn === false) {
                send(`${playerArray[Poker.turn].name}, you cannot check because someone has raised.`);
            } else if (checkReturn === "turn") {
                send(`${userId}, it is not your turn.`);
            }
        } else if (game && Poker.round === 0) {
            send(anteMsg);
        } else if (gameType !== "Poker") { return; }
        else {
            send(startGameMsg);
        }
    }

    if (command === "raise") {
        if (game && Poker.round > 0 && gameType === "Poker") {
            if (parseInt(args[0]) >= minBet && parseInt(args[0]) >= 2 * Poker.curBet && parseInt(args[0]) <= 20 * minBet * playerCount) {
                var raiseReturn = playerArray[Poker.turn].Poker.raise(isTurn(userId), parseInt(args[0]));
                if (raiseReturn === true) {
                    send(`${playerArray[Poker.turn].name} raises $${parseInt(args[0])}.`);
                    Poker.pot += parseInt(args[0]);
                    Poker.curBet = parseInt(args[0]);
                    playerArray[Poker.turn].money -= parseInt(args[0]);
                    playerArray[Poker.turn].bet += parseInt(args[0]);
                    for (i = 0; i < playerCount; i++) {
                        playerArray[i].lastRaise = false;
                    }
                    playerArray[Poker.turn].lastRaise = true;
                    Poker.turn = 0;
                    action("Poker");
                } else if (raiseReturn === "allin") {
                    send(`${playerArray[Poker.turn].name} is going all in by raising $${playerArray[Poker.turn].money}!`);
                    Poker.pot += playerArray[Poker.turn].money;
                    Poker.curBet = playerArray[Poker.turn].money;
                    Poker.allinCount++;
                    playerArray[Poker.turn].bet += playerArray[Poker.turn].money;
                    playerArray[Poker.turn].money = 0;
                    playerArray[Poker.turn].allin = true;
                    for (i = 0; i < playerCount; i++) {
                        playerArray[i].lastRaise = false;
                    }
                    playerArray[Poker.turn].lastRaise = true;
                    Poker.turn = 0;
                    action("Poker");
                } else if (raiseReturn === "turn") {
                    send(`${userId}, it is not your turn.`);
                }
            } else {
                var minRaise = Math.max(2 * Poker.curBet, minBet);
                var maxRaise = 20 * minBet * playerCount;
                send(`Invalid raise. The minimum bet is currently $${minRaise} and the maximum is $${maxRaise}.`)
            }
        } else if (game && Poker.round === 0) {
            send(anteMsg);
        } else if (gameType !== "Poker") { return; }
        else {
            send(startGameMsg);
        }
    }

    if (command === "call") {
        if (game && Poker.round > 0 && gameType === "Poker") {
            var callReturn = playerArray[Poker.turn].Poker.call(isTurn(userId));
            var diffBet = Poker.curBet - playerArray[Poker.turn].bet;
            if (callReturn === true) {
                send(`${playerArray[turn].name} calls $${diffBet}.`);
                Poker.pot += diffBet;
                playerArray[Poker.turn].bet += diffBet;
                playerArray[Poker.turn].money -= diffBet;
                Poker.turn++;
                action("Poker");
            } else if (callReturn === "last-call") {
                send(`${playerArray[turn].name} makes the final call of $${diffBet}.`);
                Poker.pot += diffBet;
                Poker.lastCall = true;
                playerArray[Poker.turn].bet += diffBet;
                playerArray[Poker.turn].money -= diffBet;
                action("Poker");
            } else if (callReturn === "allin") {
                send(`${playerArray[Poker.turn].name} is going in by matching $${playerArray[Poker.turn].money}!`);
                Poker.pot += playerArray[Poker.turn].money;
                Poker.allinCount++;
                playerArray[Poker.turn].bet += playerArray[Poker.turn].money;
                playerArray[Poker.turn].money = 0;
                playerArray[Poker.turn].allin = true;
                Poker.turn++;
                action("Poker");
            } else if (callReturn === "last-allin") {
                send(`${playerArray[Poker.turn].name} is the last to go all in with $${playerArray[Poker.turn].money}!`);
                Poker.pot += playerArray[Poker.turn].money;
                Poker.allinCount++;
                Poker.lastCall = true;
                playerArray[Poker.turn].bet += playerArray[Poker.turn].money;
                playerArray[Poker.turn].money = 0;
                playerArray[Poker.turn].allin = true;
                action("Poker");
            } else if (callReturn === "turn") {
                send(`${userId}, it is not your turn.`);
            } else {
                send(`${playerArray[Poker.turn].name}, there is nothing to call. Did you mean to **$check**?`)
            }
        } else if (game && Poker.round === 0) {
            send(anteMsg);
        } else if (gameType !== "Poker") { return; }
        else {
            send(startGameMsg);
        }
    }

    if (command === "ante") {
        if (game && gameType === "Poker") {
            var playerIndex = findPlayer(userId);
            if (playerArray[playerIndex].fold === false && playerArray[playerIndex].money >= minBet && playerArray[playerIndex].ante === false) {
                dm(`Channel: #${message.channel.name} | Server: __${message.guild.name}__`, embed("Your Cards", Poker.deckDisplay[playerIndex * 2] + _s + Poker.deckDisplay[playerIndex * 2 + 1], "green"));
                playerArray[playerIndex].ante = true;
                playerArray[playerIndex].money -= minBet;
                Poker.pot += minBet;
                Poker.turn++;
                action("Poker");
            } else if (playerArray[playerIndex].fold) {
                send(`${userId} has already folded!`);
            } else if (playerArray[playerIndex].money < minBet && playerArray[playerIndex].money > 0) {
                send(`${userId} is going all in!`);
                playerArray[playerIndex].ante = true;
                playerArray[playerIndex].allin = true;
                Poker.allinCount++;
                Poker.pot += playerArray[playerIndex].money;
                playerArray[playerIndex].money = 0;
                Poker.turn++;
                action("Poker");
            } else if (playerArray[playerIndex].ante === true) {
                send(`${userId} has already called the ante!`);
            } else {
                send("You cannot ante at this time. Please wait until the game is over.");
            }
        } else if (gameType !== "Poker") { return; }
        else {
            send(startGameMsg)
        }
    }

    if (command === "end") {
        if (game) {
            send("Game has been terminated.");
            endGame();
        } else {
            send("Game has not started yet.");
        }
    }

    if (command === "restart") {
        send("*CardBot restarting...* (This may take up to a minute)");
        cardBot.destroy();
    }
    
    if (command === "commands" || command === "clist") {
        code("fix", `__Command List__
[General]
$commands/$clist - Display this command list
$balance/$bal {player} - Shows the balances of all players of a specific player
$end - Ends the current game
$help - Sends the help message to the guild
$money {start} {min. bet} - Set the starting balance and minimum bet for new players
$player/$p [add/del/clr/list] - Add/remove/clear/list players
$restart - Restarts the bot

[Poker]
$ante - Check the cards dealt to you
$call - Match a bet that was made through a raise
$check - Play without raising or folding during a turn
$fold - Stop playing and lose all money played this game
$poker - Shuffles the deck and starts a new game
$raise - Make a bet that other players need to call
$table - Displays a list of hand types in order of rank`);
    }

    if (command === "help") {
        message.guild.defaultChannel.sendEmbed({
            title: "Hello, I am *CardBot*!",
            description: `CardBot allows you to play card games with your friends using Discord chat!
Currently, Poker and Blackjack are supported.
To learn more about how to play, check out the commands with **$commands**!`,
            color: colors.red
        });
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

cardBot.login("MjcxMDgyOTE0NTQyOTExNDkw.C2E3GQ.YPOqT8xC60_cCrxZCoQ-ZrJuPiE");