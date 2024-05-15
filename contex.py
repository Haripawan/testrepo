####version 1###

import gensim
from gensim import corpora

# Assuming 'processed_docs' is a list of lists of tokens representing the documents.
# Create a dictionary representation of the documents.
dictionary = corpora.Dictionary(processed_docs)
dictionary.filter_extremes(no_below=15, no_above=0.5, keep_n=100000)

# Convert dictionary into a bag-of-words format.
corpus = [dictionary.doc2bow(doc) for doc in processed_docs]

# Using the LDA model from gensim
lda_model = gensim.models.LdaMulticore(corpus, num_topics=10, id2word=dictionary, passes=2, workers=2)

# For each topic, we will explore the words occuring in that topic and its relative weight.
for idx, topic in lda_model.print_topics(-1):
    print("Topic: {} \nWords: {}".format(idx, topic))
