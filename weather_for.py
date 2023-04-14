import os
import sys
import requests
import json
import pandas as pd
from datetime import datetime, date, timedelta, timezone
import boto3
import csv


def lambda_handler(event, context):
    api_key = 'api_here'
    url = 'https://api.openweathermap.org/data/2.5/onecall/timemachine'
    yesterday = datetime.now() - timedelta(days=1)
    timestamp = round(datetime.timestamp(yesterday))
    params = {
        'lat': '53.349805',
        'lon': '-6.26031',
        'units': 'metric',
        'dt': timestamp,
        'appid': api_key
    }
    # Fetch hourly weather data in Dublin from OpenWeatherMap API
    input_file = requests.get(url=url, params=params)
    result_json = input_file.json()
    # Flatten and clean hourly weather data
    weather_data = pd.json_normalize(data=result_json['hourly'], record_path='weather',
                                    meta=['dt', 'temp', 'feels_like', 'clouds'])
    weather_data = weather_data.drop(['main', 'description', 'icon', 'temp', 'clouds'], 1)
    weather_data['dt'] = weather_data['dt'].apply(lambda x: datetime.fromtimestamp(x))
    date = weather_data['dt'][0].strftime("%m-%d-%Y")
    weather_data['dt'] = weather_data['dt'].apply(lambda x: x.strftime("%m/%d/%Y %H:%M:%S"))
    weather_data = weather_data.drop(weather_data.index[21:])
    weather_data = weather_data.drop(weather_data.index[:6])
    csv_data = weather_data.to_csv(index=False)

    #call your s3 bucket
    s3 = boto3.resource('s3')
    bucket = s3.Bucket('your_bucket_name_here')
    key = '{}.csv'.format(date)

    with open("/tmp/{}.csv".format(date), 'w') as f:
        csv_writer = csv.writer(f, delimiter=",")
        csv_reader = csv.reader(csv_data.splitlines())
        # Iterate over each row in the csv using reader object
        for row in csv_reader:
            # row variable is a list that represents a row in csv
            csv_writer.writerow(row)
    #upload the data into s3
    bucket.upload_file("/tmp/{}.csv".format(date), key)
