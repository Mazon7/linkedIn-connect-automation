from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located

from client import LIClient
from script import process_csv


# Login in LinkedIn (need to ask for login at the first place)
# Open and read the CSV file
# Check if the person was not connected previously
# Connect with the person
# Send message
# Writes data in the CSV file


username = input('Login: ')
password = input('Password: ')

# Possible upgrade
# make input password more secure
# input the path to the file

# Specifying signature
signature = input("Input your signature for messages:")

# Main process
with webdriver.Chrome() as driver:

    driver.get("https://www.linkedin.com/uas/login")

    # initialize LinkedIn web client
    liclient = LIClient(driver, username, password)

    # LogIn
    liclient.login()

    # main action
    process_csv(driver, signature)

    # exit driver
    liclient.driver_quit()
