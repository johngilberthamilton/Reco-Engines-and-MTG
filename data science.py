# -*- coding: utf-8 -*-
"""
Created on Wed Dec 29 18:52:26 2021

@author: HAMILJ37
"""
import json
from urllib.request import urlopen
import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt
import statistics as stat
import sys
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics.pairwise import euclidean_distances
from sklearn.metrics.pairwise import pairwise_distances

wg = pd.read_csv('C:/Users/hamilj37/OneDrive - Pfizer/Documents/mtg collab/windgrace_raw.csv')
wg['score'] = 1
# it appears there's a few duplicates
del wg['Unnamed: 0']
wg.drop_duplicates(inplace = True)
#also some issues by some 70 decks having sideboards- i have to go back to the scraping code to fix this, so i'll deal with it later
wg.dropna(inplace = True)
wg = wg[wg.card != 'Sideboard']
wg.reset_index(drop = True)

#john's scores
wg_jgh = pd.read_csv('C:/Users/hamilj37/OneDrive - Pfizer/Documents/mtg collab/jgh windgrace wip.csv')
wg = wg.append(wg_jgh)

wg_pivot = wg.pivot_table(index = 'user', columns = 'card', values = 'score')

populated = wg_pivot.size - wg_pivot.isnull().sum().sum()
size = wg_pivot.size
populated / size

wg_pivot = wg_pivot.fillna(0)

# what should the 100th card in my deck be?
# 1. generate correlation matrix of some kind (one for user and one for item)
# 2. take a list - your own unfinished on
# 3. generate scores based on correlation matrix, either user-based or item-based
#   for a given card not in the deck- 
#   a. user-based- what do the most similar deck think of this card? will need to include more than a few bc it's just ones and 0s- how many out of the 10 most similar users have this in their deck?
#   b. item-based- what does htis deck think about the most similar cards? how many of the 10 most similar cards does it include?

# first step- correlation between 1s and 0s
# tbh not totally sure- i think it makes sense to test different methods. let's just build one for now, based on euclidean distance
# resources- https://en.wikipedia.org/wiki/Similarity_measure
# https://dataaspirant.com/five-most-popular-similarity-measures-implementation-in-python/
# https://brenocon.com/blog/2012/03/cosine-similarity-pearson-correlation-and-ols-coefficients/

wg_pivot_t = wg_pivot.transpose()
wg_euc_cards = euclidean_distances(wg_pivot_t)
wg_euc_cards = pd.DataFrame(wg_euc_cards, index = wg_pivot_t.index, columns = wg_pivot_t.index)

#immediately, i can try to find some fun stuff- what are the  cards that combo/ synergize with each other?
# sheltered thicket- r/g cycle land- i'd expect to find the other cycle lands and graveyard stuff strongly correlated with it
print(wg_euc_cards['Sheltered Thicket'].sort_values().head(10))
# i guess all of these cards do have to deal with graveyards, let's look at something that is maybe less directly related to the very clear objective of the commander
# side note before continuiing- this is clearly working much better than the book data- the sparsity of that data was roughly .018%, where as this magic data has about 2.5%- roughly 140x that
print(wg_euc_cards['Omnath, Locus of Rage'].sort_values().head(10))
print(wg_euc_cards['Ramunap Excavator'].sort_values().head(10))
#hmmm maybe something not in basically all the decks- 
print(wg_euc_cards['Cabal Coffers'].sort_values().head(10))
# now we're getting somewhere- urborg and deserted temple combo af with cabal coffers
print(wg_euc_cards['Boseiju, Who Shelters All'].sort_values().head(10))
# okay so there's a combo build in here
print(wg_euc_cards['Ad Nauseam'].sort_values().head(10))
# so there are 16 ad nauseam decks, and 2 mishra's bauble decks among them
# look at this goofy ass combo deck https://www.mtggoldfish.com/deck/3941802#paper 
# in any case it seems to work well enough to warrant moving forward

#for each user
#for each card
# average the correlation of the all the (other) cards in the user's deck

wg_predict = pd.DataFrame(index = wg_pivot_t.index, columns = wg_pivot_t.columns) # creates empty data frame for scores
wg_predict_2 = wg_predict
count_user = 0 # for timing while it's running
count_item = 0 # for timing while it's running
for user in wg_predict.columns:
    decklist = wg[wg.user == user]
    for cardname, row in wg_predict.iterrows():
        corr_subset = wg_euc_cards[wg_euc_cards.index.isin(decklist.card)][cardname]
        corr_subset = corr_subset[corr_subset.index != cardname]
        corr_subset_df = pd.DataFrame(corr_subset, index = corr_subset.index)
        corr_subset_df['squared'] = corr_subset_df[cardname]**2
        score = corr_subset_df.squared.mean()**.5
        wg_predict.loc[cardname, user] = score
        score_2 = corr_subset_df[cardname].sum()/wg_euc_cards[cardname].sum()
        wg_predict_2.loc[cardname, user] = score_2
        
        
        #problem- while the results of looking at the euclidean distances makes sense intutitively, we need a similarity metric / kernel, ie higher = better
        
        
        #SECOND SCORE IDEA- JUST THE MEAN OF THE EUCLIDEAN DISTANCE / THE COUNT OF (OTHER) CARDS IN THE DECK ALREADY- THIS IS LIKE THE "SCORE" (IE 0S AND 1S) WEIGHTED BY EUC DISTANCE
        #ALSO maybe not all the entire scores- just take the 5 highest correlations for each card- the results would be like cards iwth hihgest potential synergies in your deck- or just the highest scroe- "highest potential craziness for 2 card combo"- ie if you've got splinter twin in your dcek, why not include deceiver exarch?


# after some research and discussions with others, jaccard similarity and simple matching coefficient seem to be useful here. 
# https://scikit-learn.org/stable/modules/metrics.html#metrics - different similarity metrics, as well as converting a distance to a similarity metric 
# 





wg_smc = pairwise_distances(wg_pivot_t, metric = "hamming")
wg_smc = pd.DataFrame(wg_smc, index = wg_pivot_t.index, columns = wg_pivot_t.index)
wg_smc = 1 - wg_smc
print(wg_smc['Ad Nauseam'].sort_values(ascending = False).head(10))


# idea for weighting- sum of include * SMC * # decks it's in / sum SMC * # decks it's in

#quick side bit= create a dictionary with counts of cards
dict_card = wg_pivot.sum().to_dict()
dict_user = wg_pivot_t.sum().to_dict()

wg_predict_smc = pd.DataFrame(index = wg_pivot_t.index, columns = wg_pivot_t.columns) # creates empty data frame for scores
for user in wg_predict_smc.columns:
    decklist = wg[wg.user == user]
    for cardname, row in wg_predict_smc.iterrows():
        card_score = pd.DataFrame(wg_smc[cardname]) #scores for the card in question
        card_score['num_decks'] = [dict_card[x] for x in card_score.index] # create column that weights it according to how many decks each one is in
        card_score['score_weighted'] = card_score[cardname]*card_score['num_decks']
        card_score_decklist = card_score[card_score.index.isin(decklist.card)] #pull all the scores for the specific card for every (other) card in the decklist
        card_score_decklist = card_score_decklist[card_score_decklist.index != cardname]
        score = card_score_decklist.score_weighted.sum()/card_score.score_weighted.sum()
        wg_predict_smc.loc[cardname, user] = score
        
print(wg_predict_smc[wg_predict_smc.index.isin(wg[wg.user == 999999]['card'])][999999].sort_values()) # least valuable cards in deck
print(wg_predict_smc[~wg_predict_smc.index.isin(wg[wg.user == 999999]['card'])][999999].sort_values(ascending = False))


#another idea- cherry pick the card that has the best top 5 scores
#trying two ideas at once- wg_predict_smc_3 can hold the same as the first one, but the # decks is ^.5
wg_predict_smc_2 = pd.DataFrame(index = wg_pivot_t.index, columns = wg_pivot_t.columns) # creates empty data frame for scores
wg_predict_smc_3 = pd.DataFrame(index = wg_pivot_t.index, columns = wg_pivot_t.columns)
for user in wg_predict_smc_2.columns:
    decklist = wg[wg.user == user]
    for cardname, row in wg_predict_smc_2.iterrows():
        card_score = pd.DataFrame(wg_smc[cardname]) #scores for the card in question
        card_score['num_decks'] = [dict_card[x]**.5 for x in card_score.index] # create column that weights it according to how many decks each one is in
        card_score['score_weighted'] = card_score[cardname]*card_score['num_decks']
        card_score_decklist = card_score[card_score.index.isin(decklist.card)] #pull all the scores for the specific card for every (other) card in the decklist
        card_score_decklist = card_score_decklist[card_score_decklist.index != cardname]
        score_2 = card_score_decklist.score_weighted.sum()/card_score.score_weighted.sum()
        wg_predict_smc_2.loc[cardname, user] = score_2
        score_3 = card_score_decklist[cardname].sort_values(ascending = False).head(5).mean()
        wg_predict_smc_3.loc[cardname, user] = score_3

wg_predict_smc.to_csv('C:/Users/hamilj37/OneDrive - Pfizer/Documents/mtg collab/wg_predict_smc.csv')
wg_predict_smc_2.to_csv('C:/Users/hamilj37/OneDrive - Pfizer/Documents/mtg collab/wg_predict_smc_2.csv')
wg_predict_smc_3.to_csv('C:/Users/hamilj37/OneDrive - Pfizer/Documents/mtg collab/wg_predict_smc_3.csv')

wg_predict_smc = pd.read_csv('C:/Users/hamilj37/OneDrive - Pfizer/Documents/mtg collab/wg_predict_smc.csv', index_col = 'card')
wg_predict_smc_2 = pd.read_csv('C:/Users/hamilj37/OneDrive - Pfizer/Documents/mtg collab/wg_predict_smc_2.csv', index_col = 'card')
wg_predict_smc_3 = pd.read_csv('C:/Users/hamilj37/OneDrive - Pfizer/Documents/mtg collab/wg_predict_smc_3.csv', index_col = 'card')

print(wg_predict_smc_2[wg_predict_smc_2.index.isin(wg[wg.user == 999999]['card'])]['999999'].sort_values().head(20))
print(wg_predict_smc_2[~wg_predict_smc_2.index.isin(wg[wg.user == 999999]['card'])]['999999'].sort_values(ascending = False).head(20))

print(wg_predict_smc_3[wg_predict_smc_3.index.isin(wg[wg.user == 999999]['card'])]['999999'].sort_values().head(20))
print(wg_predict_smc_3[~wg_predict_smc_3.index.isin(wg[wg.user == 999999]['card'])]['999999'].sort_values(ascending = False).head(20))

# a few notes
# 1. 3 doesn't work, the results are weird
# 2. i think the structure works, but io htink that i need to dive into a deck that has multiple distinct builds within the commander
# a friend suggested i look at morophon because it's inherently so open-ended