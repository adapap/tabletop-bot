module.exports = {
    Player: function(name, money, username) {
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
        this.Poker = {
            doFold: function(t) {
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
            },
            check: function(t) {
                if (t) {
                    if (Poker.curBet == 0 || playerArray[turn].bet == Poker.curBet) {
                        return true;
                    } else {
                        return false;
                    }
                } else {
                    return "turn";
                }
            },
            raise: function(t, amount) {
                if (t) {
                    if (amount < playerArray[turn].money) {
                        return true;
                    } else if (amount >= playerArray[turn].money) {
                        return "allin"
                    }
                } else {
                    return "turn";
                }
            },
            call: function(t) {
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
        }
    }
}