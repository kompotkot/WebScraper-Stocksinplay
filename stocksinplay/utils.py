import json
from collections import OrderedDict

import gspread
from oauth2client.service_account import ServiceAccountCredentials


output_dir = 'output'


# Read parsed data from spider briefing_earnings and return tickets
def get_tickets_list():
    tickers = []

    with open(f'{output_dir}/briefing_parsed.json') as f:
        data = OrderedDict(json.load(f))
        days = data.keys()
        for day in days:
            for ticker in data[day]:
                tickers.append(ticker)

    return tickers


# Correct json file for finviz_screener spider
def correct_json():
    clear_dct = {}

    with open(f'{output_dir}/finviz_parsed.json') as f:
        for line in f:
            clear_line = json.loads(line)
            clear_dct[clear_line['ticker']] = {'name': clear_line['name'], 'sector': clear_line['sector'],
                                               'price': clear_line['price']}
    with open(f'{output_dir}/finviz_parsed.json', 'w') as f:
        json.dump(clear_dct, f)


# Create final final_parsed.json file with filtered data
def process_final(googlewrite=False):
    final_out = OrderedDict()

    with open(f'{output_dir}/briefing_parsed.json') as f:
        br_out = OrderedDict(json.load(f))

        with open(f'{output_dir}/finviz_parsed.json') as j:
            fn_out = json.load(j)
            for day in br_out:
                for ticker in br_out[day].keys():
                    if ticker in fn_out:
                        final_out[ticker] = {
                            'day': day,
                            'name': fn_out[ticker]['name'],
                            'sector': fn_out[ticker]['sector'],
                            'current_price': fn_out[ticker]['price'],
                            'surprise_value': br_out[day][ticker]['surprise_value'],
                            'actual_value': br_out[day][ticker]['actual_value'],
                            'consensus_value': br_out[day][ticker]['consensus_value']}

    if googlewrite:
        google_sheet_writer(final_out)

    with open(f'{output_dir}/final_parsed.json', 'w') as f:
        json.dump(final_out, f)


# Write data to google sheet document via API
def google_sheet_writer(data):
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
             "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope)
    client = gspread.authorize(creds)
    sheet = client.open('StocksInPlay').sheet1

    sheet.clear()
    rows = []

    for ticker in data:
        for i in data[ticker]:              # Process None values for float converting
            if data[ticker][i] is None:
                data[ticker][i] = 0

        row = [data[ticker]['day'], ticker, float(data[ticker]['current_price']), data[ticker]['name'],
               data[ticker]['sector'], float(data[ticker]['surprise_value']),
               float(data[ticker]['actual_value']), float(data[ticker]['consensus_value'])]

        rows.append(row)

    sheet.insert_rows(rows)
