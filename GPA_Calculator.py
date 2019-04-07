#! /usr/bin/env python3

import re
import sys
import getpass
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options


def scrape_grades(username, password):
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
    except Exception:
        print('Invalid Username or Password!')
        sys.exit()
    rows = table.find_elements(By.TAG_NAME, 'tr')
    grades = []
    for x in range(3, 11):
        columns = [11, 13, 14, 15, 18, 19, 16]
        row_data = []
        for y in range(0, len(columns)):
            col = rows[x].find_elements(By.TAG_NAME, 'td')[columns[y]]
            if columns[y] == 11:
                col_data = col.text.split(' \n ', 1)[0]
            else:
                col_data = re.sub('[^0-9.]', '', col.text)
            if col_data == '':
                col_data = None
            row_data.append(col_data)
        subject = {
            'Subject': row_data[0],
            'Q1': row_data[1],
            'Q2': row_data[2],
            'X1': row_data[3],
            'Q3': row_data[4],
            'Q4': row_data[5],
            'X2': row_data[6],
        }
        grades.append(subject)
    driver.quit()
    return grades


def level(grades):
    gym = None
    for row in range(0, len(grades)):
        subject_level = 0
        subject = grades[row]['Subject']
        if 'Phys Ed' in subject or 'Physical Education' in subject:
            gym = row
        elif 'AP' in subject:
            subject_level = 4
        elif 'Acc' in subject:
            subject_level = 3
        elif 'CPA' in subject:
            subject_level = 2
        elif 'CPB' in subject:
            subject_level = 1
        grades[row]['Level'] = subject_level
    if gym is not None:
        del (grades[gym])
    return grades


def main():
    print('Enter your username: ', end='')
    username = input()
    print('Enter your password: ', end='')
    password = input()
    # password = getpass.getpass('Enter your password: ')
    grades = overall_gpa(letter(overall_grades(level(scrape_grades(username, password)))))
    weighted_gpa = get_weighted_gpa(grades)
    unweighted_gpa = get_unweighted_gpa(grades)

    print('Weighted GPA: %s' % weighted_gpa)
    print('Unweighted GPA: %s\n' % unweighted_gpa)
    for subject in range(0, len(grades)):
        if grades[subject]['Grade'] != -1:
            print('%s:  %s (%s) - %s' % (
                grades[subject]['Subject'], grades[subject]['Grade'], grades[subject]['Letter'],
                grades[subject]['WeightedGPA']))
        else:
            print('%s:  None' % grades[subject]['Subject'])


def get_weighted_gpa(grades):
    gpa = 0
    count = 0
    for subject in range(0, len(grades)):
        gpa_temp = grades[subject]['WeightedGPA']
        if gpa_temp is not None:
            gpa += gpa_temp
            count += 1
    gpa = round(gpa / float(count), 3)
    return gpa


def get_unweighted_gpa(grades):
    gpa = 0
    count = 0
    for subject in range(0, len(grades)):
        gpa_temp = grades[subject]['UnweightedGPA']
        if gpa_temp is not None:
            gpa += gpa_temp
            count += 1
    gpa = round(gpa / float(count), 3)
    return gpa


def overall_gpa(grades):
    num = 0
    for subject in grades:
        grade = subject['Grade']
        gpa_weighted = 0
        gpa_unweighted = 0
        if subject['Level'] != 0 and grade != -1:
            if subject['Level'] == 4:
                gpa_weighted = gpa_ap(grade)
            elif subject['Level'] == 3:
                gpa_weighted = gpa_acc(grade)
            else:
                gpa_weighted = gpa_cp(grade)
            gpa_unweighted = gpa_cp(grade)
        grades[num]['WeightedGPA'] = gpa_weighted
        grades[num]['UnweightedGPA'] = gpa_unweighted
        num += 1
    return grades


def overall_grades(grades):
    num = 0
    for subject in grades:
        count = 0
        grade = 0
        if midterms(subject['Subject']):
            if finals(subject['Subject']):
                if subject['Q1'] is not None:
                    grade += (0.2 * float(subject['Q1']))
                    count += 0.2
                if subject['Q2'] is not None:
                    grade += (0.2 * float(subject['Q2']))
                    count += 0.2
                if subject['X1'] is not None:
                    grade += (0.1 * float(subject['X1']))
                    count += 0.1
                if subject['Q3'] is not None:
                    grade += (0.2 * float(subject['Q3']))
                    count += 0.2
                if subject['Q4'] is not None:
                    grade += (0.2 * float(subject['Q4']))
                    count += 0.2
                if subject['X2'] is not None:
                    grade += (0.1 * float(subject['X2']))
                    count += 0.1
            else:
                if subject['Q1'] is not None:
                    grade += (0.2 * float(subject['Q1']))
                    count += 0.2
                if subject['Q2'] is not None:
                    grade += (0.2 * float(subject['Q2']))
                    count += 0.2
                if subject['X1'] is not None:
                    grade += (0.1 * float(subject['X1']))
                    count += 0.1
                if subject['Q3'] is not None:
                    grade += (0.25 * float(subject['Q3']))
                    count += 0.25
                if subject['Q4'] is not None:
                    grade += (0.25 * float(subject['Q4']))
                    count += 0.25
        else:
            if finals(subject['Subject']):
                if subject['Q1'] is not None:
                    grade += (0.25 * float(subject['Q1']))
                    count += 0.25
                if subject['Q2'] is not None:
                    grade += (0.25 * float(subject['Q2']))
                    count += 0.25
                if subject['Q3'] is not None:
                    grade += (0.2 * float(subject['Q3']))
                    count += 0.2
                if subject['Q4'] is not None:
                    grade += (0.2 * float(subject['Q4']))
                    count += 0.2
                if subject['X2'] is not None:
                    grade += (0.1 * float(subject['X2']))
                    count += 0.1
            else:
                if subject['Q1'] is not None:
                    grade += (0.25 * float(subject['Q1']))
                    count += 0.25
                if subject['Q2'] is not None:
                    grade += (0.25 * float(subject['Q2']))
                    count += 0.25
                if subject['Q3'] is not None:
                    grade += (0.25 * float(subject['Q3']))
                    count += 0.25
                if subject['Q4'] is not None:
                    grade += (0.25 * float(subject['Q4']))
                    count += 0.25
        if count == 0:
            grade = -1
        else:
            grade *= 1.0 / count
        grades[num]['Grade'] = round(grade, 3)
        num += 1
    return grades


def midterms(subject_name):
    if 'AP' in subject_name:
        return True
    elif 'Music' in subject_name:
        return False
    elif 'Spanish' in subject_name:
        return False
    return True


def finals(subject_name):
    if 'AP' in subject_name:
        return False
    elif 'Music' in subject_name:
        return False
    elif 'Spanish' in subject_name:
        return False
    elif 'Literature' in subject_name:
        return False
    return True


def letter(grades):
    num = 0
    for subject in grades:
        grade = round(subject['Grade'])
        if grade >= 93:
            grades[num]['Letter'] = 'A'
        elif grade >= 90:
            grades[num]['Letter'] = 'A-'
        elif grade >= 87:
            grades[num]['Letter'] = 'B+'
        elif grade >= 83:
            grades[num]['Letter'] = 'B'
        elif grade >= 80:
            grades[num]['Letter'] = 'B-'
        elif grade >= 77:
            grades[num]['Letter'] = 'C+'
        elif grade >= 73:
            grades[num]['Letter'] = 'C'
        elif grade >= 70:
            grades[num]['Letter'] = 'C-'
        elif grade >= 67:
            grades[num]['Letter'] = 'D+'
        elif grade >= 63:
            grades[num]['Letter'] = 'D'
        elif grade >= 60:
            grades[num]['Letter'] = 'D-'
        else:
            grades[num]['Letter'] = 'F'
        num += 1
    return grades


def gpa_ap(grade):
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


def gpa_acc(grade):
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


def gpa_cp(grade):
    grade = round(grade)
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
