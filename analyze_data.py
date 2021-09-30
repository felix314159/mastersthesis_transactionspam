import pandas as pd
# pip3 install pandas

def calculate_median():
    df = pd.read_csv("data.csv")

    # access columns by index
    gasLimit = df.iloc[:, 1]
    gasUsed = df.iloc[:, 2]

    # calculate median and round to int, since fractional gas does not exist
    # (IMO median more suited than mean since some blocks are empty)
    gasLimit_median = gasLimit.median().round()
    # result: 12478453.0
    gasUsed_median = gasUsed.median().round()
    # result: 12478453.0

    return gasLimit_median, gasUsed_median


gasLimit_median, gasUsed_median = calculate_median()
print("Analyzing blocks 11567295 to 11567314", "\n\nMedian of gasLimit:", gasLimit_median, "\nMedian of gasUsed:", gasUsed_median)


print("\nSuitable block gas limit:", int(gasLimit_median))
# i aim for contracts that use around 1/3 of avg gas used per block
print("Suitable gas for transaction spam contracts:", int(gasUsed_median / 3))

