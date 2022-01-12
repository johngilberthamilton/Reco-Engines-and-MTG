# Reco-Engines-and-MTG

In this project, I test the use of different recommendation systems on building Magic: the Gathering commander decks. Commander is a great fit for this project becuase 
1. you can only include 1 copy of a card in your deck, so it avoids the question of the relative significance of including the first vs the second copy etc.
2. every deck has 99 cards, so not including basic lands that's roughly 80 entries per user and
3. decks can be very distinctly categorized by their commander

The first hurdle was data mining the decks, for which the code is included.

To start, I've tried to create a reco system that tells you what additional cards you should include, and what cards you might take out

Next, I will attempt to look at a commander that has 2 or more distinct builds to see if some sort of clustering yields any results, as well as whether my reco systems work when there are different builds within the same dataset
