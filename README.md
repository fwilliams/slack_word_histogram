# (Shitty) Slack word histogram generator

Generate a histogram of words for a slack user.

To use:

```
python histogram_gen.py --token=<your-slack-api-token> --username=<the_user> --channel=<channel_to_crawl> --limit=<top_n_words>
```

Notes:
* The `--channel` argument defaults to random and is optional
* The `--limit` shows only the top `n` words where `n` is the argument. It is optional and by default will show all words