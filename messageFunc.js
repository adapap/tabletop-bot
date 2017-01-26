module.exports = {
    code: function(lang, arg) {
        message.channel.sendCode(lang, arg);
    },
    dm: function(msg, emb) {
        message.author.send(msg, emb);
    },
    embed: function(titleArg, desc, color) {
        return {
            embed: {
                title: titleArg,
                description: desc,
                color: color.replace(/^red$|^green$|^gold$|^black$|^blue$/gi, function(matched) {
                    return colors[matched];
                })
            }
        };
    },
    purge: function(amount) {
        if (amount >= 1 && amount < 100) {
            amount++;
            message.delete();
            message.channel.fetchMessages({
                limit: amount || 10
            }).then(messages => message.channel.bulkDelete(messages)).catch(console.error);
        } else {
            send("Invalid amount of messages. Must be between 1-99.");
        }
    },
    send: function(msg, embed) {
        message.channel.send(msg, embed);
    },
    getUserName: function(id) {
        var userIndex = userNameArray.map(function(a) {
            return `<@${a.user.id}>`;
        }).indexOf(id);
        return userNameArray[userIndex].user.username;
    },
    isBot: function(id) {
        var botArray = userNameArray.map(function(a) {
            return a.user.bot;
        });
        var botIndex = userNameArray.map(function(a) {
            return `<@${a.user.id}>`;
        }).indexOf(id);
        return botArray[botIndex];
    }
}