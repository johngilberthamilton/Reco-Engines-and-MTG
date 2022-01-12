# -*- coding: utf-8 -*-
"""
Created on Wed Jan 12 12:51:46 2022

@author: HAMILJ37
"""

from bs4 import BeautifulSoup
import requests
import re
import pandas as pd

url_endnum = 'https://www.mtggoldfish.com/deck/custom?mformat=commander&commander=Lord+Windgrace#paper'
res_endnum = requests.get(url_endnum)
soup_endnum = BeautifulSoup(res_endnum.text)
end_number = int(soup_endnum.select('.page-link')[6].contents[0])




df_master = pd.DataFrame(columns = ['card', 'user'])

# warning- this makes many calls to the mtg goldfish server, it seems you get throttled after 5k, or maybe it's rate-based. 
# I really should be adding headers here to go under any detection they have, but I just got lazy (this first dataset was only about 7k decks)
for i in range(22,end_number):
    i2 = i + 1
    url = 'https://www.mtggoldfish.com/deck/custom/commander?commander=Lord+Windgrace&page='+str(i2) #each page of search results
    res = requests.get(url)
    soup = BeautifulSoup(res.text)
    #get list of decks
    decks = []
    for a in soup.find_all('a', href = True):
        if re.search('/deck/[0-9]+$', a['href']):
            decks.append(a['href'][6:100])
    #loop through all decks' pages to pull all cards
    df_page = pd.DataFrame(columns = ['card', 'user'])
    for user in decks:
        url2  = 'https://www.mtggoldfish.com/deck/arena_download/'+user
        res2 = requests.get(url2)
        soup2 = BeautifulSoup(res2.text)
        text2 = soup2.select('.copy-paste-box')
        text3 = str(text2[0].contents[0])
        decklist = text3.split('\n')
        del decklist[0:4]
        for j in range(len(decklist)):
            x = decklist[j].find(' ')+1
            decklist[j] = decklist[j][x:100] #trimmming count of cards off the 
        df = pd.DataFrame(decklist, columns = ['card'])
        df['user'] = user
        df_page = df_page.append(df)
        print('page '+str(i2)+': deck #'+str(user))
    df_master = df_master.append(df_page)
    
df_master.to_csv('C:/Users/hamilj37/OneDrive - Pfizer/Documents/mtg collab/windgrace_raw.csv')
