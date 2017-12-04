import pandas as pd
import datetime
from io import StringIO
import boto3


def load_data(sample):
    s3bucket = "twde-datalab"
    # Load all tables from raw data
    tables = {}
    tables_to_download = ['stores', 'items', 'transactions', 'cities', 'holidays_events']
    if sample:
        tables_to_download.append('sample_train')
        tables_to_download.append('sample_test')
    else:
        tables_to_download.append('last_year_train')
        tables_to_download.append('test')

    for t in tables_to_download:
        key = "raw/{table}.csv".format(table=t)
        print("Loading data from {}".format(key))

        s3client = boto3.client('s3')
        csv_string = s3client.get_object(Bucket=s3bucket, Key=key)['Body'].read().decode('utf-8')
        tables[t] = pd.read_csv(StringIO(csv_string))
    return tables


def left_outer_join(left_table, right_table, on):
    new_table = left_table.merge(right_table, how='left', on=on)
    return new_table


def filter_for_latest_year(train):
    train['date'] = pd.to_datetime(train['date'])
    latest_date = train['date'].max()
    year_offset = latest_date - pd.DateOffset(days=365)
    print("Filtering for dates after {}".format(year_offset))
    return train[train['date'] > year_offset]


def join_tables_to_train_data(tables, sample):
    filename = 'bigTable'
    if sample:
        table = 'sample_train'
    else:
        table = 'last_year_train'

    filename += '2016-2017'
    filename += '.hdf'
    bigTable = add_tables(table, tables)
    return bigTable, filename


def add_days_off(bigTable, tables):
    holidays = tables['holidays_events']
    holidays['date'] = pd.to_datetime(holidays['date'], format="%Y-%m-%d")

    # Isolating events that do not correspond to holidays
    # TODO use events? events=holidays.loc[holidays.type=='Event']
    holidays = holidays.loc[holidays.type != 'Event']

    # Creating a categorical variable showing weekends
    bigTable['dayoff'] = [x in [5, 6] for x in bigTable.dayofweek]

    # TODO ignore transferred holidays

    # Adjusting this variable to show all holidays
    for (d, t, l, n) in zip(holidays.date, holidays.type, holidays.locale, holidays.locale_name):
        if t != 'Work Day':
            if l == 'National':
                bigTable.loc[bigTable.date == d, 'dayoff'] = True
            elif l == 'Regional':
                bigTable.loc[(bigTable.date == d) & (bigTable.state == n), 'dayoff'] = True
            else:
                bigTable.loc[(bigTable.date == d) & (bigTable.city == n), 'dayoff'] = True
        else:
            bigTable.loc[(bigTable.date == d), 'dayoff'] = False
    return bigTable


def join_tables_to_test_data(tables, sample):
    if sample:
        table = 'sample_test'
    else:
        table = 'test'
    bigTable = add_tables(table, tables)
    filename = 'bigTestTable.hdf'
    return bigTable, filename


def add_date_columns(df):
    print("Converting date columns into year, month, day, day of week, and days from last datapoint")
    df['date'] = pd.to_datetime(df['date'], format="%Y-%m-%d")
    maxdate = df.date.max()

    df['year'] = df.date.dt.year
    df['month'] = df.date.dt.month
    df['day'] = df.date.dt.day
    df['dayofweek'] = df.date.dt.dayofweek
    df['days_til_end_of_data'] = (maxdate - df.date).dt.days

    return df


def add_tables(base_table, tables):
    print("Joining {}.csv and items.csv".format(base_table))
    bigTable = left_outer_join(tables[base_table], tables['items'], 'item_nbr')

    print("Joining stores.csv to bigTable")
    bigTable = left_outer_join(bigTable, tables['stores'], 'store_nbr')

    print("Joining transactions.csv to bigTable")
    bigTable = left_outer_join(bigTable, tables['transactions'], ['store_nbr', 'date'])

    print("Joining cities.csv to bigTable")
    bigTable = left_outer_join(bigTable, tables['cities'], 'city')

    print("Adding date columns")
    bigTable = add_date_columns(bigTable)

    print("Adding days off")
    bigTable = add_days_off(bigTable, tables)

    # ### Can't drop date yet, because splitter.py needs it
    # print("Dropping datetime column")
    # bigTable = bigTable.drop('date', axis=1)
    return bigTable


def write_data_to_s3(table, filename, timestamp, sample=False):
    s3resource = boto3.resource('s3')
    s3client = boto3.client('s3')
    s3bucket = "twde-datalab"
    print("Putting timestamp as latest file: {}".format(timestamp))
    s3client.put_object(Body=timestamp, Bucket=s3bucket, Key='merger/latest')

    key = "merger/{timestamp}".format(timestamp=timestamp)
    print("Writing to s3://{}/{}/{}".format(s3bucket, key, filename))

    table.to_hdf(filename, 'key_to_store', mode='w')
    s3resource.Bucket(s3bucket).upload_file(filename, '{key}/{filename}'.format(key=key, filename=filename))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--sample", help="Use sample data? true | false", type=str)

    sample = False
    args = parser.parse_args()
    if args.sample == 'true':
        sample = True

    timestamp = datetime.datetime.now().isoformat()
    tables = load_data(sample)

    print("Joining data to train.csv to make bigTable")
    bigTable, filename = join_tables_to_train_data(tables, sample)
    write_data_to_s3(bigTable, filename, timestamp, sample)

    print("Joining data to test.csv to make bigTable")
    bigTestTable, filename = join_tables_to_test_data(tables, sample)
    write_data_to_s3(bigTable, filename, timestamp, sample)
