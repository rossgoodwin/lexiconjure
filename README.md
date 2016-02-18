# lexiconjure

[@lexiconjure](https://twitter.com/lexiconjure)

I trained a recurrent neural network on the [Oxford English Dictionary](http://www.oed.com/). When you tweet a word (real or made up) @ the bot, you're seeding that generator. The invented words it tweets automatically every 90 minutes are created by smashing together random sequences of characters with a genetic algorithm until something that looks (sort of) like a real word comes out.

I trained my RNN using [Char-RNN](https://github.com/karpathy/char-rnn) by Andrej Karpathy, and the bot's linguistic-taste integrity is moderated by badwords.json via [Darius Kazemi](https://github.com/dariusk/wordfilter). I will make my model available under creative commons when it's done training.

Twitter profile image: [Book by Julien Deveaux from the Noun Project](https://thenounproject.com/Julihan)



