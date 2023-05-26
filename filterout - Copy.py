from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import re

# Load stop words
stop_words = set(stopwords.words('english'))

# Add additional stop words
additional_stopwords = [
    'found', 'honeypot?', 'unknown:'
]
stop_words.update(additional_stopwords)

# Tokenize the comment and remove stopwords
def nltk_filter(comment):
    word_tokens = word_tokenize(comment)
    filtered_comment = [w for w in word_tokens if not w.lower() in stop_words]
    return ' '.join(filtered_comment)

# Filter out specific phrases
def regex_filter(comment):
    phrase_to_remove = "Found Honeypot? UNKNOWN:"
    return re.sub(phrase_to_remove, '', comment)

# A list of your comments
comments = [
    # your comments here...
]

# Apply the filter to the comments
filtered_comments = [regex_filter(nltk_filter(comment)) for comment in comments]

for comment in filtered_comments:
    print(comment)
