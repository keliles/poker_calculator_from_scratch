### Poker Probability Calculator ♠️♥️♣️♦️

## Overview 🗒️

This project is a Monte Carlo simulation engine for Texas Hold’em poker. 
Given hole cards and community cards, it simulates possible outcomes and estimates each player’s probability of winning, losing, or tying.

The implementation is built from scratch in Python using only numpy, pandas, and itertools.
It incudes hand ranking logic, probability calculations, and tie resolution — without relying on poker-specific libraries.

## Features 😎

1. Accurate hand evaluation (pairs → straight flush) with subranking and further for tie resolution.
2. Monte Carlo simulation for win/tie probabilities
3. Support for multiple opponents
4. Validated against trusted sources (e.g., PokerNews odds)

## Example Input 🧑‍🦲
$ python3 poker_calculator.py

$ example: "ten of spades, jack of diamonds, queen of hearts" = TsJdQh

$ which cards are on the board already? (press enter if none)  3d4c6h

$ how many opponents are there? (must be > 0) 1

$ do you know your opponents' cards?(yes/no)  yes

$ board is 3d4c6h  
$ cards of opponent #1:  9c7d  
$ what cards do you have?  Th2c  

$ thinking...

## Example Output 💻
$ given a board of: 3d4c6h

$ where...  
$ user has: Th2c  
$ opponent #1 has: 9c7d  

$ each player's probability of winning is:  
$ user:    0.53272  
$ 1:       0.46728  
$ tie:     0.00000  

## How it works ⚙️
- Monte Carlo Simulation
  1. Takes cards of each player and combines it with the current cards on the board
  2. All cards in play are subracted from the 52 standard cards to get the remaining cards to simulate hands with
  3. Remaining cards are dealt in all possible scenarios
  4. Functions check for flush, straight, full house, etc
  5. Best 5-card hand is determined for each player
  6. Outcome of the simulated hand is stored
  7. Winning percentages are calculated and presented to the user
