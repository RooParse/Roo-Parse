import pandas as pd
import datetime
from datetime import date
from plotnine import *
from mizani.breaks import date_breaks
from mizani.formatters import date_format


def create_graphs_from_data(data_df):
    def custom_date_format2(breaks):
        """
        Function to format the date
        """
        res = []
        for x in breaks:
            # First day of the year
            if x.month == 1 and x.day == 1:
                fmt = '%Y'
            # Every other month
            elif x.month % 2 != 0:
                fmt = '%b'
            else:
                fmt = ''

            res.append(date.strftime(x, fmt))

        return res

    cols = ['Hours_worked', 'Orders', 'Total']
    data_df[cols] = data_df[cols].apply(pd.to_numeric, errors='coerce', axis=1)
    data_df["Date"] = data_df["Date"].map(str)
    data_df["Date"] = pd.to_datetime(data_df["Date"], format="%d-%m-%y")
    daily_summary = data_df.groupby("Date").agg({"Hours_worked": "sum", "Orders": "sum", "Total": "sum"})
    daily_summary["mean_per_order"] = daily_summary["Total"] / daily_summary["Orders"]
    daily_summary["date"] = daily_summary.index  # this doesn't work properly lol
    daily_summary = daily_summary.sort_values(by="date")

    weekly_summary = daily_summary.copy()
    weekly_summary['first_day_of_the_week'] = weekly_summary.date - pd.TimedeltaIndex(weekly_summary.date.dt.dayofweek,
                                                                                      unit='d')

    weekly_summary = weekly_summary.groupby("first_day_of_the_week").agg({"Hours_worked": "sum",
                                                                          "Orders": "sum",
                                                                          "Total": "sum"})
    weekly_summary["mean_per_order"] = weekly_summary["Total"] / weekly_summary["Orders"]
    weekly_summary["mean_per_hour"] = weekly_summary["Total"] / weekly_summary["Hours_worked"]
    weekly_summary["first_day_of_the_week"] = weekly_summary.index
    weekly_summary.index = pd.to_datetime(weekly_summary.index)
    weekly_summary.sort_index(inplace=True)

    weekly_summary["week_string"] = weekly_summary.first_day_of_the_week.dt.strftime("%Y-week%W")
    weekly_summary["first_day_of_the_week"] = weekly_summary.first_day_of_the_week.dt.date

    weekly_summary["midweek"] = weekly_summary.index + datetime.timedelta(days=3, hours=12)

    # weekly_plot_order_mean = weekly_summary.plot(x="first_day_of_the_week", y="mean_per_order")

    plot_mean_per_order_weekly = ggplot(data=weekly_summary, mapping=aes(x="midweek", y="mean_per_order")) + \
        geom_path(aes(group=1)) + theme_bw() + \
        scale_x_datetime(name="", breaks=date_breaks('1 months'), labels=custom_date_format2,
                      minor_breaks=[]) + \
        ggtitle("Earnings per order (weekly average)") + \
        scale_y_continuous(name="Earnings / order (£)")
    # print(plot_mean_per_order_weekly)

    plot_mean_per_hour_weekly = ggplot(data=weekly_summary, mapping=aes(x="midweek", y="mean_per_hour")) + \
        geom_path(aes(group=1)) + theme_bw() + \
        scale_x_datetime(name="", breaks=date_breaks('1 months'), labels=custom_date_format2,
                         minor_breaks=[]) + \
        ggtitle("Earnings per hour (weekly average)") + \
        scale_y_continuous(name="Earnings / hour (£)")
    # print(plot_mean_per_hour_weekly)

    return {"plot_mean_per_order_weekly": plot_mean_per_order_weekly,
            "plot_mean_per_hour_weekly": plot_mean_per_hour_weekly}


def main():
    # Main function is for testing purposes only
    # Requires data.csv saved in the project directory (as extracted by gui.py)
    data_df = pd.read_csv("data.csv", dtype=str)
    # data_df["Date"] = data_df["Date"].map(str)
    # data_df["Date"] = pd.to_datetime(data_df["Date"], format="%d-%m-%y")

    graphs = create_graphs_from_data(data_df)

    for key, plot in graphs.items():
        print(plot)
        plot.save(filename=key + ".png")


if __name__ == "__main__":
    main()
