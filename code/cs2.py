import pandas as pd
import numpy as np


def genDurationPairList(listType, tempSent, spreadTempI='', spreadTempII='', nextCycle=False, timeSpread=False, numEpochs=1):

    pairList = []
    multiTimeListCond = listType in ['day_time', 'month']

    for _ in range(numEpochs):

        if listType == 'day_time':
            timeList1, timeList2 = (allListDict['day_time_12'], allListDict['day_time_24']) if (
                np.random.rand() > 0.5) else (allListDict['day_time_24'], allListDict['day_time_12'])
        elif listType == 'month':
            timeList1, timeList2 = (allListDict['month_full'], allListDict['month_abv']) if (
                np.random.rand() > 0.5) else (allListDict['month_abv'], allListDict['month_full'])
        else:
            timeList = allListDict[listType]

        timeInd1, timeInd2 = np.random.choice((range(len(
            timeList1)) if multiTimeListCond else range(len(timeList))), size=2, replace=False)

        if not nextCycle:
            timeInd1, timeInd2 = (timeInd1, timeInd2) if (
                timeInd1 < timeInd2) else (timeInd2, timeInd1)
            goldDuration = timeInd2 - timeInd1
        else:
            timeInd1, timeInd2 = (timeInd1, timeInd2) if (
                timeInd1 > timeInd2) else (timeInd2, timeInd1)
            goldDuration = (len(timeList1) if multiTimeListCond else len(
                timeList)) - timeInd1 + timeInd2

        time1, time2 = (timeList1[timeInd1], timeList2[timeInd2]) if multiTimeListCond else (
            timeList[timeInd1], timeList[timeInd2])
        timeDiff = goldDuration / \
            (len(timeList1) if multiTimeListCond else len(timeList))

        if listType.startswith('day_time'):
            durationMag = 'hours'
            spreadPrep = 'at'
        elif listType in ['day', 'date']:
            durationMag = 'days'
            spreadPrep = 'on'
        elif listType.startswith('month'):
            durationMag = 'months'
            spreadPrep = 'in'
        elif listType == 'year':
            durationMag = 'years'
            spreadPrep = 'in'

        durationDict = {'GOLD': goldDuration,
                        'GOLD+1': goldDuration + 1, 'GOLD*10': 10 * goldDuration}
        durationTypeDict = {'EQUAL': 'for', 'LESS': 'for less than'}

        for durTypeKey, durType in durationTypeDict.items():
            for durationKey, duration in durationDict.items():
                if not timeSpread:
                    premiseSent = tempSent + ' from ' + time1 + ' to ' + time2 + '.'
                else:
                    untilCond = spreadTempII.split(' ')[-1] == 'until'
                    premiseSent = spreadTempI + ' ' + spreadPrep + ' ' + time1 + ' ' + \
                        spreadTempII + \
                        ('' if untilCond else (' ' + spreadPrep)) + ' ' + time2 + '.'
                hypSent = tempSent + ' ' + durType + ' ' + \
                    str(duration) + ' ' + (durationMag if (duration != 1)
                                           else durationMag[:-1]) + '.'
                if 'less' in durType:
                    label = 'Entailment' if (
                        goldDuration < duration) else 'Contradiction'
                else:
                    label = 'Entailment' if (
                        goldDuration == duration) else 'Contradiction'
                hypType = durTypeKey + '_' + durationKey

                pairList.append(
                    (premiseSent, hypSent, label, hypType, timeDiff))

    return pairList


def genDurationDatePairs(tempSent, spreadTempI='', spreadTempII='', monthListType='full', timeSpread=False, durationMonths=True, numEpochs=1):

    pairList = []
    yearList = allListDict['year']

    for _ in range(numEpochs):

        if monthListType == 'both':
            monthList1, monthList2 = (allListDict['month_full'], allListDict['month_abv']) if (
                np.random.rand() > 0.5) else (allListDict['month_abv'], allListDict['month_full'])
        else:
            monthList = allListDict['month_' + monthListType]

        monthInd1, monthInd2 = np.random.choice((range(len(monthList1)) if (
            monthListType == 'both') else range(len(monthList))), size=2, replace=True)
        yearInd1, yearInd2 = np.random.choice(
            range(len(yearList)), size=2, replace=False)
        yearInd1, yearInd2 = (yearInd1, yearInd2) if (
            yearInd1 < yearInd2) else (yearInd2, yearInd1)
        year1, year2 = yearList[yearInd1], yearList[yearInd2]
        month1, month2 = (monthList1[monthInd1], monthList2[monthInd2]) if (
            monthListType == 'both') else (monthList[monthInd1], monthList[monthInd2])
        goldDuration = (yearInd2 - yearInd1) * 12 + ((monthInd2 - monthInd1)
                                                     if (monthInd2 >= monthInd1) else (- monthInd1 + monthInd2))
        timeDiff = goldDuration / (12 * len(yearList))

        durationDict = {'GOLD': goldDuration,
                        'GOLD+1': goldDuration + 1, 'GOLD*10': 10 * goldDuration}
        durationTypeDict = {'EQUAL': 'for', 'LESS': 'for less than'}

        for durTypeKey, durType in durationTypeDict.items():
            for durationKey, duration in durationDict.items():
                if not timeSpread:
                    premiseSent = tempSent + ' from ' + month1 + ' ' + \
                        year1 + ' to ' + month2 + ' ' + year2 + '.'
                else:
                    untilCond = spreadTempII.split(' ')[-1] == 'until'
                    premiseSent = spreadTempI + ' in ' + month1 + ' ' + year1 + ' ' + \
                        spreadTempII + (' ' if untilCond else ' in ') + \
                        month2 + ' ' + year2 + '.'
                if durationMonths:
                    yearString = ''
                    monthString = str(duration) + ' months'
                else:
                    durYears, durMonths = int(duration / 12), duration % 12
                    yearString = str(durYears) + \
                        (' years' if durYears != 1 else ' year')
                    if durMonths == 0:
                        monthString = ''
                    elif durMonths == 1:
                        monthString = ' 1 month'
                    else:
                        monthString = ' ' + str(durMonths) + ' months'
                hypSent = tempSent + ' ' + durType + ' ' + yearString + monthString + '.'
                if 'less' in durType:
                    label = 'Entailment' if (
                        goldDuration < duration) else 'Contradiction'
                else:
                    label = 'Entailment' if (
                        goldDuration == duration) else 'Contradiction'

                hypType = durTypeKey + '_' + durationKey

                pairList.append(
                    (premiseSent, hypSent, label, hypType, timeDiff))

    return pairList


def genChallengeSet(templatesDF, EPOCH_NUM=5):

    challengeSetDF = pd.DataFrame()

    # Generating single/across lists

    for ind, row in templatesDF.iterrows():

        durList = row['Duration'].split(', ')
        if 'point' in durList:
            continue
        if 'month' in durList:
            durList += ['month_full', 'month_abv']
        if 'day_time' in durList:
            durList += ['day_time_12', 'day_time_24']
        if 'day' in durList:
            durList += ['date']

        durTemp = row['Duration Template']
        spreadTempI = row['Spread I']
        spreadTempII = row['Spread II']

        for listType in durList:
            for nextCycleVal in [True, False]:
                if nextCycleVal and (listType in ['date', 'year']):
                    continue
                for timeSpreadVal in [True, False]:
                    returnedList = genDurationPairList(listType=listType, tempSent=durTemp, spreadTempI=spreadTempI,
                                                       spreadTempII=spreadTempII, nextCycle=nextCycleVal, timeSpread=timeSpreadVal,
                                                       numEpochs=EPOCH_NUM)
                    premList, hypoList, labelList, durTypeList, timeDiffList = zip(
                        *returnedList)
                    currDF = pd.DataFrame({'Premise': premList, 'Hypothesis': hypoList, 'Label': labelList, 'Time Diff': timeDiffList,
                                           'Type': ('SINGLE_' + listType) if listType not in ['month', 'day_time'] else ('MULTI_' + listType),
                                           'Dur Type': durTypeList, 'Next Cycle': nextCycleVal, 'Temp Type': 'Spread' if timeSpreadVal else 'Near'})
                    challengeSetDF = pd.concat(
                        [challengeSetDF, currDF], ignore_index=True)

    # Generating dates

    for ind, row in templatesDF.iterrows():

        durList = row['Duration'].split(', ')
        if 'year' not in durList:
            continue

        durTemp = row['Duration Template']
        spreadTempI = row['Spread I']
        spreadTempII = row['Spread II']

        for monthListTypeVal in ['full', 'abv', 'both']:
            for durationMonthsVal in [True, False]:
                for timeSpreadVal in [True, False]:
                    returnedList = genDurationDatePairs(tempSent=durTemp, spreadTempI=spreadTempI, spreadTempII=spreadTempII,
                                                        monthListType=monthListTypeVal, timeSpread=timeSpreadVal, durationMonths=durationMonthsVal,
                                                        numEpochs=EPOCH_NUM)
                    premList, hypoList, labelList, durTypeList, timeDiffList = zip(
                        *returnedList)
                    currDF = pd.DataFrame({'Premise': premList, 'Hypothesis': hypoList, 'Label': labelList, 'Time Diff': timeDiffList,
                                           'Type': ('DATE_M_' + monthListTypeVal) if durationMonthsVal else ('DATE_YM_' + monthListTypeVal),
                                           'Dur Type': durTypeList, 'Next Cycle': False, 'Temp Type': 'Spread' if timeSpreadVal else 'Near'})
                    challengeSetDF = pd.concat(
                        [challengeSetDF, currDF], ignore_index=True)

    return challengeSetDF


if __name__ == '__main__':

    # Defining the lists
    dayTimeList_12HR = ['12 AM'] + [str(elem) + ' AM' for elem in range(1, 12)] + [
        '12 PM'] + [str(elem) + ' PM' for elem in range(1, 12)]
    dayTimeList_24HR = ['{:02d}'.format(elem) + ':00' for elem in range(0, 24)]
    weekdayList = ['Sunday', 'Monday', 'Tuesday',
                   'Wednesday', 'Thursday', 'Friday', 'Saturday']
    datesList = ['1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th', '9th', '10th', '11th', '12th', '13th', '14th', '15th',
                 '16th', '17th', '18th', '19th', '20th', '21st', '22nd', '23rd', '24th', '25th', '26th', '27th', '28th']
    monthsList_Full = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
                       'November', 'December']
    monthsList_Abv = ['Jan', 'Feb', 'Mar', 'Apr', 'May',
                      'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    yearsList = [str(year) for year in range(1900, 2001)]

    allListDict = {
        'day_time_12': np.array(dayTimeList_12HR),
        'day_time_24': np.array(dayTimeList_24HR),
        'day': np.array(weekdayList),
        'date': np.array(datesList),
        'month_full': np.array(monthsList_Full),
        'month_abv': np.array(monthsList_Abv),
        'year': np.array(yearsList),
    }

    # Loading the templates
    templatesDF = pd.read_csv('../data/templates.csv')

    # Separating train and test templates
    testInds = [20, 21, 22, 23, 24, 25, 40, 41,
                42, 43, 44, 45, 50, 53, 55, 61, 67, 69]
    trainTemplatesDF = templatesDF.iloc[[
        idx for idx in templatesDF.index if idx not in testInds]]
    testTemplatesDF = templatesDF.iloc[testInds]
    trainTemplatesDF.reset_index(inplace=True, drop=True)
    testTemplatesDF.reset_index(inplace=True, drop=True)

    # Generating train set
    trainChallengeSet = genChallengeSet(trainTemplatesDF, EPOCH_NUM=5)
    trainChallengeSet.to_csv('../data/cs2_train.csv')
    print('Train Dataset Instances:', trainChallengeSet.shape[0])

    # Generating test set
    testChallengeSet = genChallengeSet(testTemplatesDF, EPOCH_NUM=5)
    testChallengeSet.to_csv('../data/cs2_test.csv')
    print('Test Dataset Instances:', testChallengeSet.shape[0])
