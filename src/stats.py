import pandas as pd
import plotly.express as px
import pytz


def get_stats(diary: pd.DataFrame):
    word_count = diary["entry"].str.split().str.len().sum()
    entries = len(diary)
    mean_words = round(word_count / entries, 2)

    ## generate a historgram of the number of entries per day
    ## plot it with seaborn
    distrubution_over_weekdays = diary["date"].dt.day_name().value_counts()
    # sort the days of the week
    distrubution_over_weekdays = distrubution_over_weekdays.reindex(
        [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
    )
    distrubution_over_weekdays = (
        distrubution_over_weekdays.to_frame()
        .reset_index()
        .rename(columns={"index": "weekday", "date": "entries"})
    )

    fig = px.bar(
        distrubution_over_weekdays,
        x="weekday",
        y="entries",
        title="Number of entries per weekday",
        color="entries",
        color_continuous_scale=px.colors.sequential.Sunsetdark,
        width=800,
        height=400,
        text="entries",
    )
    entries_per_weekday = "/tmp/entries_per_weekday.png"
    fig.write_image(entries_per_weekday, format="png", engine="kaleido")

    # distribution over months
    distrubution_over_months = diary["date"].dt.month_name().value_counts()
    # sort the months
    distrubution_over_months = distrubution_over_months.reindex(
        [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ]
    )
    distrubution_over_months = (
        distrubution_over_months.to_frame()
        .reset_index()
        .rename(columns={"index": "month", "date": "entries"})
    )
    fig = px.bar(
        distrubution_over_months,
        x="month",
        y="entries",
        title="Number of entries per month",
        color="entries",
        color_continuous_scale=px.colors.sequential.Sunsetdark,
        width=800,
        height=400,
        text="entries",
    )
    entries_per_month = "/tmp/entries_per_month.png"
    fig.write_image(entries_per_month, format="png", engine="kaleido")

    stats = f"Stats:\n\nNumber of entries: {entries}\nNumber of words: {word_count}\nMean words per entry: {mean_words}"
    return stats, entries_per_weekday, entries_per_month
