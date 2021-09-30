import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def plot_gas_overview():
    """Plots a barchart to visualize how gas costs of certain operations changed over time."""
    
    values = [[40, "CALL",        "Frontier"], [700, "CALL",        "Muir Glacier"], [2600, "CALL",        "Berlin (Cold fee)"],
              [40, "CALLCODE",    "Frontier"], [700, "CALLCODE",    "Muir Glacier"], [2600, "CALLCODE",    "Berlin (Cold fee)"],
              [20, "BALANCE",     "Frontier"], [400, "BALANCE",     "Muir Glacier"], [2600, "BALANCE",     "Berlin (Cold fee)"],
              [20, "EXTCODESIZE", "Frontier"], [700, "EXTCODESIZE", "Muir Glacier"], [2600, "EXTCODESIZE", "Berlin (Cold fee)"],
              [20, "EXTCODEHASH", "Frontier"], [400, "EXTCODEHASH", "Muir Glacier"], [2600, "EXTCODEHASH", "Berlin (Cold fee)"]]

    # save values in dataframe (use int because fractional gas does not exist)
    df = pd.DataFrame(values, columns =["Gas", "EVM instructions", "Hard fork"], dtype = int)

    # create plot
    sns.set_theme(style="whitegrid")
    ax = sns.barplot(x="EVM instructions", y="Gas", hue="Hard fork", data=df)
    plt.show()


def plot_execution_times():
    """Plots a barchart to visualize an avg execution time comparision of certain EVM operations
       on a full node (amount of iterations adjusted to respective gas burned). Results are split
       depending on the Geth parameters used (default vs caching disabled)."""

    values = [[6.49, "STATICCALL",   "Default parameters"], [20.78, "STATICCALL",   "Caching features disabled"],
              [6.44, "DELEGATECALL", "Default parameters"], [18.43, "DELEGATECALL", "Caching features disabled"],
              [5.52, "CALL",         "Default parameters"], [15.52, "CALL",         "Caching features disabled"],
              [5.35, "CALLCODE",     "Default parameters"], [15.41, "CALLCODE",     "Caching features disabled"],
              [5.82, "BALANCE",      "Default parameters"], [44.80, "BALANCE",      "Caching features disabled"],
              [5.89, "EXTCODESIZE",  "Default parameters"], [43.53, "EXTCODESIZE",  "Caching features disabled"],
              [5.27, "EXTCODEHASH",  "Default parameters"], [42.92, "EXTCODEHASH",  "Caching features disabled"]]

    # save values in dataframe (using float values here)
    df = pd.DataFrame(values, columns =["Avg execution time in seconds", "EVM instructions", "Geth parameters"], dtype = float)

    # create plot
    sns.set_theme(style="whitegrid")
    # set title to explain under which conditions times were measured and how much gas was burned
    title = "Size of underlying blockchain: ~931 GB\nGas burned during execution (Berlin fork): ~4152896"
    ax = sns.barplot(x="EVM instructions", y="Avg execution time in seconds", hue="Geth parameters", data=df).set_title(title)
    plt.show()


# plot_gas_overview()
# plot_execution_times()
