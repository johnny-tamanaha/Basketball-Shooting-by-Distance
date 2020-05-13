'''Clean individual shooting efficiency data from basketball-reference.com'''
import numpy as np 
import pandas as pd 

def convert_pos(pos):
    if pos[0] == 'C':
        return 5
    positions = ['PG', 'SG', 'SF', 'PF']
    return positions.index(pos[0:2]) + 1

def clean_shooting(csv):
    '''Clean player shooting data
Arguments:
    1. csv (string) -> name of csv with shooting data
Cleaned Data:
    1. shooting_clean.csv -> cleaned shooting data
        Season -> year of observation
        Pos -> individual player position
            PG -> point Guard
            SG -> shooting Guard
            SF -> small Forward
            PF -> power Forawrd
            C -> center
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
        MPG -> minutes per game
Excluded Data:
    1. Observations with less than 12 minutes per game were omitted from the dataset'''
    df = pd.read_csv(csv, index_col=0)
    df.columns = ['%0-3A',
                  '%10-16A',
                  '%16-3ptA',
                  '%2PA',
                  '%3-10A',
                  '%3PA',
                  'Corner1',
                  'Corner2',
                  'Corner3',
                  'Dunk1',
                  'Dunk2',
                  '0-3%',
                  '10-16%',
                  '16-3pt%',
                  '2P%',
                  '3-10%',
                  '3P%',
                  'Heaves1',
                  'Heaves2',
                  'Season',
                  'Age',
                  'Ast1',
                  'Ast2',
                  'Ast3',
                  'Tm',
                  'Lg',
                  'Pos',
                  'G',
                  'MP',
                  'FG%',
                  'Dist']
    df = df[['Season',
            'Pos',
            'G',
            'MP',
            '%2PA',
            '%0-3A',
            '%3-10A',
            '%10-16A',
            '%16-3ptA',
            '%3PA',
            '2P%',
            '0-3%',
            '3-10%',
            '10-16%',
            '16-3pt%',
            '3P%']]

    df['MPG'] = df['MP']/df['G']
    del df['MP']
    del df['G']
    df = df[df['MPG'] >= 12]

    df['Season'] = df['Season'].map(lambda x: int(x[-2:]))
    df['Pos'] = df['Pos'].map(convert_pos)

    percentages = ['%2PA',
                '%0-3A',
                '%3-10A',
                '%10-16A',
                '%16-3ptA',
                '%3PA',
                '2P%',
                '0-3%',
                '3-10%',
                '10-16%',
                '16-3pt%',
                '3P%']

    for p in percentages:
        invalid_p = df[df[p] < 0].index
        df = df.drop(invalid_p)
        invalid_p = df[df[p] > 1].index
        df = df.drop(invalid_p)
    df.to_csv('shooting_clean.csv')

if __name__ == '__main__':
    clean_shooting('shooting.csv')