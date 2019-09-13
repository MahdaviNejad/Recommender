from math import sqrt
import copy

def getNeighbours(prefs,userid,bookid, n=5):
    orgscores = [(similarity(prefs,userid,other),other)
                for other in prefs if other != userid]
    scores = {}
    for sim, userid in orgscores:
        if bookid in prefs[userid].keys():
            scores[userid] = sim
    scores = sorted(scores.items(), key=lambda d:d[1])
    scores.reverse()
    return scores[0:n]

def similarity(prefs,p1,p2):
    si = {}
    for item in prefs[p1]:
        if item in prefs[p2]: 
            si[item] = 1

    if len(si) == 0:
        return 0

    n = len(si)

    sum1 = sum([prefs[p1][it] for it in si])
    sum2 = sum([prefs[p2][it] for it in si])

    sum1Sq = sum([pow(prefs[p1][it],2) for it in si])
    sum2Sq = sum([pow(prefs[p2][it],2) for it in si])

    pSum = sum([prefs[p1][it] * prefs[p2][it] for it in si])

    num = pSum - (sum1 * sum2/n)
    den = sqrt((sum1Sq - pow(sum1,2)/n) * (sum2Sq - pow(sum2,2)/n))

    if den == 0:
        return 0
    r = num/den

    if r < 0:
        r = 0
    return r

def convertScale(rating):
    scale = {
        '0': -1,
        '-5': 0.00,
        '-3': 0.25,
        '1': 0.50,
        '3': 0.75,
        '5': 1.00,
    }
    return scale[rating]

def loadDataset(path=""):
    books = []
    for line in open(path+"books.txt"):
        line  = line.strip('\n').strip()
        books.append(line)
    testPrefs = {}
    prefs = {}
    users = []
    index = 1
    userid = 0
    for line in open(path+"books.txt"):
        line  = line.strip('\n').strip()
        if index % 2 == 1:
            users.append(line)
            index += 1
            continue 
        ratings = line.split(" ")
        testRatings = {}
        allRatings = {}
        count = 0
        bookid = 0
        valid = 0
        for rating in ratings:
            if rating != '0' and count < 2:
                testRatings[bookid] = convertScale(rating)
                allRatings[bookid] = convertScale(rating)
                count += 1
            else:
                if rating != '0':
                    valid = 1
                    allRatings[bookid] = convertScale(rating)
            bookid += 1
        if valid == 1:
            testPrefs[userid] = testRatings
        prefs[userid] = allRatings
        userid += 1
        index += 1
    return testPrefs,prefs,users,books

def predict(prefs, userid, bookid, neighbours):
    sumSim = 0
    for uid, sim in neighbours:
        sumSim += sim
    if sumSim == 0:
        return -1
    weight = {}
    rating = 0
    for uid, sim in neighbours:
        weight[uid] = sim/sumSim
        if bookid in prefs[uid].keys():
            if prefs[uid][bookid] != -1:
                rating += prefs[uid][bookid] * weight[uid]
    return rating

def generateTrainPrefs(prefs, userid, items):
    trainPrefs = copy.deepcopy(prefs)
    for key in items.keys():
        trainPrefs[userid].pop(key)
    return trainPrefs

def rmse(predictRatings, realRatings):
    predictRatingList = []
    for userid, items in predictRatings.items():
        for itemid, value in items.items():
            predictRatingList.append(value)

    realRatingList = []
    for userid, items in realRatings.items():
        for itemid, value in items.items():
            realRatingList.append(value)
    return sqrt(sum([(f - o) ** 2 for f, o in zip(predictRatingList, realRatingList)]) / len(predictRatingList))

def evaluation_mean(testPrefs, prefs):
    rating = {}
    ratings = {}
    count = {}

    for (userid, items) in testPrefs.items():
        rating.setdefault(userid, {})
        count.setdefault(userid, {})
        for (bookid, value) in items.items():
            rating[userid][bookid] = 0
            count[userid][bookid] = 0

    for testUserid in testPrefs.keys():
        rating.setdefault(testUserid, {})
        for (userid, items) in prefs.items():
            if userid == testUserid:
                continue
            for (bookid,value) in items.items():
                if bookid in rating[testUserid].keys() and value != -1:
                    rating[testUserid][bookid] += value
                    count[testUserid][bookid] += 1
    for testUserid in testPrefs.keys():
        for bookid in rating[testUserid].keys():
            rating[testUserid][bookid] = rating[testUserid][bookid]/count[testUserid][bookid]
        ratings[testUserid] = rating[testUserid]
            
    return rmse(ratings, testPrefs)

def evaluation_cf(testPrefs, prefs, neighbour_num = 5):
    ratings = {}
    missUser = []
    validTestPrefs = {}
    for userid in testPrefs.keys():
        trainPrefs = generateTrainPrefs(prefs, userid, testPrefs[userid])
        ratings.setdefault(userid, {})
        for bookid in testPrefs[userid].keys():
            neighbours = getNeighbours(trainPrefs, userid, bookid, neighbour_num)
            ratings[userid][bookid] = predict(trainPrefs, userid, bookid, neighbours)

            if ratings[userid][bookid] == -1:
                ratings.pop(userid)
                missUser.append(userid)
                break
        validTestPrefs[userid] = testPrefs[userid]
    return rmse(ratings, validTestPrefs)

if __name__ == '__main__':
    testPrefs,prefs,users,_ = loadDataset("")
    print evaluation_mean(testPrefs, prefs)
    print evaluation_cf(testPrefs, prefs, 5);
    print evaluation_cf(testPrefs, prefs, 10);

    
    
