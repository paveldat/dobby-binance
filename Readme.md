# Dobby - Binance Trade Bot

<p align="center">
  <img src = "https://github.com/paveldat/dobby-binance/blob/main/img/logo.png">
</p>

## Introduction
According to our observations and monitoring of the crypto market for a long time, we have revealed that all coins follow Bitcoin's lead; the difference is their phase offset.


## What is the `BRIDGE CURRENCY`?
Unfortunately, the Binance crypto exchange does not have all crypto assets, so Binance does not have markets for every pair of altcoins.
The workaround for this is to use a bridge currency that will complement missing pairs.
The default bridge currency is Tether (USDT), which is stable by design and compatible with nearly every coin on the Binance platform.
Instead of Tether (USDT), the user can set his coin as a bridge currency.

<p align="center">
  Coin A → BRIDGE CURRENCY COIN → Coin B
</p>

The way the bot takes advantage of the observed behaviour is to always downgrade from the "strong" coin to the "weak" coin, under the assumption that at some point the tables will turn.
It will then return to the original coin, ultimately holding more of it than it did originally. This is done while taking into consideration the trading fees.

<div align="center">
  <p><b>Coin A</b> → BRIDGE CURRENCY COIN → Coin B</p>
  <p>Coin B → BRIDGE CURRENCY COIN → Coin C</p>
  <p>...</p>
  <p>Coin Z → BRIDGE CURRENCY COIN → <b>Coin A</b></p>
</div>

The bot jumps between a configured set of coins on the condition that it does not return to a coin unless it is profitable in respect to the amount held last.
This means that we will never end up having less of a certain coin. The risk is that one of the coins may freefall relative to the others all of a sudden, attracting our reverse greedy algorithm.


## Preparing the `BINANCE` application
 -  Create a [Binance account](https://accounts.binance.com/en/register?ref=186219461)
 -  Enable Two-factor Authentication. (This can be done in the settings after authorization)
 -  Create a [new API key](https://github.com/paveldat/dobby-binance#how-to-create-new-api-key)
 -  Buy the cryptocurrencies that you want to use as bridge currency. (Note that in the Binance crypto exchange, the minimum transaction price is $10)


## How to create new API key
-   Click (hover) on the profile window
-   Click on `API Manager`
-   Select `Create API`
-   Follow the instructions of Binance

<p align="center">
  <img src = "https://github.com/paveldat/dobby-binance/blob/main/img/account.png">
</p>


## Tool setup

### Install Python dependencies
Run the following line in the terminal: `pip install -r requirements.txt`.

### User configuration (`user.cfg`)
**The configuration file consists of the following fields:**

-   **api_key** - Binance API key generated in the [How to create new API key](https://github.com/paveldat/dobby-binance#how-to-create-new-api-key) stage.
-   **api_secret_key** - Binance secret key generated in the [How to create new API key](https://github.com/paveldat/dobby-binance#how-to-create-new-api-key) stage.
-   **current_coin** - This is your starting coin of choice. This should be one of the coins from your supported coin list. If you want to start from your bridge currency, leave this field empty - the bot will select a random coin from your supported coin list and buy it.
-   **bridge** - Your bridge currency of choice. Notice that different bridges will allow different sets of supported coins. For example, there may be a Binance particular-coin/USDT pair but no particular-coin/BUSD pair.
-   **tld** - 'com' or 'us', depending on your region. Default is 'com'.
-   **hourToKeepScoutHistory** - Controls how many hours of scouting values are kept in the database. After the amount of time specified has passed, the information will be deleted.
-   **scout_sleep_time** - Controls how many seconds are waited between each scout.
-   **use_margin** - 'yes' to use scout_margin. 'no' to use scout_multiplier.
-   **scout_multiplier** - Controls the value by which the difference between the current state of coin ratios and previous state of ratios is multiplied. For bigger values, the bot will wait for bigger margins to arrive before making a trade.
-   **scout_margin** - Minimum percentage coin gain per trade. 0.8 translates to a scout multiplier of 5 at 0.1% fee.
-   **strategy** - The trading strategy to use. See [`binance_trade_bot/strategies`](https://github.com/paveldat/dobby-binance/blob/main/binance_trade_bot/strategies/Readme.md) for more information
-   **buy_timeout/sell_timeout** - Controls how many minutes to wait before cancelling a limit order (buy/sell) and returning to "scout" mode. 0 means that the order will never be cancelled prematurely.
-   **scout_sleep_time** - Controls how many seconds bot should wait between analysis of current prices. Since the bot now operates on websockets this value should be set to something low (like 1), the reasons to set it above 1 are when you observe high CPU usage by bot or you got api errors about requests weight limit.

### Supported coin list
To set coins for trading use the supported_coin_list file.

#### Environment Variables
All of the options provided in `user.cfg` can also be configured using environment variables.
```
CURRENT_COIN_SYMBOL:
SUPPORTED_COIN_LIST: "XLM TRX ICX EOS IOTA ONT QTUM ETC ADA XMR DASH NEO ATOM DOGE VET BAT OMG BTT"
BRIDGE_SYMBOL: USDT
API_KEY: <Your API key>
API_SECRET_KEY: <Your API Secret key>
SCOUT_MULTIPLIER: 5
SCOUT_SLEEP_TIME: 1
TLD: com
STRATEGY: default
BUY_TIMEOUT: 0
SELL_TIMEOUT: 0
```

### Pay attention
Environment Variables are in priority.

### Paying Fees with BNB
You can [use BNB to pay for any fees on the Binance platform](https://support.binance.us/hc/en-us/articles/360046786894-Using-BNB-to-Pay-for-Fees#:~:text=From%20your%20'Home'%20screen%2C,will%20be%20paid%20in%20BNB), which will reduce all fees by 25%. In order to support this benefit, the bot will always perform the following operations:
-   Automatically detect that you have BNB fee payment enabled.
-   Make sure that you have enough BNB in your account to pay the fee of the inspected trade.
-   Take into consideration the discount when calculating the trade threshold.

### Notifications with Apprise
Apprise allows the bot to send notifications to all of the most popular notification services available such as: Telegram, Discord, Slack, Amazon SNS, Gotify, etc.

To set this up you need to create a apprise.yml file in the config directory.

There is an example version of this file to get you started.

If you are interested in running a Telegram bot, more information can be found at [Telegram's official documentation](https://core.telegram.org/bots).

## Run
```shell
python -m binance_trade_bot
```

## Database Viewer (for Windows only)
A separate program was written that can display the contents of the database created by the bot in the interface.
How it works:
* Copy the file `crypto_trading.db` from the `data` directory located in the root directory of the repository to the `datbase_viewer` folder
* Now let's go to the `datbase_viewer` folder
* Launch `Dobby.exe`

Database Viewer example:
<p align="center">
  <img src = "https://github.com/paveldat/dobby-binance/blob/main/img/database_viewer.png">
</p>

## Responsibility
This project is for informational purposes only. You should not construe any such information or other material as legal, tax, investment, financial, or other advice.
Nothing contained here constitutes a solicitation, recommendation, endorsement, or offer by me or any third party service provider to buy or sell any securities or other financial instruments in this or in any other jurisdiction in which such solicitation or offer would be unlawful under the securities laws of such jurisdiction.

If you plan to use real money, USE AT YOUR OWN RISK.

Under no circumstances will I be held responsible or liable in any way for any claims, damages, losses, expenses, costs, or liabilities whatsoever, including, without limitation, any direct or indirect damages for loss of profits.
