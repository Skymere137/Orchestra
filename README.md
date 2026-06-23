🚨 CODE RED WARNING — DO NOT USE THIS ON LIVE MARKETS

⚠️ CRITICAL WARNING: The trading strategies and backtester in this repository are UNFINISHED and UNTESTED.
    Do NOT run any strategy from this project with real funds or on a live exchange. Using these tools as-is can cause significant financial loss and may expose you to legal risk.

This project is experimental and under active development. It is provided for research and educational purposes only.

Key warnings and required actions:

    -Several files and data sources are NOT included (e.g., personalNotes.txt, data feeds). You must obtain and connect your own data.
    
    -Do NOT connect to real exchanges, brokers, or live accounts. Use an isolated simulator or sandbox/demo account with ZERO real funds.
    
    -Do NOT commit, store, or share any credentials, API keys, private keys, passwords, or other secrets in this repository or its history. 
    Remove any secrets from code, config files, and commit history (use git-filter-repo or BFG if needed).
    
    -Thoroughly review all data handling, order execution, and exception paths before any live use. Run extensive tests in a controlled 
     environment first.
    
    -If unsure about technical, financial, or legal implications, stop and consult a qualified professional.

The maintainers accept no responsibility for financial losses, damages, or legal liabilities resulting from use of this code.

How to Use:

    -Due to the frequency of use, changes and addistions to the main codebase the code can be a little messy. However despite this I always strive to keep it in working order. As a result though there may or may not be a lot of lines that are commented out. 

    -There are 3 data files available for use in the "testing_data" directory.

    -The backtester works by passing a strat as a parameter. All strats should be imported from the strategies dir(some strategies may not work at all due to lack of testing or chages that rendered them incompatable with the backtester).

    -First instantiate a BackTest object, it must take a strategy as the first parameter. You can add a min_r or set the index of the "backtests_date_ranges" index for the last date you want from the data. From here you can run the "run_strat" method, pass in the ticker (AAPL is default) and set your min_trade. You can also set the range of time that you want by setting the "time_range" parameter to the corrosponding index of the "temporal_ranges" list (default is all day and time is in UTC). The last parameter "return_trades" will decide what this method returns. If True it will return the trades that were "placed". This can be useful if you are trying to compare what worked with what doesn't, and also when using the "plotting_trades" function from the charting file. Otherwise the method will return a list with the following values, [profit, win_rate, num_of_trades, and R].