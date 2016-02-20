import os
import re

import pytumblr
import tumblr_credentials

client = pytumblr.TumblrRestClient(
    os.environ.get('TUMBLR_CONSUMER_KEY', '-1'),
    os.environ.get('TUMBLR_CONSUMER_SECRET', '-1'),
    os.environ.get('TUMBLR_ACCESS_TOKEN', '-1'),
    os.environ.get('TUMBLR_ACCESS_TOKEN_SECRET', '-1')
)

def post_to_tumblr(word, bodytext, source=None):
	bodyhtml = '<p>%s</p>' % bodytext.replace('\n', '</p><p>')
	tags = ['lexiconjure', 'dictionary', 'definition', word]
	if source:
		tags.append(source)
	client.create_text(
		"lexiconjure",
		state="published",
		slug=re.sub(r'\W+', '-', word),
		title=word,
		body=bodyhtml,
		tags=tags
	)

# post_to_tumblr('test', '<p>a test</p><p>this is a test</p>')