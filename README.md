# Poker AI Agent

A heads-up poker betting agent that recommends what to do preflop, flop, turn, and river against one opponent.

The project includes:
- a rule-based betting agent
- Monte Carlo postflop equity estimation
- a terminal demo
- a clickable desktop GUI for selecting cards and entering betting amounts in dollars

## Features

- Recommends `fold`, `check`, `call`, `bet`, `raise`, or `all_in`
- Suggests a recommended dollar amount
- Supports preflop, flop, turn, and river decisions
- Lets you click cards in a GUI instead of typing them manually
- Shows confidence and a short explanation for each recommendation

## Project Structure

- [gui.py](/c:/Users/Admin/Documents/PokerAI_1/gui.py): desktop GUI
- [demo.py](/c:/Users/Admin/Documents/PokerAI_1/demo.py): terminal-based interactive runner
- [poker_agent/agent.py](/c:/Users/Admin/Documents/PokerAI_1/poker_agent/agent.py): betting logic
- [poker_agent/evaluator.py](/c:/Users/Admin/Documents/PokerAI_1/poker_agent/evaluator.py): hand evaluation and Monte Carlo equity
- [poker_agent/models.py](/c:/Users/Admin/Documents/PokerAI_1/poker_agent/models.py): game state and action models
- [tests/test_agent.py](/c:/Users/Admin/Documents/PokerAI_1/tests/test_agent.py): test cases

## Requirements

- Python 3.10+
- No extra packages required for the current version

## How to Run

Run the GUI:

```bash
python gui.py
```

Run the terminal demo:

```bash
python demo.py
```

Run the tests:

```bash
python -m unittest discover -s tests -v
```

## How It Works

### Preflop

The agent groups starting hands into strength tiers such as premium, strong, and playable hands. It uses those groups together with pot pressure to decide whether to play aggressively, call, check, or fold.

### Postflop

On the flop, turn, and river, the agent estimates hand equity against one opponent using Monte Carlo simulation. It compares that equity to pot odds and uses betting heuristics to recommend an action and sizing.

## GUI Inputs

The GUI lets you enter:
- your hole cards
- flop, turn, and river cards
- pot size in dollars
- amount to call in dollars
- your remaining stack
- opponent remaining stack
- minimum raise
- big blind
- position

## Example

If you enter a hand like:

- Hole cards: `A♥ K♦`
- Flop: `Q♠ J♣ 2♥`
- Pot size: `$10`
- To call: `$3`

the agent will estimate your hand strength and recommend the best action with a dollar amount and reasoning.

## Current Status

This version is a rule-based baseline, not a trained machine learning model yet.

Current progress:
- implemented heads-up betting logic
- added postflop Monte Carlo simulation
- built a GUI with clickable cards
- added tests for common scenarios

## Future Improvements

- generate self-play training data
- add more features about the board and betting situation
- train a simple machine learning model
- compare the ML model with the rule-based baseline
- improve opponent modeling

## Author

Brandon Nguyen
