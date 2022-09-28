"""
TODO
- Create GUI for inputting information
- Figure out a more elegant way to get swid/espn_2 cookie and store
- Determine where and how to store ESPN league information
- Rerun is_free_agent until the api retries exceeded error occurs again.
  Adjust the except clause to only include this error.
- Add capability to handle adding (rather than just swapping)
- Clean up datetime pausing (will be part of GUI)
- For defenses, choose a random player to query to determine free agency status (find one through waivers request)
"""

import time


def is_player_free_agent(player_to_add, leagueID, seasonID, cookies):
    """
    Query the ESPN api and determine if specified player is a free agent.
    :param player_to_add: Player to check status of
    :param leagueID: ID of ESPN fantasy league
    :param seasonID: ID of season (year)
    :param cookies: swid and espn_s2 cookies required for accessing the api
    :return: True if the player is a free agent; false otherwise
    """
    import requests
    import json
    import pandas as pd

    url = 'https://sports.core.api.espn.com/v3/sports/football/nfl/athletes?limit=18000'
    jsonData = requests.get(url).json()

    players = pd.DataFrame(jsonData['items']).dropna(subset='firstName')
    players = players[['id', 'fullName']].dropna()
    player_to_add_ID = players[players['fullName'] == player_to_add]['id'].values[0]

    url = f"https://fantasy.espn.com/apis/v3/games/ffl/seasons/{seasonID}/segments/0/leagues/{leagueID}"

    filters = {"players": {"filterIds": {"value": [player_to_add_ID]}}}
    headers = {'x-fantasy-filter': json.dumps(filters)}
    r = requests.get(url,
                     params={
                         'view': 'kona_player_info',
                     },
                     headers=headers,
                     cookies=cookies)
    print(r.json())

    player_status = r.json()['players'][0]['status']

    if player_status == "FREEAGENT":
        return True
    else:
        return False


def swap_player(player_to_add, player_to_drop, username, password, leagueID, teamID, seasonID):
    """
    Swaps a player using selenium to interact with ESPN front-end and perform the transaction.
    :param player_to_add: Name of player to add
    :param player_to_drop: Name of player to drop
    :param username: Username of fantasy account (email address)
    :param password: Passwrod of fantasy account
    :param leagueID: ID number for league
    :param teamID: ID number for team
    :param seasonID: ID number for season (the year)
    :return:
    """
    # Selenium imports
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.action_chains import ActionChains

    # Initialize selenium Chrome driver
    s = Service('/Users/ng/Desktop/Free_Agent_Automation/chromedriver')
    driver = webdriver.Chrome(service=s)

    # Go to ESPN website
    url = f'https://fantasy.espn.com/football/team?leagueId={leagueID}&teamId={teamID}&seasonId={seasonID}'
    driver.get(url)
    time.sleep(3)

    # ----------- Login -----------
    # swap to iframe of login window
    driver.switch_to.frame("disneyid-iframe")
    # find username box and send username
    username_field = driver.find_element("xpath", "//input[@placeholder='Username or Email Address']")
    username_field.send_keys(username)
    time.sleep(1)
    # find password box and send password
    password_field = driver.find_element("xpath", "//input[@placeholder='Password (case sensitive)']")
    password_field.send_keys(password)
    time.sleep(1)
    # find login button and press it
    login_button = driver.find_element("xpath", "//button[@class='btn btn-primary btn-submit ng-isolate-scope']")
    login_button.click()
    # return to the default content from the iframe
    driver.switch_to.default_content()
    time.sleep(1)

    # ----------- Players -----------
    # navigate to the players tab
    driver.find_element("xpath", "//span[text()='Players']").click()
    time.sleep(1)
    # lookup player name
    player_name_field = driver.find_element("xpath", "//input[@placeholder='Player Name']")
    player_name_field.send_keys(player_to_add)
    time.sleep(2)
    # click on located player
    driver.find_element("xpath", "//button[@class='player--search--match']").click()
    time.sleep(2)

    # try clicking the add free agent button
    try:
        driver.find_element("xpath", f"//button[contains(@aria-label, 'Add {player_to_add}')]").click()
    except Exception as e:
        # if it does not work, the player must still be on waivers or on someone's team
        print("Player is not available as a free agent.")
    time.sleep(5)

    # ----------- Drop Player -----------
    # Scroll down to the player that is to be dropped (this must be done because Selenium will error if
    # it cannot see the player that is to be dropped).
    actions = ActionChains(driver)
    drop_player_button = driver.find_element("xpath",
                                             f"//button[contains(@aria-label, 'Drop Player {player_to_drop}')]")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});", drop_player_button)
    time.sleep(2)
    # Click the drop button
    drop_player_button.click()
    time.sleep(2)
    # Confirm action
    driver.find_element("xpath",
                        f"//button[contains(@aria-label, 'Continue to add {player_to_add} and drop {player_to_drop}')]").click()
    time.sleep(2)
    # Confirm action again
    driver.find_element("xpath",
                        f"//button[contains(@aria-label, 'Confirm add {player_to_add} and drop {player_to_drop}')]").click()
    time.sleep(2)


def main():
    import pause
    from datetime import datetime
    import json
    import os

    # Getting ESPN cookies to request data from api
    if os.path.exists("cookies.json"):
        cookies_file = open("cookies.json")
        cookies = json.load(cookies_file)
    else:
        # TODO: Generate cookies file
        return

    # Getting store metadata about league
    if os.path.exists("league_info.json"):
        league_metadata_file = open("league_info.json")
        league_metadata = json.load(league_metadata_file)
        leagueID = league_metadata['leagueID']
        teamID = league_metadata['teamID']
        seasonID = league_metadata['seasonID']
    else:
        # TODO: Generate league_info file
        return

    username = input("Enter username: ")
    password = input("Enter password: ")

    players_to_add = ['Rams D/ST']
    players_to_drop = ['Cowboys D/ST']

    pause.until(datetime(2022, 9, 28, 3))

    for transaction_idx in range(len(players_to_add)):
        is_free_agent = is_player_free_agent(players_to_add[transaction_idx], leagueID, seasonID, cookies)
        while not is_free_agent:
            print("Not a free agent.")
            time.sleep(300)
            try:
                is_free_agent = is_player_free_agent(players_to_add[transaction_idx], leagueID, seasonID, cookies)
            except:
                # Intended to catch timeout issues.
                # Sometimes ESPN decides too many api calls have been made by this account
                # and will cause an error to crash the program if not handled.
                is_free_agent = False
        try:
            swap_player(players_to_add[transaction_idx], players_to_drop[transaction_idx], username, password, leagueID,
                        teamID, seasonID)
        except:
            print(f"Unable to swap {players_to_drop[transaction_idx]} for {players_to_add[transaction_idx]}.")


if __name__ == '__main__':
    main()
