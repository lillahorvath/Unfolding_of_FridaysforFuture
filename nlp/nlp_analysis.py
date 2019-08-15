# Code used for NLP on 20K tweets with the hashtag #FridaysForFuture published between May and July 2019

# get dependencies 
# ----------------------------------------------------------
import simplejson as json
import pandas as pd
import dill
import re
from spacy.lang.en.stop_words import STOP_WORDS
from sklearn.feature_extraction.text import CountVectorizer
import spacy
import en_core_web_sm
# ----------------------------------------------------------

# get all request outputs 
# (twitter by default returns approximately 500 tweets per request)
# -----------------------------------------------------------------
all_tweets = [dill.load(open('data/tweets_{}.pkd'.format(i), 'rb'))['results'] for i in range(1,42)]
tweets_list = [tweet for tweet_batch in all_tweets for tweet in tweet_batch]

# extract data of interest
# ------------------------

# id and date of tweet
tweets_id = [entry['id'] for entry in tweets_list]
tweets_date = [entry['created_at'] for entry in tweets_list]

# user info
tweets_user = [(entry['user']['id'],
                entry['user']['name'],
                entry['user']['followers_count'], 
                entry['user']['friends_count'], 
                entry['user']['favourites_count'], 
                entry['user']['statuses_count'], 
                entry['user']['created_at']) for entry in tweets_list]

# full text
tweets_ft = [entry['extended_tweet']['full_text'] 
             if entry['truncated'] 
             else entry['text'] 
             for entry in tweets_list]

# strip tweet
def clean_tweet(tw):
    tw1 = re.sub('(@|#)\w+[^\W]|https.+[^\W]|\n|[^\s\w\%\']', ' ', tw)
    tw2 = re.sub('\s\s+', ' ', tw1)
    clean_tw = re.sub('amp', 'and', tw2)
    return clean_tw 
tweets_cft = [clean_tweet(entry) for entry in tweets_ft]

# hashtags
def get_ht(tw):
    return tuple([ht['text'] for ht in tw])
tweets_ht = [get_ht(entry['extended_tweet']['entities']['hashtags']) 
             if entry['truncated'] 
             else get_ht(entry['entities']['hashtags']) 
             for entry in tweets_list]

# user mentions
def get_um(tw):
    if tw:
        return tuple([um['name'] for um in tw])
    return tuple()
tweets_um = [get_um(entry['extended_tweet']['entities']['user_mentions']) 
             if entry['truncated'] 
             else get_um(entry['entities']['user_mentions']) 
             for entry in tweets_list]

# retweets and likes
tweets_rt = [entry['retweet_count'] for entry in tweets_list]
tweets_fav = [entry['favorite_count'] for entry in tweets_list]

# check
assert len(tweets_id) == len(tweets_date) == len(tweets_user) == len(tweets_ft) == len(tweets_cft) == len(tweets_ht) == len(tweets_um) == len(tweets_rt) == len(tweets_fav) 

# create dfs
# ----------

# tweets df
tweets_df = pd.DataFrame(zip(tweets_date, 
                             tweets_ft, 
                             tweets_cft, 
                             tweets_ht, 
                             tweets_um, 
                             tweets_rt, 
                             tweets_fav), 
                  index = [tweets_id], 
                  columns = ['date', 
                             'text', 
                             'clean_text', 
                             'hashtags', 
                             'user_mentions', 
                             'retweets', 
                             'likes'])

# user df
user_df = pd.DataFrame(zip([i[0] for i in tweets_user], 
                           [i[1] for i in tweets_user], 
                           [i[2] for i in tweets_user], 
                           [i[3] for i in tweets_user], 
                           [i[4] for i in tweets_user], 
                           [i[5] for i in tweets_user], 
                           [i[6] for i in tweets_user]),
                  index = [tweets_id], 
                  columns = ['user_id',
                             'user_name',
                             'followers_count', 
                             'following_count', 
                             'favourites_count', 
                             'statuses_count', 
                             'up_created'])

# compute and add popularity score
tweets_df['popularity'] = tweets_df['retweets'] + tweets_df['likes']

# get most and least popular batch of tweets
pop_tweets = tweets_df.sort_values(by=['popularity'])[-5000:]
notpop_tweets = tweets_df.sort_values(by=['popularity'])[:5000]

# analyze language
# ----------------

# stop words
nlp = en_core_web_sm.load()
stop_words_lemma = set(w.lemma_ for w in nlp(' '.join(STOP_WORDS))) 

# tokenizer function
def tokenize_lemma(text):
    return [w.lemma_ for w in nlp(text)]

# bag of words model - most popular tweets
bwv_p = CountVectorizer(max_features=20,
                      stop_words=stop_words_lemma,
                      tokenizer=tokenize_lemma)
counts_p = bwv_p.fit_transform(list(pop_tweets[:]['clean_text'])) 

list_words_p = sorted(bwv_p.vocabulary_.items(), key=lambda x: (x[1], x[0]))
popscore_p = list(np.sum(counts_p.toarray(), axis = 0))

# bag of words model - least popular tweets
bwv_np = CountVectorizer(max_features=20,
                      stop_words=stop_words_lemma,
                      tokenizer=tokenize_lemma)
counts_np = bwv_np.fit_transform(list(notpop_tweets[:]['clean_text'])) 

list_words_np = sorted(bwv_np.vocabulary_.items(), key=lambda x: (x[1], x[0]))
popscore_np = list(np.sum(counts_np.toarray(), axis = 0))

