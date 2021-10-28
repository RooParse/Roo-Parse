import pandas as pd
import datetime
import matplotlib as mpl
import matplotlib.pyplot as plt
import os.path

mpl.use('TkAgg')
plt.ioff()


def format_numeric_columns(df=None, columns=None, prefix='', suffix='', decimals=2, inplace=True):
    if columns is None:
        raise TypeError('Please specify columns')

    if not inplace:
        df = df.copy()

    for col_name in columns:
        df[col_name] = df[col_name].apply(lambda x: '{prefix}{x:.{decimals}f}{suffix}'.format(x=x, prefix=prefix,
                                                                                              suffix=suffix,
                                                                                              decimals=decimals))
        if prefix == '' and suffix == '':
            df[col_name] = df[col_name].apply(lambda x: float(x))

    if not inplace:
        return df


def calculate_summaries(data_df, output_dir=None):
    df = data_df.copy()

    # Daily summary
    cols = ['hours_worked', 'orders_delivered', 'Total']
    df[cols] = df[cols].apply(pd.to_numeric, errors='coerce', axis=1)
    df['Date'] = df['Date'].map(str)
    df['Date'] = pd.to_datetime(df['Date'], format='%d-%m-%y')
    daily_summary = df.groupby('Date').agg({'hours_worked': 'sum', 'orders_delivered': 'sum', 'Total': 'sum'})
    daily_summary.rename(columns={'Total': 'total_earnings'}, inplace=True)
    daily_summary['mean_per_order'] = daily_summary['total_earnings'] / daily_summary['orders_delivered']
    daily_summary['mean_per_hour'] = daily_summary['total_earnings'] / daily_summary['hours_worked']
    daily_summary['date'] = daily_summary.index
    daily_summary = daily_summary.sort_values(by='date')

    # Daily summary to save
    daily_summary_to_save = daily_summary[['date', 'hours_worked', 'mean_per_hour',
                                           'orders_delivered', 'mean_per_order', 'total_earnings']]
    daily_summary_to_save['date'] = daily_summary_to_save['date'].dt.date
    daily_summary_to_save.reset_index(drop=True, inplace=True)

    format_numeric_columns(daily_summary_to_save, columns=['mean_per_hour', 'mean_per_order', 'total_earnings'],
                           # prefix=u'\u00A3' + ' ',
                           decimals=2)
    format_numeric_columns(daily_summary_to_save, columns=['hours_worked'],
                           # suffix=' h',
                           decimals=1)
    format_numeric_columns(daily_summary_to_save, columns=['orders_delivered'],
                           decimals=0)

    daily_summary_to_save.rename(columns={'date': 'Date',
                                          'hours_worked': 'Hours worked',
                                          'mean_per_hour': 'Per HOUR average earnings',
                                          'orders_delivered': 'Orders delivered',
                                          'mean_per_order': 'Per ORDER average earnings',
                                          'total_earnings': 'Total earnings'
                                          }, inplace=True)

    # Weekly summaries
    weekly_summary = daily_summary.copy()
    weekly_summary['first_day_of_the_week'] = weekly_summary.date - pd.TimedeltaIndex(weekly_summary.date.dt.dayofweek,
                                                                                      unit='d')

    weekly_summary = weekly_summary.groupby('first_day_of_the_week').agg({'hours_worked': 'sum',
                                                                          'orders_delivered': 'sum',
                                                                          'total_earnings': 'sum'})
    weekly_summary['mean_per_order'] = weekly_summary['total_earnings'] / weekly_summary['orders_delivered']
    weekly_summary['mean_per_hour'] = weekly_summary['total_earnings'] / weekly_summary['hours_worked']
    weekly_summary['first_day_of_the_week'] = weekly_summary.index
    weekly_summary.index = pd.to_datetime(weekly_summary.index)
    weekly_summary.sort_index(inplace=True)

    weekly_summary['week_string'] = weekly_summary.first_day_of_the_week.dt.strftime('%Y-week%W')
    weekly_summary['first_day_of_the_week'] = weekly_summary['first_day_of_the_week'].dt.date
    weekly_summary['last_day_of_the_week'] = weekly_summary.index + datetime.timedelta(days=6)
    weekly_summary['last_day_of_the_week'] = weekly_summary['last_day_of_the_week'].dt.date
    weekly_summary.reset_index(inplace=True, drop=True)

    weekly_summary['week_daterange'] = pd.Series(
        [f'{str(f)} - {str(l)}' for f, l in zip(weekly_summary['first_day_of_the_week'],
                                                weekly_summary['last_day_of_the_week'])]
    )

    weekly_summary['midweek'] = weekly_summary['first_day_of_the_week'] + datetime.timedelta(days=3, hours=12)

    # Weekly summary to save
    weekly_summary_to_save = weekly_summary[['week_daterange', 'hours_worked', 'mean_per_hour',
                                             'orders_delivered', 'mean_per_order', 'total_earnings']]

    format_numeric_columns(weekly_summary_to_save, columns=['mean_per_hour', 'mean_per_order', 'total_earnings'],
                           # prefix=u'\u00A3' + ' ',
                           decimals=2)
    format_numeric_columns(weekly_summary_to_save, columns=['hours_worked'],
                           # suffix=' h',
                           decimals=1)
    format_numeric_columns(weekly_summary_to_save, columns=['orders_delivered'],
                           decimals=0)

    weekly_summary_to_save.rename(columns={'week_daterange': 'Week',
                                           'hours_worked': 'Hours worked',
                                           'mean_per_hour': 'Per HOUR average earnings',
                                           'orders_delivered': 'Orders delivered',
                                           'mean_per_order': 'Per ORDER average earnings',
                                           'total_earnings': 'Total earnings'
                                           }, inplace=True)
    weekly_summary_to_save.reset_index(inplace=True, drop=True)

    # Monthly summaries
    monthly_summary = daily_summary.copy()
    monthly_summary['year'] = monthly_summary.date.dt.year
    monthly_summary['month'] = monthly_summary.date.dt.month

    monthly_summary = monthly_summary.groupby(['year', 'month'], as_index=False).agg({'hours_worked': 'sum',
                                                                                      'orders_delivered': 'sum',
                                                                                      'total_earnings': 'sum'})

    # Calculate middle of month (for plotting purposes)
    month_start = pd.Series(pd.to_datetime([f'{y}-{m}-01' for y, m in zip(monthly_summary['year'],
                                                                          monthly_summary['month'])]))
    month_end = pd.Series(pd.to_datetime(
        [f'{y + 1 if m == 12 else y}-{m + 1 if m != 12 else 1}-01' for y, m in zip(monthly_summary['year'],
                                                                                   monthly_summary['month'])]))

    monthly_summary['midmonth'] = month_start + (month_end - month_start) / 2

    monthly_summary['mean_per_order'] = monthly_summary['total_earnings'] / monthly_summary['orders_delivered']
    monthly_summary['mean_per_hour'] = monthly_summary['total_earnings'] / monthly_summary['hours_worked']

    monthly_summary_to_save = monthly_summary[['year', 'month', 'hours_worked', 'mean_per_hour',
                                               'orders_delivered', 'mean_per_order', 'total_earnings']]

    monthly_summary_to_save.sort_values(by=['year', 'month'], ascending=[True, True], inplace=True)

    format_numeric_columns(monthly_summary_to_save, columns=['mean_per_hour', 'mean_per_order', 'total_earnings'],
                           # prefix=u'\u00A3' + ' ',
                           decimals=2)
    format_numeric_columns(monthly_summary_to_save, columns=['hours_worked'],
                           # suffix=' h',
                           decimals=1)
    format_numeric_columns(monthly_summary_to_save, columns=['orders_delivered'],
                           decimals=0)

    monthly_summary_to_save.rename(columns={'year': 'Year',
                                            'month': 'Month',
                                            'hours_worked': 'Hours worked',
                                            'mean_per_hour': 'Per HOUR average earnings',
                                            'orders_delivered': 'Orders delivered',
                                            'mean_per_order': 'Per ORDER average earnings',
                                            'total_earnings': 'Total earnings'
                                            }, inplace=True)
    monthly_summary_to_save.reset_index(inplace=True, drop=True)

    # Yearly summaries
    yearly_summary = daily_summary.copy()
    yearly_summary['year'] = yearly_summary.date.dt.year

    yearly_summary = yearly_summary.groupby(['year'], as_index=False).agg({'hours_worked': 'sum',
                                                                           'orders_delivered': 'sum',
                                                                           'total_earnings': 'sum'})

    yearly_summary['mean_per_order'] = yearly_summary['total_earnings'] / yearly_summary['orders_delivered']
    yearly_summary['mean_per_hour'] = yearly_summary['total_earnings'] / yearly_summary['hours_worked']

    yearly_summary_to_save = yearly_summary[['year', 'hours_worked', 'mean_per_hour',
                                             'orders_delivered', 'mean_per_order', 'total_earnings']]

    yearly_summary_to_save.sort_values(by='year', ascending=True, inplace=True)

    format_numeric_columns(yearly_summary_to_save, columns=['mean_per_hour', 'mean_per_order', 'total_earnings'],
                           # prefix=u'\u00A3' + ' ',
                           decimals=2)
    format_numeric_columns(yearly_summary_to_save, columns=['hours_worked'],
                           # suffix=' h',
                           decimals=1)
    format_numeric_columns(yearly_summary_to_save, columns=['orders_delivered'],
                           decimals=0)

    yearly_summary_to_save.rename(columns={'year': 'Year',
                                           'hours_worked': 'Hours worked',
                                           'mean_per_hour': 'Per HOUR average earnings',
                                           'orders_delivered': 'Orders delivered',
                                           'mean_per_order': 'Per ORDER average earnings',
                                           'total_earnings': 'Total earnings'
                                           }, inplace=True)
    yearly_summary_to_save.reset_index(inplace=True, drop=True)

    html_tables = {
        'daily': daily_summary_to_save.to_html(index=False, col_space=200, table_id='daily_table'),
        'weekly': weekly_summary_to_save.to_html(index=False, col_space=200, table_id='weekly_table'),
        'monthly': monthly_summary_to_save.to_html(index=False, col_space=200, table_id='monthly_table'),
        'yearly': yearly_summary_to_save.to_html(index=False, col_space=200, table_id='yearly_table')
    }

    html_all_tables_str = '<br /><br /><br />'.join(
        [html_tables['daily'], html_tables['weekly'], html_tables['monthly'],
         html_tables['yearly']])

    if output_dir is not None:
        daily_summary_dir = os.path.join(output_dir, 'Daily summary')
        weekly_summary_dir = os.path.join(output_dir, 'Weekly summary')
        monthly_summary_dir = os.path.join(output_dir, 'Monthly summary')
        yearly_summary_dir = os.path.join(output_dir, 'Yearly summary')

        os.makedirs(daily_summary_dir, exist_ok=True)
        os.makedirs(weekly_summary_dir, exist_ok=True)
        os.makedirs(monthly_summary_dir, exist_ok=True)
        os.makedirs(yearly_summary_dir, exist_ok=True)

        daily_summary_to_save.to_csv(path_or_buf=os.path.join(daily_summary_dir, 'Daily summary.csv'),
                                     index=False,
                                     encoding='utf-8')
        weekly_summary_to_save.to_csv(path_or_buf=os.path.join(weekly_summary_dir, 'Weekly summary.csv'),
                                      index=False,
                                      encoding='utf-8')
        monthly_summary_to_save.to_csv(path_or_buf=os.path.join(monthly_summary_dir, 'Monthly summary.csv'),
                                       index=False,
                                       encoding='utf-8')
        yearly_summary_to_save.to_csv(path_or_buf=os.path.join(yearly_summary_dir, 'Yearly summary.csv'),
                                      index=False,
                                      encoding='utf-8')

        with open(os.path.join(output_dir, 'All summary tables.html'), 'w', encoding='utf-8',
                  newline='\n') as report_html_f:
            report_html_f.write(html_all_tables_str)

        # with pd.ExcelWriter(os.path.join(output_dir, 'All summaries (spreadsheet).xlsx')) as writer:
        #     daily_summary_to_save.to_excel(writer, sheet_name='Daily')
        #     weekly_summary_to_save.to_excel(writer, sheet_name='Weekly')
        #     monthly_summary_to_save.to_excel(writer, sheet_name='Monthly')
        #     yearly_summary_to_save.to_excel(writer, sheet_name='Yearly')
        # To be added together with formatting (wrap line, columns widths).

    return {
        'daily_summary': daily_summary,
        'daily_summary_to_save': daily_summary_to_save,
        'weekly_summary': weekly_summary,
        'weekly_summary_to_save': weekly_summary_to_save,
        'monthly_summary': monthly_summary,
        'monthly_summary_to_save': monthly_summary_to_save,
        'yearly_summary': yearly_summary,
        'yearly_summary_to_save': yearly_summary_to_save,
        'html_tables': html_tables,
        'html_all_tables_str': html_all_tables_str
    }


def create_summary_graphs(data_df=None, summaries_dict=None, output_dir=None):
    if data_df is not None and summaries_dict is None:
        summaries_dict = calculate_summaries(data_df)

    if output_dir is None or isinstance(output_dir, str) is False or os.path.exists(output_dir) is False:
        raise Exception('Please specify a valid output directory')

    weekly_summary = summaries_dict['weekly_summary']
    monthly_summary = summaries_dict['monthly_summary']
    yearly_summary = summaries_dict['yearly_summary']

    weekly_summary_dir = os.path.join(output_dir, 'Weekly summary')
    monthly_summary_dir = os.path.join(output_dir, 'Monthly summary')
    yearly_summary_dir = os.path.join(output_dir, 'Yearly summary')

    os.makedirs(weekly_summary_dir, exist_ok=True)
    os.makedirs(monthly_summary_dir, exist_ok=True)
    os.makedirs(yearly_summary_dir, exist_ok=True)

    mpl.use('TkAgg')  # use Tk backend
    plt.ioff()  # disable interactive mode

    # Earnings per hour - weekly average
    fig, ax = plt.subplots()
    ax.plot(weekly_summary['midweek'],
            weekly_summary['mean_per_hour'],
            color='k')
    ax.grid(which='major', axis='y')
    ax.tick_params(axis='x', labelrotation=70)
    ax.set_ylabel('Average earnings per HOUR  (' + u'\u00A3' + ') ')
    fig.tight_layout()
    fig.savefig(os.path.join(weekly_summary_dir, 'Earnings per HOUR - weekly average graph.png'))

    # Earnings per order - weekly average
    fig, ax = plt.subplots()
    ax.plot(weekly_summary['midweek'],
            weekly_summary['mean_per_order'],
            color='k')
    ax.grid(which='major', axis='y')
    ax.tick_params(axis='x', labelrotation=70)
    ax.set_ylabel('Average earnings per ORDER  (' + u'\u00A3' + ') ')
    fig.tight_layout()
    fig.savefig(os.path.join(weekly_summary_dir, 'Earnings per ORDER - weekly average graph.png'))

    mpl.use('TkAgg')  # use Tk backend
    plt.ioff()  # disable interactive mode

    # Earnings per hour - monthly average
    fig, ax = plt.subplots()
    ax.plot(monthly_summary['midmonth'],
            monthly_summary['mean_per_hour'],
            color='k')
    ax.grid(which='major', axis='y')
    ax.tick_params(axis='x', labelrotation=70)
    ax.set_ylabel('Average earnings per HOUR  (' + u'\u00A3' + ') ')
    fig.tight_layout()
    fig.savefig(os.path.join(monthly_summary_dir, 'Earnings per HOUR - monthly average graph.png'))

    # Earnings per order - monthly average
    fig, ax = plt.subplots()
    ax.plot(monthly_summary['midmonth'],
            monthly_summary['mean_per_order'],
            color='k')
    ax.grid(which='major', axis='y')
    ax.tick_params(axis='x', labelrotation=70)
    ax.set_ylabel('Average earnings per ORDER  (' + u'\u00A3' + ') ')
    fig.tight_layout()
    fig.savefig(os.path.join(monthly_summary_dir, 'Earnings per ORDER - monthly average graph.png'))


def test():
    # Main function is for testing purposes only
    # Requires data.csv saved in the project directory (as extracted by gui.py)
    data_df = pd.read_csv('data.csv', dtype=str)
    summaries = calculate_summaries(data_df, output_dir='summary_tables')
    create_summary_graphs(summaries_dict=summaries, output_dir='graphs')


if __name__ == '__main__':
    test()
