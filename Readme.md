# Dobby - Binance Trade Bot

## Introduction
According to our observations and monitoring of the crypto market for a long time, we have revealed that all coins follow Bitcoin's lead; the difference is their phase offset.

## What is the `BRIDGE CURRENCY`?
Unfortunately, the Binance crypto exchange does not have all crypto assets, so Binance does not have markets for every pair of altcoins.
The workaround for this is to use a bridge currency that will complement missing pairs.
The default bridge currency is Tether (USDT), which is stable by design and compatible with nearly every coin on the Binance platform.
Instead of Tether (USDT), the user can set his coin as a bridge currency.

<p align="center">
  Coin A → <BRIDGE CURRENCY COIN> → Coin B
</p>

The way the bot takes advantage of the observed behaviour is to always downgrade from the "strong" coin to the "weak" coin, under the assumption that at some point the tables will turn.
It will then return to the original coin, ultimately holding more of it than it did originally. This is done while taking into consideration the trading fees.

<div align="center">
  <p><b>Coin A</b> → <BRIDGE CURRENCY COIN> → Coin B</p>
  <p>Coin B → <BRIDGE CURRENCY COIN> → Coin C</p>
  <p>...</p>
  <p>Coin Z → <BRIDGE CURRENCY COIN> → <b>Coin A</b></p>
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