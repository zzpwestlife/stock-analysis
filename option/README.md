# American Option Strategy Pricing Calculator

This is a Python program for calculating the theoretical price of American option strategies. It uses a binomial tree model (Cox-Ross-Rubinstein model) to price American options and can handle multi-leg option strategies.

## Features

- Calculate theoretical prices for individual American options (calls/puts)
- Calculate total price for multi-leg option strategies
- Generate payoff diagrams for option strategies
- Support both command-line arguments and interactive input
- Web-based interface for easier interaction

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Command-Line Arguments

```bash
python option_calculator.py --price 100 --rate 0.05 --vol 0.3 --legs "C,105,30,1" "P,95,30,-1"
```

Parameter details:
- `--price`: Underlying asset price
- `--rate`: Risk-free interest rate (decimal form, e.g., 0.05 for 5%)
- `--vol`: Volatility (decimal form, e.g., 0.3 for 30%)
- `--legs`: Option leg information, format: "type(C/P),strike,days_to_expiry,quantity"
  - type: C for call option, P for put option
  - strike: Strike price of the option
  - days_to_expiry: Days remaining until option expiration
  - quantity: Positive for long positions, negative for short positions

### Interactive Mode

If you don't provide the `--legs` parameter, the program will enter interactive mode and prompt you to input option leg information:

```bash
python option_calculator.py --price 100 --rate 0.05 --vol 0.3
```

## Web Interface

The project also includes a web-based interface for easier interaction with the option pricing model:

### Option Calculator Web Interface

To start the web interface:

```bash
python start_option_calculator.py
```

This will:
1. Start the API backend server
2. Open the calculator in your default web browser

In the web interface, you can:
- Set common parameters (underlying price, risk-free rate, volatility)
- Add multiple option legs to create complex strategies
- Remove unwanted legs
- Calculate prices and Greeks for the entire strategy
- View prices for individual legs and their contribution to the total

The web interface works by calling the same option pricing code used in the command-line tools, ensuring consistent results.

If the backend server fails to start, the interface will fall back to a simplified simulation mode.

### Requirements for Web Interface

The web interface requires additional packages:
- Flask
- Flask-CORS

These are included in the requirements.txt file.

## Examples

Calculate a bull call spread strategy (long a lower strike call, short a higher strike call):

```bash
python option_calculator.py --price 100 --rate 0.05 --vol 0.3 --legs "C,95,30,1" "C,105,30,-1"
```

## Technical Details

- Uses binomial tree model to calculate American option prices
- Accounts for the possibility of early exercise
- Payoff diagram shows the profit/loss of the option strategy at different underlying asset prices

生成一个 html 文件, 需要实现可以增加或删除期权策略中的一条或多条腿, 然后展示每腿的价格以及整个策略的价格.
