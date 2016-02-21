# lexiconjure

[@lexiconjure](https://twitter.com/lexiconjure) is a twitter bot that uses machine learning to define invented words, posting truncated definitions on Twitter and complete ones [on Tumblr](http://lexiconjure.tumblr.com).

It uses an [LSTM](https://en.wikipedia.org/wiki/Long_short-term_memory) neural network trained on the [Oxford English Dictionary](http://www.oed.com/). When you tweet a word (real or made up) @ the bot, you're seeding that generator.

By smashing together random sequences of characters with a genetic algorithm until something that looks (sort of) like a real word comes out, the bot invents its own words to define every 90 minutes.

### Credits

* Bot created and trained by [Ross Goodwin](http://rossgoodwin.com)
* LSTM is [Char-RNN](https://github.com/karpathy/char-rnn) by Andrej Karpathy
* Linguistic-taste integrity moderated by badwords.json via [Darius Kazemi](https://github.com/dariusk/wordfilter)
* Model to be released under creative commons when training is complete
* Profile image: [Book by Julien Deveaux from the Noun Project](https://thenounproject.com/Julihan)



