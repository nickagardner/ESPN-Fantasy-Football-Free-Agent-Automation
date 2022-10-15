# ESPN-Fantasy-Football-Free-Agent-Automation

This program is intended as a very simple implementation to allow obsessed fantasy players to get more sleep. If you are like me and you have found yourself pursuing free agent trades at 5am, consider that course of action no longer! 

This program queries the ESPN API until desired player is a free agent. Once this occurs, testing software (selenium) is used to sign in to the ESPN fantasy website and add the desired player.

There is quite a bit left to do, and progress has slowed somewhat after I discovered that my league settings this year update waiver position weekly based on performance (meaning there is little benefit to adding from free agency vs. claiming from waivers). 

To use currently, change player to add and player to drop in the main function. Additionally, change the time to begin querying in the same location. A cookies file containing the swid key and espn_2 key is required, and a metadata file with leagueID, seasonID, and teamID is required as well. The construction method for these files has not yet been implemented, but they are just json files with your relevant personal information in it. 

# TODO
- Create GUI for inputting information
- Figure out a more elegant way to get swid/espn_2 cookie and store
- Determine where and how to store ESPN league information
- Rerun is_free_agent until the api retries exceeded error occurs again.
  Adjust the except clause to only include this error.
- Add capability to handle adding (rather than just swapping)
- Clean up datetime pausing (will be part of GUI)
- For defenses, choose a random player to query to determine free agency status
