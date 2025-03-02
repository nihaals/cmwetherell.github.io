from sys import getallocatedblocks

from prometheus_client import Summary
# from grandPrix import GrandPrix
from candidatesTorunament import Candidates
from candidatesTorunament import getCandidates

from norwayChess import Norway
from norwayChess import getNorway

from superbetClassic import Superbet
from superbetClassic import getSuperbet

from sinquefieldCup import SCup
from sinquefieldCup import getPlayers

import pandas as pd
import plotly
import plotly.express as px
import pickle
import numpy as np

def summarizeCurrent(games):

    playersCopy = getCandidates()
    # print(playersCopy[1])
    # print(playersCopy[1])
    gamesCopy = games.copy()

    playersCopy['Ding Liren'].EloC = 2806
    playersCopy['Firouzja'].EloC = 2793
    playersCopy['Caruana'].EloC = 2783
    playersCopy['Nepomniachtchi'].EloC = 2766
    playersCopy['Duda'].EloC = 2750
    playersCopy['Radjabov'].EloC = 2753
    playersCopy['Rapport'].EloC = 2764
    playersCopy['Nakamura'].EloC = 2760

    gamesCopy = gamesCopy[gamesCopy.played == 1]

    for _, row in gamesCopy.iterrows():
        whitePlayer = playersCopy[row.whitePlayer]
        blackPlayer = playersCopy[row.blackPlayer]

        whiteElo = getattr(whitePlayer, 'EloC') 
        blackElo = getattr(blackPlayer, 'EloC')

        whitePlayer.addGame(row.result, whiteElo, blackElo, 'c')
        blackPlayer.addGame((1 - row.result), blackElo, whiteElo, 'c')

    gamesCopy['blackWin'] = 0

    whiteResults = gamesCopy[['whitePlayer', 'blackPlayer', 'result', 'blackWin']].values
    blackResults = gamesCopy[['blackPlayer', 'whitePlayer', 'result', 'blackWin']].values
    blackResults[:, 2] = 1 - blackResults[:, 2] # to change the game results to black player POV
    blackResults[:, 3] = 1 * (blackResults[:, 2] == 1) #checking for black wins, used for tb
    
    tbrrSummary = pd.DataFrame(np.concatenate(
        (whiteResults, blackResults)
        , axis = 0))
    tbrrSummary.columns = ['name', 'oppName','result', 'blackWin']
    tbrrSummary['wins'] = 1 * (tbrrSummary.result == 1)

    tmpScores = tbrrSummary.groupby(['name']).agg(
        score = ('result','sum')).reset_index() # df[name, score]

    #add SB tiebreak, move sort values code to this df
    tbrrSummary['sbPoints'] = 0
    for idx, row in tbrrSummary.iterrows():
        tbrrSummary.at[idx, 'sbPoints'] = row.result * tmpScores.loc[tmpScores.name == row.oppName, 'score'].values[0]

    tbrrSummary = tbrrSummary.groupby(['name']).agg( #using more sorting mechanisms than needed, but still advancing everyone with same score to TBs
        score = ('result','sum'),
        sb = ('sbPoints', 'sum'),
        wins = ('wins','sum'),
        blackWins = ('blackWin','sum'),
        ).reset_index()

    tprSummary = pd.DataFrame([[playerZ.name, playerZ.performance()] for (_, playerZ) in playersCopy.items()], columns = ['name', 'tpr'])
    return pd.merge(tprSummary, tbrrSummary).sort_values(by = ['score', 'sb', 'wins', 'blackWins'], ascending = False)

def simCandidatesTournament(games): #_ is because map has to pass an argument to the function
    candidates = getCandidates()
    tournament = Candidates(candidates, games)
    tournament.simCandidates()
    return tournament.winner, tournament.second, tournament.tie


def simSCup(games): #_ is because map has to pass an argument to the function
    players = getPlayers()
    tournament = SCup(players, games)
    tournament.simCup()
    return tournament.winner, tournament.gctWinner

def simNorway(_): #_ is because map has to pass an argument to the function
    players = getNorway()
    tournament = Norway(players)
    tournament.simNorway()
    return tournament.winner, tournament.magnus, tournament.newElo

def simSuperbet(games): #_ is because map has to pass an argument to the function
    players = getSuperbet()
    tournament = Superbet(players, games)
    tournament.simSuperbet()
    return tournament.winner, 0, tournament.newElo

'''
 def simGrandPrix(playerData, overridePool = False, gameData = None):

    GP3 = GrandPrix(playerData, 'event3', overridePool, gameData)
    GP3.simGP()

    finalStandings = pd.concat([playerData[(playerData.event2 == 1) & (playerData.event3 == 0)], GP3.players]).reset_index(drop = True)

    finalStandings['gpScore'] = 0
    finalStandings['event2Points'] = finalStandings['event2Points'].fillna(0)
    finalStandings['event3Points'] = finalStandings['event3Points'].fillna(0)
    finalStandings['gpScore'] = finalStandings.event1Points + finalStandings.event2Points + finalStandings.event3Points

    finalStandings.TF = 1*(finalStandings.event1Points == 13) + 1*(finalStandings.event2Points == 13) + 1*(finalStandings.event3Points == 13)
    finalStandings.TS = 1*(finalStandings.event1Points == 10) + 1*(finalStandings.event2Points == 10) + 1*(finalStandings.event3Points == 10)

    fs = finalStandings.sort_values(by = ['gpScore','TF', 'TS', 'GP', 'GW'], ascending = False).reset_index(drop = True)
    
    fs['Qualify'] = "DNQ"
    fs.loc[fs.Name == fs.Name[0], 'Qualify'] = "First"
    fs.loc[fs.Name == fs.Name[1], 'Qualify'] = "Second"

    return fs, GP3.gameData, pd.DataFrame(GP3.koGames, columns = ['whitePlayer', 'blackPlayer', 'result', 'koType'])
'''

## Want to add code that exports MD for table under each scenario for each pool game.

def toMD(current, standings, hash):

    hash_pool = set(pd.util.hash_pandas_object(current[current.played==1])) # gets a hash for each row of the df where the pool game was played
    # standings = pickle.load(open( "./chess-sim/data/sims/standings.p", "rb" ) )
    # koGames = pickle.load(open( "./chess-sim/data/sims/koGames.p", "rb" ) )
    # poolGames = pickle.load(open( "./chess-sim/data/sims/poolGames.p", "rb" ) )
    # simHashesPool = pickle.load(open( "./chess-sim/data/sims/simHashesPool.p", "rb" ) )   
    # simHashesKO = pickle.load(open( "./chess-sim/data/sims/simHashesKO.p", "rb" ) )   

    simMatchPool = [ind for ind, simHash in enumerate(hash) if hash_pool <= simHash] # checks if all the played games match that simulations games
    # simMatchKO = [ind for ind, simHash in enumerate(simHashesKO) if hash_ko <= simHash] # checks if all the played games match that simulations games

    standings = [standings[i] for i in simMatchPool]
    # poolGames = [poolGames[i] for i in simMatchPool]
    # koGames = [koGames[i] for i in simMatchPool]

    standings = pd.concat(standings)

    # standings['Wins'] = 1 * (standings.event3Points==13) # TODO should move this to simulation function

    df = standings[['Name', 'Qualify', 'gpScore']].groupby(["Name", "Qualify", "gpScore"]).size().to_frame('Frequency').reset_index()

    area_df = pd.pivot_table(df, values='Frequency', index=['Name', 'gpScore'], columns=['Qualify'], aggfunc='mean').reset_index().fillna(0)

    # area_df = area_df.head(100)
    nSims = df.Frequency.sum() / len(df.Name.unique())

    area_df.DNQ = area_df.DNQ / nSims
    area_df.First = area_df.First / nSims
    area_df.Second = area_df.Second / nSims

    area_df.Name[area_df.Name == 'Étienne Bacrot'] = 'Etienne Bacrot'
    area_df.Name[area_df.Name == 'Richárd Rapport'] = 'Richard Rapport'
    area_df.Name[area_df.Name == 'Leinier Domínguez'] = 'Leinier Dominguez'

    scores = area_df.gpScore.unique()
    names = area_df.Name.unique()

    need = []
    for x in names:
        for y in scores:
            need.append([x, y])
    df = pd.DataFrame(need, columns = ["Name", "Score"])
    df['DNQ'] = 0.000
    df['Second'] = 0.000
    df['First'] = 0.000

    for i, row in df.iterrows():
        DNQ, Second, First = 0,0,0
        
        
        if len(area_df['DNQ'][(area_df.Name == row.Name) & (area_df.gpScore == row.Score)]) > 0:
            DNQ = area_df['DNQ'][(area_df.Name == row.Name) & (area_df.gpScore == row.Score)].item()
        if len(area_df['Second'][(area_df.Name == row.Name) & (area_df.gpScore == row.Score)]) > 0:
            Second = area_df['Second'][(area_df.Name == row.Name) & (area_df.gpScore == row.Score)].item()
        if len(area_df['First'][(area_df.Name == row.Name) & (area_df.gpScore == row.Score)]) > 0:
            First = area_df['First'][(area_df.Name == row.Name) & (area_df.gpScore == row.Score)].item()
        # print(DNQ)

        df.at[i,'DNQ'] = DNQ
        df.at[i,'Second'] = Second
        df.at[i,'First'] = First

    df.sort_values(by = ['Name', 'Score'], axis=0, ascending=True, inplace=True)
    qualifiers = df.Name[(df.Second > 0)| (df.First > 0)].unique()
    df = df[df.Name.isin(qualifiers)]

    export = pd.DataFrame([[name, 
                        100*(df.Second[df.Name == name].sum() + df.First[df.Name == name].sum()),
                        ( # Expected Points
                        df.Score[df.Name == name] * 
                         (df.DNQ[df.Name == name].values + df.Second[df.Name == name].values + df.First[df.Name == name].values)
                        ).sum(),
                       ] for name in df.Name.unique()],
             columns = ['Name', 'Qualify', 'Expected GP Points']).sort_values(by=['Qualify','Expected GP Points'], ascending = False).reset_index(drop=True)

    export = export[export.Qualify > 0]

    return nSims, export.to_markdown(index = False, floatfmt = "#.1f")