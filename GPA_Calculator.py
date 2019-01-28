#! /usr/bin/env python3

import os
import re
import sys
import getpass
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options


def scrapeGrades(username, password):
    login_url = 'https://ps2.millburn.org/public/home.html'
    grades_url = 'https://ps2.millburn.org/guardian/home.html'

    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)

    driver.get(login_url)
    u = driver.find_element_by_name('account')
    u.send_keys(username)
    p = driver.find_element_by_name('pw')
    p.send_keys(password)
    p.send_keys(Keys.RETURN)
    driver.get(grades_url)

    try:
        table = driver.find_element(By.XPATH, '//*[@id="quickLookup"]/table[1]/tbody')
    except:
        print('Invalid Username or Password!')
        sys.exit()
    rows = table.find_elements(By.TAG_NAME, 'tr')
    grades = []
    for x in range(3,11):
        columns = [11,12,14,15,16,18,19]
        rowData = []
        for y in range(0,len(columns)):
            col = rows[x].find_elements(By.TAG_NAME, 'td')[columns[y]]
            colData = ''
            if (columns[y] == 11):
                colData = col.text.split(' \n ', 1)[0]
            else:
                colData = re.sub('[^0-9.]','', col.text)
            if (colData == ''):
                colData = None
            rowData.append(colData)
        subject = {
            'Subject': rowData[0],
            'Q1': rowData[1],
            'Q2': rowData[2],
            'X1': rowData[3],
            'Q3': rowData[5],
            'Q4': rowData[6],
            'X2': rowData[4],
        }
        grades.append(subject)
    driver.quit()
    return grades

def level(grades):
    gym = None
    for row in range(0,len(grades)):
        level = 0
        subject = grades[row]['Subject']
        if ('Phys Ed' in subject):
            gym = row
        elif ('AP' in subject):
            level = 4
        elif ('Acc' in subject):
            level = 3
        elif ('CPA' in subject):
            level = 2
        elif ('CPB' in subject):
            level = 1
        grades[row]['Level'] = level
    if (gym != None):
        del(grades[gym])
    return grades

def main():
    print('Enter your username: ', end = '')
    username = input()
    password = getpass.getpass('Enter your password: ')
    grades = level(scrapeGrades(username, password))
    weightedGPA = getWeightedGPA(grades)
    unweightedGPA = getUnweightedGPA(grades)

    print('Weighted GPA: %s' %weightedGPA)
    print('Unweighted GPA: %s\n' %unweightedGPA)
    for subject in range(0,len(grades)):
        if overallGrades(grades[subject]) != -1:
            print('%s:  %s (%s) - %s' %(grades[subject]['Subject'], overallGrades(grades[subject]), grades[subject]['Letter'], getSubjectGPA(grades[subject])))
        else:
            print('%s:  None' %grades[subject]['Subject'])


def getWeightedGPA(grades):
    gpa = 0
    count = 0
    for subject in range(0,len(grades)):
        grade = overallGrades(grades[subject])
        grades[subject]['Letter'] = letter(grade)
        gpaTemp = getSubjectGPA(grades[subject])
        if (gpaTemp != None):
            gpa += gpaTemp
            count += 1
    gpa = round(gpa/float(count),3)
    return gpa

def getUnweightedGPA(grades):
    gpa = 0
    count = 0
    for subject in range(0,len(grades)):
        grade = overallGrades(grades[subject])
        gpa += gpa_CP(grade)
        count += 1
    gpa = round(gpa/float(count),3)
    return gpa

def getSubjectGPA(subject):
    gpa = None
    grade = overallGrades(subject)
    if (subject['Level'] != 0 and grade != -1):
        if (subject['Level'] == 4):
            gpa = gpa_AP(grade)
        elif (subject['Level'] == 3):
            gpa = gpa_ACC(grade)
        else:
            gpa = gpa_CP(grade)
    return gpa

def overallGrades(subject):
    count = 0
    grade = 0
    if (midterms(subject['Subject'])):
        if (finals(subject['Subject'])):
            if (subject['Q1'] != None):
                grade += (0.2*float(subject['Q1']))
                count += 0.2
            if (subject['Q2'] != None):
                grade += (0.2*float(subject['Q2']))
                count += 0.2
            if (subject['X1'] != None):
                grade += (0.1*float(subject['X1']))
                count += 0.1
            if (subject['Q3'] != None):
                grade += (0.2*float(subject['Q3']))
                count += 0.2
            if (subject['Q4'] != None):
                grade += (0.2*float(subject['Q4']))
                count += 0.2
            if (subject['X2'] != None):
                grade += (0.1*float(subject['X2']))
                count += 0.1
        else:
            if (subject['Q1'] != None):
                grade += (0.2*float(subject['Q1']))
                count += 0.2
            if (subject['Q2'] != None):
                grade += (0.2*float(subject['Q2']))
                count += 0.2
            if (subject['X1'] != None):
                grade += (0.1*float(subject['X1']))
                count += 0.1
            if (subject['Q3'] != None):
                grade += (0.25*float(subject['Q3']))
                count += 0.25
            if (subject['Q4'] != None):
                grade += (0.25*float(subject['Q4']))
                count += 0.25
    else:
        if (finals(subject['Subject'])):
            if (subject['Q1'] != None):
                grade += (0.25*float(subject['Q1']))
                count += 0.25
            if (subject['Q2'] != None):
                grade += (0.25*float(subject['Q2']))
                count += 0.25
            if (subject['Q3'] != None):
                grade += (0.2*float(subject['Q3']))
                count += 0.2
            if (subject['Q4'] != None):
                grade += (0.2*float(subject['Q4']))
                count += 0.2
            if (subject['X2'] != None):
                grade += (0.1*float(subject['X2']))
                count += 0.1
        else:
            if (subject['Q1'] != None):
                grade += (0.25*float(subject['Q1']))
                count += 0.25
            if (subject['Q2'] != None):
                grade += (0.25*float(subject['Q2']))
                count += 0.25
            if (subject['Q3'] != None):
                grade += (0.25*float(subject['Q3']))
                count += 0.25
            if (subject['Q4'] != None):
                grade += (0.25*float(subject['Q4']))
                count += 0.25
    if (count == 0):
        grade = -1
    else:
        grade *= 1.0/count
    return round(grade,3)


def midterms(subjectName):
    if ('Music' in subjectName):
        return False
    return True

def finals(subjectName):
    if ('Music' in subjectName):
        return False
    elif ('Literature' in subjectName):
        return False
    return True

def letter(grade):
    grade = round(grade)
    if grade >= 93:
        return 'A'
    elif grade >= 90:
        return 'A-'
    elif grade >= 87:
        return 'B+'
    elif grade >= 83:
        return 'B'
    elif grade >= 80:
        return 'B-'
    elif grade >= 77:
        return 'C+'
    elif grade >= 73:
        return 'C'
    elif grade >= 70:
        return 'C-'
    elif grade >= 67:
        return 'D+'
    elif grade >= 63:
        return 'D'
    elif grade >= 60:
        return 'D-'
    else:
        return 'F'

def gpa_AP(grade):
    grade = round(grade)
    if grade >= 93:
        gpa = 4.667
    elif grade >= 90:
        gpa = 4.333
    elif grade >= 87:
        gpa = 4
    elif grade >= 83:
        gpa = 3.667
    elif grade >= 80:
        gpa = 3.333
    elif grade >= 77:
        gpa = 2.667
    elif grade >= 73:
        gpa = 2
    elif grade >= 70:
        gpa = 1.667
    elif grade >= 67:
        gpa = 1.333
    elif grade >= 63:
        gpa = 1
    elif grade >= 60:
        gpa = 0.667
    else:
        gpa = 0
    return gpa

def gpa_ACC(grade):
    grade = round(grade)
    if grade >= 93:
        gpa = 4.333
    elif grade >= 90:
        gpa = 4
    elif grade >= 87:
        gpa = 3.667
    elif grade >= 83:
        gpa = 3.333
    elif grade >= 80:
        gpa = 3
    elif grade >= 77:
        gpa = 2.667
    elif grade >= 73:
        gpa = 2
    elif grade >= 70:
        gpa = 1.667
    elif grade >= 67:
        gpa = 1.333
    elif grade >= 63:
        gpa = 1
    elif grade >= 60:
        gpa = 0.667
    else:
        gpa = 0
    return gpa

def gpa_CP(grade):
    grade = round(grade)
    gpa = 0
    if grade >= 93:
        gpa = 4
    elif grade >= 90:
        gpa = 3.667
    elif grade >= 87:
        gpa = 3.333
    elif grade >= 83:
        gpa = 3
    elif grade >= 80:
        gpa = 2.667
    elif grade >= 77:
        gpa = 2.333
    elif grade >= 73:
        gpa = 2
    elif grade >= 70:
        gpa = 1.667
    elif grade >= 67:
        gpa = 1.333
    elif grade >= 63:
        gpa = 1
    elif grade >= 60:
        gpa = 0.667
    else:
        gpa = 0
    return gpa


if __name__ == '__main__':
    main()