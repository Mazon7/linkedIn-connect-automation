from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException

from bs4 import BeautifulSoup
import csv
import time
import sys
from datetime import datetime, timedelta


# Main function
def main_check(driver, row, name, signature):
    with open('result.csv', 'a', newline='') as result_csv_file:
        csv_writer = csv.writer(result_csv_file,  delimiter=',')

        # Declaring the list for the row in the result.csv file
        new_dataset = []

        # Get dates for Messaged, Withdraw and Reconnection dates
        current_utc_datetime = datetime.utcnow()
        reconnect_date_1 = current_utc_datetime + timedelta(days=21)
        reconnect_date_2 = reconnect_date_1 + timedelta(days=21)

        # If Messaged, Reconnected_1, Reconnected_2 field are specified do all checks
        if row[5] != "" and row[6] != "" and row[7] != "":

            withdraw_date = datetime.strptime(
                row[5], '%c') + timedelta(days=14)

            if withdraw_date <= current_utc_datetime < datetime.strptime(row[6].split(' /', 1)[0], '%c'):
                if "Withdrawn" not in row[6]:
                    withdraw_connection(driver, name)
                    row[6] += " / Withdrawn"
                    print("Withdrawn connection first time\n")
                else:
                    print("Reconnect_1 time has not come yet\n")
            elif datetime.strptime(row[6].split(' /', 1)[0], '%c') <= current_utc_datetime < datetime.strptime(row[7].split(' /', 1)[0], '%c'):
                if "Withdrawn" in row[6]:
                    connect(driver, name, row, signature)
                    row[6] += " / Reconnected"
                    print("Reconnected first time\n")
                else:
                    withdraw_connection(driver, name)
                    driver.get(row[1])
                    connect(driver, name, row, signature)
                    row[6] += " / Withdrawn / Reconnected"
                    print("Withdrawn and reconnected first time\n")
            elif current_utc_datetime >= datetime.strptime(row[7].split(' /', 1)[0], '%c'):
                withdraw_connection(driver, name)
                driver.get(row[1])
                connect(driver, name, row, signature)
                row[7] += " / Withdrawn / Reconnected"
                print("Withdrawn and reconnected second time\n")
            else:
                print(
                    "Nothing was done for person! Please check it if you think something is wrong!\n")
        # If Messaged field is empty than dates are written in fields
        else:
            # Send connection
            connect(driver, name, row, signature)
            row[5] = current_utc_datetime.strftime("%c")
            row[6] = reconnect_date_1.strftime("%c")
            row[7] = reconnect_date_2.strftime("%c")
            print("Connected and specified dates for reconnection\n")

        # Write row into result.csv
        new_dataset.append(row)
        csv_writer.writerow(new_dataset[0])


def withdraw_connection(driver, name):
    driver.get('https://www.linkedin.com/mynetwork/invitation-manager/sent/')
    driver.find_element_by_xpath(
        f'//button[@aria-label="Withdraw invitation sent to {name}"]').click()
    driver.find_elements_by_class_name(
        'artdeco-modal__confirm-dialog-btn')[1].click()
    time.sleep(1)
    if driver.find_element_by_xpath(
            '//li[@data-test-artdeco-toast-item-type="success"]').isDisplayed():
        print(f"Connection withdrawn for {name}")
    else:
        print(f"Connection wasn't withdrawn for {name}. Check what's wrong!")


def connect(driver, name, row, signature):
    # send the connection request with the corresponding "Custom message" if the field is not empty
    # send the connection request with the specified message if the "Broken website" field is not empty

    driver.find_element_by_xpath(
        '//button[@aria-label="Add a note"]').click()
    time.sleep(1)

    custom_message = row[3]

    no_website_message = f"Hello ____,\n\nHope you are doing well.\n\nJust checked out your profile and couldn't find a website for your business.\nWe'd love to help you set up a website.\nWe've helped many businesses grow online.\n\nLet me know when we can talk if you are interested.\nThanks,\n{signature}"

    main_message = f"Hello {name},\n\nHope you are doing well.\n\nI work in digital marketing and I noticed one of your websites, {row[2]} is not loading.\nHave you thought about getting it fixed?\n\nWe can fix it for you or rebuild it.\nLet me know if you're interested.\n\nThanks a lot.\n{signature}"

    alt_message = f"Hello {name},\n\nHope you are doing well.\n\nI noticed one of your websites, {row[2]} is not loading.\nHave you thought about getting it fixed?\n\nWe can fix it for you or rebuild it.\nLet me know if you're interested.\n\nThanks a lot.\n{signature}"

    if row[2] == "":
        driver.find_element_by_id(
            'custom-message').send_keys(no_website_message)
        print("No website message is used")
    elif row[4] == "" and custom_message != "":
        driver.find_element_by_id('custom-message').send_keys(custom_message)
        print("Custom message is used")
    else:
        if len(main_message) <= 300:
            # use different message
            driver.find_element_by_id('custom-message').send_keys(main_message)
            print("Main message is used")
        else:
            driver.find_element_by_id('custom-message').send_keys(alt_message)
            print("Alternative message is used")

    time.sleep(2)
    driver.find_element_by_xpath(
        '//button[@aria-label="Send now"]').click()


def process_csv(driver, signature):

    sys.stdout = open("log.txt", "w", encoding='utf-8')

    with open('result.csv', 'w', newline='') as result_csv_file:
        csv_writer = csv.writer(result_csv_file, delimiter=',')

        # Declaring and writing headers to the result.csv file
        headers = ('StockCode', 'LinkedIn Link', 'Website', 'Custom Message',
                   'Broken website?', 'Messaged', 'Reconnect_1', 'Reconnect_2')
        csv_writer.writerow(headers)

    # Open input file
    with open('input.csv', 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        next(csv_reader)

        for row in csv_reader:
            driver.get(row[1])
            WebDriverWait(driver, 10)
            time.sleep(2)

            # Get the exact name of user
            src = driver.page_source
            soup = BeautifulSoup(src, 'lxml')
            name_div = soup.find('div', {'class': 'flex-1 mr5'})
            name_loc = name_div.find_all('ul')
            name = name_loc[0].find('li').get_text().strip()
            print(name)

            # Check if there are buttons for connection
            # If there is no option to connect move on to the next person.

            # Get main buttons
            main_btn = driver.find_element_by_class_name(
                'pv-s-profile-actions')

            more_btn = driver.find_element_by_css_selector(
                'button.pv-s-profile-actions__overflow-toggle')
            more_btn.click()
            time.sleep(3)

            # Get the pre-last button label of the actions list
            btn_labels = driver.find_elements_by_css_selector(
                'span.pv-s-profile-actions__label')
            alt_btn = btn_labels[-2:-1][0]

            if main_btn.text == "Pending" or alt_btn.text == "Pending":
                main_check(driver, row, name, signature)
            elif main_btn.text == "Connect":
                main_btn.click()
                main_check(driver, row, name, signature)
            elif alt_btn.text == "Connect":
                alt_btn.click()
                main_check(driver, row, name, signature)
            else:
                print('Moved to next person' + "\n")

    result_csv_file.close()
    csv_file.close()
    print("Done")

    # Close log file
    sys.stdout.close()
