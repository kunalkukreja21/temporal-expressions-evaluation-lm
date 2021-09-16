import pandas as pd
import numpy as np

def relationString(ind1, ind2):

    if ind1 < ind2:
        return '<'
    elif ind1 > ind2:
        return '>'
    else:
        return '='


def genOrderingPairList(tempSent, listType, premFixed=True, tempFirst=True, numEpochs=1):

    relativePrepList = ['before', 'after']
    pairList = []
    multiTimeListCond = listType in ['day_time', 'month']

    for _ in range(numEpochs):

        pairFound = False
        while not pairFound:

            if listType == 'day_time':
                timeList1, timeList2 = (allListDict['day_time_12'], allListDict['day_time_24']) if (
                    np.random.rand() > 0.5) else (allListDict['day_time_24'], allListDict['day_time_12'])
            elif listType == 'month':
                timeList1, timeList2 = (allListDict['month_full'], allListDict['month_abv']) if (
                    np.random.rand() > 0.5) else (allListDict['month_abv'], allListDict['month_full'])
            else:
                timeList = allListDict[listType]

            timeInd1, timeInd2 = np.random.choice((range(len(
                timeList1)) if multiTimeListCond else range(len(timeList))), size=2, replace=True)
            premTime, hypTime = (timeList1[timeInd1], timeList2[timeInd2]) if multiTimeListCond else (
                timeList[timeInd1], timeList[timeInd2])

            if premFixed:
                if listType.startswith('day_time'):
                    premPrep = 'at'
                elif listType in ['day', 'date']:
                    premPrep = 'on'
                else:
                    premPrep = 'in'
                hypPrep = np.random.choice(relativePrepList, size=1)[0]

            else:
                hypPrep, premPrep = np.random.choice(
                    relativePrepList, 2, replace=True)

            if tempFirst:
                premSent = tempSent + ' ' + premPrep + ' ' + premTime + '.'
                hypoSent = tempSent + ' ' + hypPrep + ' ' + hypTime + '.'
            else:
                premSent = premPrep.capitalize() + ' ' + premTime + ', ' + tempSent + '.'
                hypoSent = hypPrep.capitalize() + ' ' + hypTime + ', ' + tempSent + '.'

            if premSent != hypoSent:
                pairFound = True

            if (listType != 'year') and (abs(timeInd1 - timeInd2) > (len(timeList1) if multiTimeListCond else len(timeList)) / 2):
                pairFound = False

        relation = relationString(timeInd1, timeInd2)
        timeDiff = abs(timeInd1 - timeInd2) / (len(timeList1)
                                               if multiTimeListCond else len(timeList))

        if premFixed:
            if (relation == '<') and (hypPrep == 'before'):
                label = 'Entailment'
            elif (relation == '>') and (hypPrep == 'after'):
                label = 'Entailment'
            else:
                label = 'Contradiction'
        else:
            if (relation == '<') and (premPrep == 'before') and (hypPrep == 'before'):
                label = 'Entailment'
            elif (relation == '>') and (premPrep == 'after') and (hypPrep == 'after'):
                label = 'Entailment'
            elif (relation in ['<', '=']) and (premPrep == 'before') and (hypPrep == 'after'):
                label = 'Contradiction'
            elif (relation in ['>', '=']) and (premPrep == 'after') and (hypPrep == 'before'):
                label = 'Contradiction'
            else:
                label = 'Neutral'

        pairList.append((premSent, hypoSent, label, timeDiff))

    return pairList


def genOrderingDatePairs(tempSent, monthListType='full', premFixed=True, includeDate=False, tempFirst=True, numEpochs=1):

    relativePrepList = ['before', 'after']
    pairList = []
    yearList = allListDict['year']
    dateList = allListDict['date']

    for _ in range(numEpochs):

        pairFound = False
        premDate, hypDate = '', ''

        while not pairFound:

            if monthListType == 'both':
                monthList1, monthList2 = (allListDict['month_full'], allListDict['month_abv']) if (
                    np.random.rand() > 0.5) else (allListDict['month_abv'], allListDict['month_full'])
            else:
                monthList = allListDict['month_' + monthListType]

            monthInd1, monthInd2 = np.random.choice((range(len(monthList1)) if (
                monthListType == 'both') else range(len(monthList))), size=2, replace=True)
            yearInd1, yearInd2 = np.random.choice(
                range(len(yearList)), size=2, replace=True)
            premYear, hypYear = yearList[yearInd1], yearList[yearInd2]
            premMonth, hypMonth = (monthList1[monthInd1], monthList2[monthInd2]) if (
                monthListType == 'both') else (monthList[monthInd1], monthList[monthInd2])

            if includeDate:
                dateInd1, dateInd2 = np.random.choice(
                    range(len(dateList)), size=2, replace=True)
                premDate, hypDate = dateList[dateInd1], dateList[dateInd2]

            if premFixed:
                if includeDate:
                    premPrep = 'on'
                else:
                    premPrep = 'in'

                hypPrep = np.random.choice(relativePrepList, size=1)[0]

            else:
                hypPrep, premPrep = np.random.choice(relativePrepList, size=2)

            if tempFirst:
                premSent = tempSent + ' ' + premPrep + ' ' + \
                    (premDate + ' ' if premDate != '' else '') + \
                    premMonth + ' ' + premYear + '.'
                hypoSent = tempSent + ' ' + hypPrep + ' ' + \
                    (hypDate + ' ' if hypDate != '' else '') + \
                    hypMonth + ' ' + hypYear + '.'
            else:
                premSent = premPrep.capitalize() + ' ' + (premDate + ' ' if premDate != '' else '') + \
                    premMonth + ' ' + premYear + ', ' + tempSent + '.'
                hypoSent = hypPrep.capitalize() + ' ' + (hypDate + ' ' if hypDate != '' else '') + \
                    hypMonth + ' ' + hypYear + ', ' + tempSent + '.'

            if premSent != hypoSent:
                pairFound = True

        yearRelation = relationString(yearInd1, yearInd2)
        monthRelation = relationString(monthInd1, monthInd2)
        if includeDate:
            dateRelation = relationString(dateInd1, dateInd2)

        if yearRelation != '=':
            relation = yearRelation
            timeDiff = abs(yearInd1 - yearInd2) / len(yearList)
        elif (yearRelation == '=') and (monthRelation != '='):
            relation = monthRelation
            timeDiff = abs(monthInd1 - monthInd2) / (len(monthList1)
                                                     if (monthListType == 'both') else len(monthList))
        elif (includeDate) and (monthRelation == '=') and (dateRelation != '='):
            relation = dateRelation
            timeDiff = abs(dateInd1 - dateInd2) / len(dateList)
        else:
            relation = monthRelation
            timeDiff = abs(monthInd1 - monthInd2) / (len(monthList1)
                                                     if (monthListType == 'both') else len(monthList))

        if premFixed:
            if (relation == '<') and (hypPrep == 'before'):
                label = 'Entailment'
            elif (relation == '>') and (hypPrep == 'after'):
                label = 'Entailment'
            else:
                label = 'Contradiction'
        else:
            if (relation == '<') and (premPrep == 'before') and (hypPrep == 'before'):
                label = 'Entailment'
            elif (relation == '>') and (premPrep == 'after') and (hypPrep == 'after'):
                label = 'Entailment'
            elif (relation in ['<', '=']) and (premPrep == 'before') and (hypPrep == 'after'):
                label = 'Contradiction'
            elif (relation in ['>', '=']) and (premPrep == 'after') and (hypPrep == 'before'):
                label = 'Contradiction'
            else:
                label = 'Neutral'

        pairList.append((premSent, hypoSent, label, timeDiff))

    return pairList


def genChallengeSet(templatesDF, EPOCH_NUM=5):

    challengeSetDF = pd.DataFrame()

    # GENERATING NORMAL PAIRS

    # Running for past templates
    for ind, row in templatesDF.iterrows():
        pastFwdTemplate = row['Forward Past Template']
        pastBwdTemplate = row['Backward Past Template']
        if (type(pastFwdTemplate) is not str) and np.isnan(pastFwdTemplate):
            continue
        occPast = row['Occurrence Past'].split(', ')
        if 'month' in occPast:
            occPast += ['month_full', 'month_abv']
        if 'day_time' in occPast:
            occPast += ['day_time_12', 'day_time_24']
        if 'day' in occPast:
            occPast += ['date']
        for listType in occPast:
            for premFixVal in [True, False]:
                for tempFirstVal in [True, False]:
                    returnedList = genOrderingPairList(tempSent=pastFwdTemplate if tempFirstVal else pastBwdTemplate, listType=listType,
                                                       premFixed=premFixVal, tempFirst=tempFirstVal, numEpochs=EPOCH_NUM)
                    premList, hypoList, labelList, timeDiffList = zip(
                        *returnedList)
                    currDF = pd.DataFrame({'Premise': premList, 'Hypothesis': hypoList, 'Label': labelList, 'Time Diff': timeDiffList,
                                          'Type': ('SINGLE_' + listType) if listType not in ['month', 'day_time'] else ('MULTI_' + listType),
                                           'Prem Fixed': premFixVal, 'Temp Type': 'Forward Past' if tempFirstVal else 'Backward Past'})
                    challengeSetDF = pd.concat(
                        [challengeSetDF, currDF], ignore_index=True)

    # Running for future templates
    for ind, row in templatesDF.iterrows():
        futureFwdTemplate = row['Forward Future Template']
        futureBwdTemplate = row['Backward Future Template']
        if (type(futureFwdTemplate) is not str) and np.isnan(futureFwdTemplate):
            continue
        occFuture = row['Occurrence Future'].split(', ')
        if 'month' in occFuture:
            occFuture += ['month_full', 'month_abv']
        if 'day_time' in occFuture:
            occFuture += ['day_time_12', 'day_time_24']
        if 'day' in occFuture:
            occFuture += ['date']
        if 'minutes' in occFuture:
            occFuture.remove('minutes')
        for listType in occFuture:
            for premFixVal in [True, False]:
                for tempFirstVal in [True, False]:
                    returnedList = genOrderingPairList(tempSent=futureFwdTemplate if tempFirstVal else futureBwdTemplate, listType=listType,
                                                       premFixed=premFixVal, tempFirst=tempFirstVal, numEpochs=EPOCH_NUM)
                    premList, hypoList, labelList, timeDiffList = zip(
                        *returnedList)
                    currDF = pd.DataFrame({'Premise': premList, 'Hypothesis': hypoList, 'Label': labelList, 'Time Diff': timeDiffList,
                                          'Type': ('SINGLE_' + listType) if listType not in ['month', 'day_time'] else ('MULTI_' + listType),
                                           'Prem Fixed': premFixVal, 'Temp Type': 'Forward Future' if tempFirstVal else 'Backward Future'})
                    challengeSetDF = pd.concat(
                        [challengeSetDF, currDF], ignore_index=True)

    # GENERATING DATE PAIRS

    # Running for past templates
    for ind, row in templatesDF.iterrows():
        pastFwdTemplate = row['Forward Past Template']
        pastBwdTemplate = row['Backward Past Template']
        if (type(pastFwdTemplate) is not str) and np.isnan(pastFwdTemplate):
            continue
        occPast = row['Occurrence Past'].split(', ')
        if 'year' not in occPast:
            continue
        for monthListTypeVal in ['full', 'abv', 'both']:
            for includeDateVal in [True, False]:
                for tempFirstVal in [True, False]:
                    for premFixVal in [True, False]:
                        returnedList = genOrderingDatePairs(tempSent=pastFwdTemplate if tempFirstVal else pastBwdTemplate, monthListType=monthListTypeVal,
                                                            premFixed=premFixVal, includeDate=includeDateVal, tempFirst=tempFirstVal, numEpochs=EPOCH_NUM)
                        premList, hypoList, labelList, timeDiffList = zip(
                            *returnedList)
                        currDF = pd.DataFrame({'Premise': premList, 'Hypothesis': hypoList, 'Label': labelList, 'Time Diff': timeDiffList,
                                               'Type': ('DATE_DMY_' + monthListTypeVal) if includeDateVal else ('DATE_MY_' + monthListTypeVal),
                                               'Prem Fixed': premFixVal, 'Temp Type': 'Forward Past' if tempFirstVal else 'Backward Past'})
                        challengeSetDF = pd.concat(
                            [challengeSetDF, currDF], ignore_index=True)

    # Running for past templates
    for ind, row in templatesDF.iterrows():
        futureFwdTemplate = row['Forward Future Template']
        futureBwdTemplate = row['Backward Future Template']
        if (type(futureFwdTemplate) is not str) and np.isnan(futureFwdTemplate):
            continue
        occFuture = row['Occurrence Future'].split(', ')
        if 'year' not in occFuture:
            continue
        for monthListTypeVal in ['full', 'abv', 'both']:
            for includeDateVal in [True, False]:
                for tempFirstVal in [True, False]:
                    for premFixVal in [True, False]:
                        returnedList = genOrderingDatePairs(tempSent=futureFwdTemplate if tempFirstVal else futureBwdTemplate, monthListType=monthListTypeVal,
                                                            premFixed=premFixVal, includeDate=includeDateVal, tempFirst=tempFirstVal, numEpochs=EPOCH_NUM)
                        premList, hypoList, labelList, timeDiffList = zip(
                            *returnedList)
                        currDF = pd.DataFrame({'Premise': premList, 'Hypothesis': hypoList, 'Label': labelList, 'Time Diff': timeDiffList,
                                               'Type': ('DATE_DMY_' + monthListTypeVal) if includeDateVal else ('DATE_MY_' + monthListTypeVal),
                                               'Prem Fixed': premFixVal, 'Temp Type': 'Forward Future' if tempFirstVal else 'Backward Future'})
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
    trainChallengeSet.to_csv('../data/cs1_train.csv')
    print('Train Dataset Instances:', trainChallengeSet.shape[0])

    # Generating test set
    testChallengeSet = genChallengeSet(testTemplatesDF, EPOCH_NUM=5)
    testChallengeSet.to_csv('../data/cs1_test.csv')
    print('Test Dataset Instances:', testChallengeSet.shape[0])
