"""
Python interpretation of / solution for https://github.com/islemaster/good-enough-golfers
Original JavaScript code by Brad Buchanan https://github.com/islemaster
https://github.com/islemaster/good-enough-golfers/blob/master/lib/geneticSolver.js
"""

import math
import random
import functools
import copy

GENERATIONS = 30
RANDOM_MUTATIONS = 2
MAX_DESCENDANTS_TO_EXPLORE = 100

# init variables
weights = 0
groupCost = 0
mutations = []

def forEachPair(array, callback):
    # array = group to check. loops iterate through every pair in group
    for i in range(len(array)):
        for j in range(i + 1, len(array)):
            # callback = given function applied to each pair
            callback(array[i], array[j])

def geneticSolver(groups, ofSize, forRounds, forbiddenPairs=[], discouragedGroups=[]):
    totalSize = groups * ofSize
    groupCost = 0

    def score(curRound, weights):
        def getGroupCost(group):
            global groupCost
            groupCost = 0

            def addPairWeights(a, b):
                global groupCost
                # add exponent of pair weight to group cost
                groupCost += math.pow(weights[a][b], 2)
                return groupCost

            forEachPair(group, addPairWeights)
            return groupCost

        groupScores = list(map(getGroupCost, curRound))
        scoreDict = dict(groups=curRound,
                         groupsScores=groupScores,
                         total=functools.reduce(lambda sSum, sNext: sSum + sNext, groupScores, 0))
        return scoreDict

    def swap(groups, i, j):
        copyList = copy.deepcopy(groups)
        copyList[math.floor(i / ofSize)][i % ofSize] = groups[math.floor(j / ofSize)][j % ofSize]
        copyList[math.floor(j / ofSize)][j % ofSize] = groups[math.floor(i / ofSize)][i % ofSize]
        return copyList

    def generatePermutation():
        # create array of values and shuffle randomly
        people = list(range(groups * ofSize))
        random.shuffle(people)
        return list(map(lambda i: list(map(lambda j: people[i * ofSize + j], list(range(ofSize)))), list(range(groups))))

    # called by generateMutations
    def findCandidate(candidate):
        global mutations
        # calls function with each element in list (1 positional arg)
        scoredGroups = list(map(lambda g, x: dict(group=g, score=x), candidate.get("groups"), candidate.get("groupsScores")))
        sortedScoredGroups = sorted(scoredGroups, key=lambda sg: sg.get("score"), reverse=True)
        sortedFinal = list(map(lambda ssg: ssg.get("group"), sortedScoredGroups))

        # Always append the original candidate back onto the list
        mutations.append(candidate)

        # Add every mutation that swaps somebody out of the most expensive group
        # (The first group is the most expensive now that we've sorted them)
        for i in range(ofSize):
            for j in range(ofSize, totalSize):
                mutations.append(score(swap(sortedFinal, i, j), weights))

        # Add some random mutations to the search space to help break out of local peaks
        for i in range(RANDOM_MUTATIONS):
            mutations.append(score(generatePermutation(), weights))

    def generateMutations(candidates, weights):
        global mutations
        mutations = []
        list(map(findCandidate, candidates))
        return mutations

    def updatePairWeights(a, b):
        weights[a][b] = weights[b][a] = (weights[a][b] + 1)
        # need return value?
        # return

    def updateWeights(roundGroups, weights):
        for group in roundGroups:
            forEachPair(group, updatePairWeights)

    # fix
    def mapWeights(s):
        fillList = list(range(totalSize))
        for index, val in enumerate(fillList):
            fillList[index] = 0
        return fillList

    # initialize list of weights
    weights = list(map(mapWeights, list(range(totalSize))))

    ''' # No functionality currently
    # Fill some initial restrictions
    forbiddenPairs.forEach(lambda group:
        forEachPair(group, lambda (a, b):
            if a >= totalSize or b >= totalSize:
                return
            weights[a][b] = weights[b][a] = Infinity

    discouragedGroups.forEach(lambda group:
        forEachPair(group, lambda (a, b):
            if a >= totalSize or b >= totalSize:
                return
            weights[a][b] = weights[b][a] = (weights[a][b] + 1)
    '''

    # initialize lists
    rounds = []
    roundScores = []

    # fix
    def mapTopOptions(s):
        return score(generatePermutation(), weights)

    # PRIMARY LOOP
    for round in range(forRounds):
        topOptions = list(map(mapTopOptions, list(range(5))))
        generation = 0
        while generation < GENERATIONS and topOptions[0].get("total") > 0:
            # generate list of candidates
            candidates = generateMutations(topOptions, weights)
            sortByCand = sorted(candidates, key=lambda c: c.get("total"), reverse=False)
            bestScore = sortByCand[0].get("total")
            # Reduce to all the options that share the best score
            dropIndex = len(sortByCand)-1
            for i, cand in enumerate(sortByCand):
                # if total is larger (worse) than best score, save index and break for loop
                if cand.get("total") > bestScore:
                    dropIndex = i
                    break
            topOptions = sortByCand[0:dropIndex]
            # Shuffle those options and only explore some maximum number of them
            random.shuffle(topOptions)
            topOptions = topOptions[0:MAX_DESCENDANTS_TO_EXPLORE]
            generation += 1

        bestOption = topOptions[0]
        rounds.append(bestOption.get("groups"))
        roundScores.append(bestOption.get("total"))
        updateWeights(bestOption.get("groups"), weights)

    return rounds, roundScores

''' RUN PROGRAM (ex) '''
calcRounds, calcScores = geneticSolver(4, 4, 6)
print(calcRounds)
print(calcScores)
