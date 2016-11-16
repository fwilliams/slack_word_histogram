import urllib2
import json
import argparse
import heapq

parser = argparse.ArgumentParser()
parser.add_argument('--token', type=str)
parser.add_argument('--username', type=str)
parser.add_argument('--channel', type=str, default='random')
parser.add_argument('--limit', type=int, default=0)
args = parser.parse_args()
slack_api_token = args.token

channel_name = args.channel
channel_id = ""
user_name = args.username
user_id = ""

with open("ignore_words.txt", "r") as f:
    stopwords = dict([("%s" % s, "") for s in f.read().split(",")])

words_histogram = dict()


channels = json.loads(urllib2.urlopen("https://slack.com/api/channels.list?token=%s&pretty=1" % slack_api_token).read())
assert channels["ok"], "There was an error fetching the list of channels: %s" % channels["error"]

found = False
for chan in channels["channels"]:
    if chan["name"] == channel_name:
        channel_id = chan["id"]
        found = True
        break
if not found:
    assert False, "Channel named %s does not exist" % channel_name

users = json.loads(urllib2.urlopen("https://slack.com/api/users.list?token=%s&pretty=1" % slack_api_token).read())
assert users["ok"], "There was an error fetching the list of users: %s" % users["error"]

found = False
for user in users["members"]:
    if user["name"] == user_name:
        user_id = user["id"]
        found = True
        break
if not found:
    assert False, "User named %s does not exist" % user_name


has_more_history = True

def get_history(ts=None):
    if ts:
        url = "https://slack.com/api/channels.history?token=%s&channel=%s&latest=%s" % (slack_api_token, channel_id, ts)
    else:
        url = "https://slack.com/api/channels.history?token=%s&channel=%s&pretty=1" % (slack_api_token, channel_id)    
    history = json.loads(urllib2.urlopen(url).read())
    assert history["ok"], "There was an error fetching the channel history for of %s (id %s): %s" % (channel_name, channel_id, channels["error"])

    return history

has_more_history = True
last_ts = None
while has_more_history:
    history = get_history(last_ts)
    for m in history["messages"]:
        try:
            if m["type"] == "message" and m["user"] == user_id:
                text = m["text"]
                words = text.strip().split()
                for w in words:
                    w = w.lower()
                    if w in stopwords:
                        continue
                    if w in words_histogram:
                        words_histogram[w] += 1
                    else:
                        words_histogram[w] = 1
        except KeyError as ke:
            # Bitstrips and the like don't have users associated with them
            assert "user" not in m
            
        last_ts = m["ts"]

    has_more_history = history["has_more"]
    

output = []
for k in words_histogram:
    output.append((words_histogram[k], k))
    
output = sorted(output, reverse=True)

num_print = args.limit if args.limit else len(output)
for w in range(num_print):
    print "%s: %d" % (output[w][1], output[w][0])


