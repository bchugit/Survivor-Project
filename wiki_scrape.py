
from bs4 import BeautifulSoup
import urllib2
import re

import numpy as np
import pandas as pd
import itertools as iter
from IPython import display as dis
import pickle

def parse_td(td):
    # Extract text from table data element
    try:
        # if there is a colspan element present ...
        n = int(td['colspan'])
    except KeyError:
        n = 1
    # (these all end with \n so strip that)
    return [td.text[:-1]] * n  # ... repeat text n times

def get_voting_results(url):
    html= urllib2.urlopen(url)
    soup = BeautifulSoup(html, 'html.parser')
    voting_table = soup.find(id='Voting_History').find_next('table')
    
    # Eliminated
    # find the 'tr' flag right before the 'th' flag with text described by reg. exp.
    # (use iter.chain to flatten list)
    eliminated = list(iter.chain(*[parse_td(i) for i in 
              voting_table
              .find('th', text=re.compile(r"(Voted Out|Eliminated|Voted Off)"))
              .findPrevious('tr').findAll('td')]))
    
    # we want all rows after the row that starts with "Vote:"
    voting_rows = voting_table.find('th', text=re.compile(r"Vote:")).findAllNext('tr')
    # extract the text from all table data in the rows we just extracted
    votes = [list(iter.chain(*[parse_td(i) for i in j.findAll('td')])) for j in voting_rows]
    
    # convert to pandas data frame
    votes = pd.DataFrame(votes)
    # the contestant casting the vote is in the second row - make that the index
    votes.index = votes[1]
    # now we can drop the first two columns
    votes.drop(votes.columns[[0, 1]], inplace=True, axis=1)
    # drop any rows where the index is None
    votes.drop(votes.index[[i == None for i in votes.index]], inplace=True, axis=0)
    # Our columns correspond to those eliminated (from above)
    # There appears to be an extra column. Drop anthing beyoned the elimination info we have
    votes = votes[votes.columns[[range(len(eliminated))]]]
    # rename columns to be the eliminated contestants
    votes.columns = [e.strip() for e in eliminated]
    # find the season number
    summary_table = soup.find('table', {'class': "toccolours"})
    season_num = int(summary_table.find(string=re.compile("Season"))
                                  .find_next('td')
                                  .text.strip())
    
    # Embed Jury Vote info into votes table (otherwise inconsistent)
    # -- to find out how many contestants went to final counsel
    # -- find "Jury Vote" in the episode guide and count the rowspan
    try:
        jury_vote = soup.find(id='Episode_Guide') \
                        .find_next('td', text=re.compile(r"Jury Vote"))
        num_at_final_counsel = int(jury_vote['rowspan'])
        if 'Cambodia' not in url:  # This is the current season
            votes.iloc[:num_at_final_counsel, -num_at_final_counsel:] = "Jury Vote"
    except TypeError:
        # This catches current season, which hasn't gone to jury yet
        pass
    
    return votes, season_num

def get_season_info(url):
    html= urllib2.urlopen(url)
    soup = BeautifulSoup(html, 'html.parser')
    # collect all link references that begin with /wiki/Survivor:
    season_refs = set(
        [i['href'] for i in soup.findAll('a', {'href': re.compile("^/wiki/Survivor:")})]
    )
    # we get the season url by adding the following prefix
    prefix = "http://survivor.wikia.com"
    season_urls = [prefix + i for i in list(season_refs)]
    # create a dictionary of this info
    seasons = {}
    for url in season_urls:
        name = url.split(':_')[-1]
        seasons[name] = {}
        seasons[name]['url'] = url
    del seasons['Heroes_vs._Villains']  # this one is a repeat
        
    return seasons

def scrape(url="http://survivor.wikia.com/wiki/Main_Page"):
    seasons = get_season_info(url)
    
    for i in seasons.keys():
        season = seasons[i]  #A dictionary
        season['votes'], season['num'] = get_voting_results(season['url'])
    
    return seasons
    