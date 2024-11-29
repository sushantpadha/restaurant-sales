import pandas as pd
import matplotlib.pyplot as plt 

SALES_FILE_PATH = "data\\sales.csv"
FITEMS_PATH = "data\\food_items.csv"
# restaurant hours 9 am (0900) to 9 pm (2100)
RESTAURANT_HOURS = list(range(9,22))
# 1 - Monday, ..., 6 - Saturday
RESTAURANT_DAYS = list(range(1,7))
RESTAURANT_DAYNAMES = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]

COLORS = ["red", "green", "blue", "brown", "magenta", "cyan"]
XLIM = -0.3
YLIM = -0.1

def fmt_time(n):
    s = n
    try:
        if n <= 12:  # n must be int
            s = f"{n:.0f} AM"
        else:
            s = f"{(n-12):.0f} PM"
    finally:
        return s

def print_buffer(c='#'):
    print(c*72)

def greet():
    print(r"""
  ____           _                              _     ____        _
 |  _ \ ___  ___| |_ __ _ _   _ _ __ __ _ _ __ | |_  / ___|  __ _| | ___  ___ 
 | |_) / _ \/ __| __/ _` | | | | '__/ _` | '_ \| __| \___ \ / _` | |/ _ \/ __|
 |  _ <  __/\__ \ || (_| | |_| | | | (_| | | | | |_   ___) | (_| | |  __/\__ \
 |_| \_\___||___/\__\__,_|\__,_|_|  \__,_|_| |_|\__| |____/ \__,_|_|\___||___/


        Use this program to analyze, tabulate and visualize data on restaurant sales.
        Perform sales analysis by choosing from the below mentioned options:

(Type number for desired option, or simply press enter to use default option)

        """)

def capitalize(s):
    # Capitalize each word
    try:
        if isinstance(s, str):
            s=' '.join(map(str.capitalize, s.split('_')))
    finally:
        return s

def prettify_df(df):
    # capitalize dataframe labels and values for printing/plotting

    df = df.rename(capitalize, axis='columns')
    df = df.rename_axis(index=  capitalize, axis=0)
    df = df.map(capitalize)
    return df


def range_input(string, min, max, default=0):
    #Take integral input from the user lying in [min, max]
    print()
    while True:
        try:
            value = input(string)
            if value == "":
                return default
            value = int(value)
            if max >= value >= min:
                return value
            else:
                print("Value out of range please try again.")
        except ValueError as _:
            print("Invalid datatype, please enter an integer.")


def food_items_inputs(string, fitems_df):
    # Take input(s) from user where values can only be:
    # 1. names of food items available
    # 2. or, indexes for said food items
    # Stop taking inputs when user enters blank

    food_item_list = list(fitems_df["food_item"])

    print()
    print(f"Following {len(food_item_list)} food items are available at the restaurant:\n")
    print(fitems_df.to_string())

    print("\n\nSelect food item(s) OR index(es) of food item in the list, \
seperated by commas, press Enter when done.")

    while True:
        inputs = []
        try:
            value = input(string).lower()
            raw_inputs = value.split(',')
            for r in raw_inputs:
                # add user-entered food item name to list, by name,
                # if not added already
                if r in food_item_list:
                    if r not in inputs:
                        inputs.append(r)
                r = int(r)
                # add user-entered food item name to list, by index,
                # if not added already
                if r < len(food_item_list):
                    if food_item_list[r] not in inputs:
                        inputs.append(food_item_list[r])
                else:
                    print(f"Value `{r}` not in set of possible values. Skipping.")
                    continue
            break
        except ValueError as _:
            print("Invalid datatype, please enter a name or index. Try again.")
            continue

    inputs.sort()
    return inputs


def menu(fitems_df):
    # Display front end interface menu for user

    # Plot hourly or daily sales data
    print_buffer()
    print("""Plot sales data
[0] per Hour (default option)
[1] per Weekday
[2] per Food Item""")
    axis = range_input("Select option: ", 0,2, 0)

    # Plot hourly or daily sales data
    if axis in (0,1):
        print_buffer()
        print("""Group data according to
[0] None (default option)
[1] Food Category
[2] Order Type (dine or delivery)
[3] Food Type (veg or non-veg)
[4] Food Item (any specific food item)""")
        group = range_input("Select option: ", 0,4, 0)
        food_items = None
        # if 4th option selected, ask for food items input
        if group == 4:
            food_items = food_items_inputs("Enter name or index: ", fitems_df)

    # Plot food item-wise sales data
    if axis == 2:
        group = -1
        food_items = food_items_inputs("Enter name or index: ", fitems_df)

    print_buffer()
    print("""Type of graph
[0] Line graph (default option)
[1] (Stacked) Bar graph""")
    graph = range_input("Select option: ", 0,1, 0)

    print_buffer()
    return (axis, group, graph, food_items)


def read_data():
    sales_df = pd.read_csv(SALES_FILE_PATH)
    fitems_df = pd.read_csv(FITEMS_PATH)

    _df = sales_df.merge(fitems_df, left_on="food_item", right_on="food_item")

    return _df, sales_df, fitems_df


def create_df(_df, inp):
    # Creates new dataframe based on user input, which contains data related to query
    # Data is then aggregated using pivot_table function

    # unpack inputs
    axis, group, graph, food_items = inp

    df = _df.copy(deep=True)
    for i, t in df["time"].items():
        df.at[i, "hour"] = round(t/100)  # convert standard time to hours

    # AXIS INPUT
    if axis == 0:
        index_name = "hour"
        index = RESTAURANT_HOURS
    if axis == 1:
        index_name = "day"
        index = RESTAURANT_DAYNAMES
    if axis == 2:
        index_name = "food_item"
        index = food_items

    # GROUP INPUT
    if group == 0:
        # aggregate all orders by given index (hourly or daily)
        kwargs = {"values": "quantity", "columns": None}
    elif group == 1:
        # aggregate orders based on food category
        kwargs = {"values": "quantity", "columns": "food_category"}
    elif group == 2:
        # aggregate orders based on order type
        kwargs = {"values": "quantity", "columns": "order_type"}
    elif group == 3:
        # aggregate orders based on food type
        kwargs = {"values": "quantity", "columns": "food_type"}
    elif group == 4:
        # aggregate orders for particular food item(s)
        kwargs = {"values": "quantity", "columns": "food_item"}
    elif group == -1:
        # aggregate orders based on food items
        kwargs = {"values": "quantity", "columns": None}

    # Remove any instances of food items that are not to be aggregated
    # This is done to speed up pivoting later by removing unneeded data
    if food_items:
        df = df.drop(
            [r_i for r_i,r_s in df.iterrows() if r_s["food_item"] not in food_items]
        )

    # Check if dataframe contains all zeroes/all False values
    # It may be empty if requested aggregate functions all give 0
    if not df.any().any():
        print("\n\n<< Invalid data analysis request. No data left to \
analyze under given conditions. Please try again. >>")
        exit()

    # Pivot table based on user input
    df = df.pivot_table(index=index_name, **kwargs, aggfunc="sum", fill_value=0)

    # Fill blank values as 0
    df = df.reindex(index, fill_value=0)
    df.fillna(0, inplace=True)

    return df


def analyze_df(df, inp):
    # Print brief analysis of new dataframe

    # unpack inputs
    axis, group, graph, food_items = inp

    pretty_df = prettify_df(df)

    print_buffer('-')
    print("Compiled sales data:")
    print_buffer('-')
    print(pretty_df)
    print_buffer('-')
    print("Sales data highlights:") 
    print_buffer('-')

    ## hourly or daily analysis
    if axis in (0,1):

        # create agg_df consisting `sum`, `median`, `max`, `idxmax` values for
        # each original column and a `total` column
        _d = df.agg('sum', axis=1)
        _d.name = "total"
        total_df = df.join(_d)

        agg_df = total_df.agg(['sum', 'max'], axis=0)
        agg_df.loc["idxmax"] = total_df.idxmax().astype(str)

        # creating templates for printing data
        # so it can be extended to more complex data if needed
        data = []

        # hourly
        if axis == 0:
            s1 = "during"
            s2 = "Hour"
            agg_df.loc["idxmax"] = agg_df.loc["idxmax"].apply(fmt_time).apply(capitalize)
        # daily
        if axis == 1:
            s1 = "on"
            s2 = "Day"

        s3 = agg_df.loc["idxmax","total"]  # busiest day/hour


        # group by food category
        if group == 1:
            for col in df:
                data.append(
                    (f"'{capitalize(col)}' orders {s1}", agg_df.loc["idxmax",col], agg_df.loc["max",col])
                )
        # group by order type
        if group == 2:
            data.extend([
                (f"dine-in orders {s1}", agg_df.loc["idxmax","dine"], agg_df.loc["max","dine"]),
                (f"delivery orders {s1}", agg_df.loc["idxmax","delivery"], agg_df.loc["max","delivery"])
            ])
        # group by food type
        if group == 3:
            data.extend([
                (f"veg orders {s1}", agg_df.loc["idxmax","veg"], agg_df.loc["max","veg"]),
                (f"non-veg orders {s1}", agg_df.loc["idxmax","non-veg"], agg_df.loc["max","non-veg"])
            ])
        # group by food items
        if group == 4:
            for col in df:
                data.append(
                    (f"orders of '{capitalize(col)}' {s1}", agg_df.loc["idxmax",col], agg_df.loc["max",col])
                )

        print(f"Busiest {s2}: {s3} ({agg_df.loc['max','total']} orders)")
        for k,v,w in data:
            print(f"Most {k}: {capitalize(v)} ({w:.0f} orders)")

    # food item wise analysis
    if axis == 2:
        # only one column: quantity
        n = 3
        i = 1
        _d = df.sort_values("quantity",ascending=False).head(n)
        print("Most ordered dishes:")
        for r_i, r_s in _d.iterrows():
            print(f"{i}.\t{capitalize(r_i)} ({r_s['quantity']} orders)")
            i +=1

    print_buffer('-')


def plot_df(df, inp):
    # Generate plots based on new dataframe

    # unpack inputs
    axis, group, graph, food_items = inp

    # GENERATE DATA SETS FOR PLOTTING (data as Series, color, label)
    datasets = []
    for i, col in enumerate(df):
        color = COLORS[i % len(COLORS)]
        group = (df[col], color, str(col))
        datasets.append(group)

    # AXIS INPUT
    if axis == 0:
        xlabel = "Hour"
        xticks = RESTAURANT_HOURS
        xlim = RESTAURANT_HOURS[0] + XLIM
    elif axis == 1:
        xlabel = "Weekday"
        xticks = list([i-1 for i in RESTAURANT_DAYS])  # start list at 0
        xlim = XLIM
    elif axis == 2:
        xlabel = "Food Items"
        xticks = list(range(len(food_items)))
        xlim = XLIM

    # alternatively, use this function for quick plotting
    # df.plot(kind="line", title="Sales Analysis", plt)

    # GRAPH INPUT
    # line graph
    if graph == 0:
        for d in datasets:
            plt.plot(d[0], marker="o", color=d[1], label=d[2], linestyle="solid")

    # bar graph
    elif graph == 1:
        # cumulative heights are used to make stacked bar graph, i.e,
        # every dataset's bars are stacked on top previous dataset's bars

        # initialize cumulative height
        cum_heights = datasets[0][0].values.copy()
        cum_heights[:] = 0
        for d in datasets:
            heights = d[0].values
            plt.bar(d[0].index, heights, color=d[1], label=d[2], bottom=cum_heights)
            cum_heights[:] += heights

    plt.xlabel(xlabel)
    plt.xticks(xticks, rotation=30)
    plt.xlim(xlim)
    plt.ylim(bottom=YLIM)
    plt.ylabel("Orders / Sales")
    plt.title("Sales Analysis")
    plt.legend()
    plt.show()


def main():
    # Greet user and give instructions
    greet()

    # Read required csv files. Catch any errors and report to the use
    try: _df, sales_df, fitems_df = read_data()
    except Exception as e:
        print("Error in reading csv files")
        print(e)
        exit

    # Initialize menu to take user input
    user_input = menu(fitems_df)

    # Create new dataframe based on user input
    df = create_df(_df, user_input)

    # Generate basic data analysis
    analyze_df(df, user_input)
    input("Press Enter to see plot.")

    # Plot datasets from the new dataframe based on user input
    plot_df(prettify_df(df), user_input)

    return


if __name__ == "__main__":
    main()
