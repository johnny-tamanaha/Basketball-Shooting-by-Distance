'''Scrape individual shooting efficiency data from basketball-reference.com'''
import numpy as np 
import pandas as pd 
from urllib.request import urlopen
from bs4 import BeautifulSoup, Comment

def scrape_players(letters):
    '''Scrape player names that begin with a given set of letters.
Arguments:
    1. letters (list-like object) -> names that begin with letters in letters will be scraped into players.csv
Scraped Data:
    1. players.csv -> single columns (names) of scraped names
Excluded names:
    1. Contains non-english symbols
    2. Contains periods
    3. Contains dashes'''

    players = []

    for letter in letters:
        url = r'https://www.basketball-reference.com/players/{}/'.format(letter)
        try:
            html = urlopen(url)
        except:
            print('Letter ->', letter, '| Load -> Failure')
            continue
        # Reference -> https://towardsdatascience.com/web-scraping-nba-stats-4b4f8c525994
        # ************************************************************************************
        soup = BeautifulSoup(html, features='html5lib')
        rows = soup.findAll('tr')[1:]
        # ************************************************************************************
        players_raw = [[a.getText() for a in rows[i].find_all('th')[0].find_all('a')] for i in range(len(rows))]
        alpha = [chr(n) for n in range(97, 97+26)] + [' '] + [chr(n) for n in range(65, 65+26)]
        for name in players_raw:
            if all(c in alpha for c in name[0]):
                players.append(name[0])
        print('Letter ->', letter, '| Load -> Success')

    df = pd.DataFrame(players, columns=['name'])
    df.to_csv('players.csv')

def scrape_shooting(csv):
    '''Scrape player shooting data.
Arguments:
    1. csv (string) -> name of csv file with player data
Scraped Data:
    1. shooting.csv -> concatenated shooting tables
        Season -> year of observation
        Age -> age
        Tm -> team 
        L -> leage
        Pos -> individual player position
            PG -> point Guard
            SG -> shooting Guard
            SF -> small Forward
            PF -> power Forawrd
            C -> center
        G -> games played
        MP -> minutes played
        FG% -> overall field goal percentage
        dist -> overall average shot distance
        %2PA -> 2-point shot frequency
        %0-3A -> 0-3 ft. shot frequency
        %3-10A -> 3-10 ft. shot frequency
        %10-16A -> 10-16 ft. shot frequency
        %10-3ptA -> 16 ft. - 3-point line shot frequency
        %3PA -> 3-point shot frequency
        2P% -> 2-point field goal percentage
        0-3% -> 0-3 ft. shot field goal percentage
        3-10% -> 0-10 ft. shot field goal percentage
        10-16% -> 10-16 ft. shot field goal percentage
        16-3pt% -> 16 ft. - 3-point line field goal percentage
        3P% -> 3-point field goal percentage
        Dunks%Ast\'d -> percentage of assisted dunks
        %DunksA -> dunk frequency
        Dunks_Md -> amount of made dunks
        Corner%Ast\'d -> percentage of assisted corner threes
        %CornerA -> corner three frequency
        Corner3P% -> corner three field goal percentage
        HeavesAtt -> amount of attempted heaves
        HeavesMd -> amount of made heaves
Errors:
    1. Error (404 Not Found) -> url doesn't exist
    2. Error (Shooring Missing) -> Shooting table doesn't exist'''

    players = pd.read_csv(csv)
    success_count = 0 
    failure_count = 0
    data = pd.DataFrame(columns=['Unnamed: 0_level_1/Season',
                                 'Unnamed: 1_level_1/Age',
                                 'Unnamed: 2_level_1/Tm',
                                 'Unnamed: 3_level_1/Lg',
                                 'Unnamed: 4_level_1/Pos',
                                 'Unnamed: 5_level_1/G',
                                 'Unnamed: 6_level_1/MP',
                                 'Unnamed: 7_level_1/FG%',
                                 'Unnamed: 8_level_1/Dist.',
                                 '% of FGA by Distance/2P',
                                 '% of FGA by Distance/0-3',
                                 '% of FGA by Distance/3-10',
                                 '% of FGA by Distance/10-16',
                                 '% of FGA by Distance/16-3pt',
                                 '% of FGA by Distance/3P',
                                 'FG% by Distance/2P',
                                 'FG% by Distance/0-3',
                                 'FG% by Distance/3-10',
                                 'FG% by Distance/10-16',
                                 'FG% by Distance/16-3pt',
                                 'FG% by Distance/3P',
                                 'Unnamed: 21_level_1/%Ast\'d',
                                 'Dunks/%FGA',
                                 'Dunks/Md.',
                                 'Unnamed: 24_level_1/Ast\'d',
                                 'Corner/%3PA',
                                 'Cornder/3P%',
                                 'Heaves/Att.',
                                 'Heaves/Md.'])

    for name in players['name']:
        # Generate url based on player name
        first = name.split(' ')[0].lower()
        if len(first) > 2:
            first = first[0:2]
        last = name.split(' ')[1].lower()
        if len(last) > 5:
            last = last[0:5]
        url = r'https://www.basketball-reference.com/players/{}/{}{}01.html'.format(last[0], last, first)

        try:
            html = urlopen(url)
        except:
            print('Player ->', name, '| Load -> Error (404 Not Found)')
            failure_count += 1
            continue

        soup = BeautifulSoup(html, features='html5lib')

        # Shooting efficiency table is embedded in comments
        # Reference -> https://stackoverflow.com/questions/61606829/python-beautifulsoup-tables-not-parsing
        # ***************************************************************************************************
        comments = soup.find_all(string=lambda text: isinstance(text, Comment))
        tables = ''
        for c in comments:
            if '<table' in c:
                tables += c
        soup = BeautifulSoup(tables, 'html5lib')
        shootingTable = soup.find('table', {'id':'shooting'})
        # ***************************************************************************************************

        # Check if table exists
        try:
            # Reference -> https://stackoverflow.com/questions/61606829/python-beautifulsoup-tables-not-parsing
            # ****************************************************************************************************
            df = pd.read_html(str(shootingTable))[0]
            # ****************************************************************************************************
        except:
            failure_count += 1
            print('Player ->', name, '| Load -> Error (Shooting Missing)')
            continue
        df.columns = df.columns.droplevel()
        df.columns = df.columns.map('{0[0]}/{0[1]}'.format)
        df = df[df.index < (df.index[df['Unnamed: 0_level_1/Season']=='Career'][0])]
        data = pd.concat([data, df], ignore_index=True, sort=True)
        success_count += 1
        print('Player ->', name, '| Load -> Success')
    
    print()
    print('Number of Successful Loads:', success_count)
    print('Number of Failed Loads:', failure_count)
    data.to_csv('shooting.csv')

if __name__ == '__main__':
    letters = [chr(n) for n in range(97, 97+26) if n != 120]
    scrape_players(letters)
    scrape_shooting('players.csv') 