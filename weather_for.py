import requests
import pandas as pd
from datetime import date
import boto3
from io import StringIO
import json


def lambda_handler():
    api_key = 'open weather api'
    url = f'https://api.openweathermap.org/data/2.5/weather?q=London&appid={api_key}'
    date_now = date.today()
    input_file = requests.get(url=url)
    result_json = input_file.json()
    
    weather_data = pd.json_normalize(data=result_json['weather'])
    df = pd.DataFrame.from_dict(pd.json_normalize(data=result_json), orient='columns')
    df = df.drop(['weather'],axis=1)
    result = pd.concat([weather_data, df], axis=1, join="inner")
    result = result.drop(['id', 'icon', 'cod', 'base', 'sys.country', 'sys.id', 'sys.type'],axis=1)
    result['dt'] = pd.to_datetime(result['dt'], unit='s')
    result['sys.sunrise'] = pd.to_datetime(result['sys.sunrise'], unit='s')
    result['sys.sunset'] = pd.to_datetime(result['sys.sunset'], unit='s')
    result['dt'] = result['dt'].apply(lambda x: x.strftime("%d/%m/%Y %H:%M:%S"))
    result['sys.sunrise'] = result['sys.sunrise'].apply(lambda x: x.strftime("%d/%m/%Y %H:%M:%S"))
    result['sys.sunset'] = result['sys.sunset'].apply(lambda x: x.strftime("%d/%m/%Y %H:%M:%S"))

    desc = result['description'].iloc[0]
    temp = result['main.temp'].apply(lambda x: x - 273.15).round(2).iloc[0]
    temp_now = result['main.feels_like'].apply(lambda x: x - 273.15).round(2).iloc[0]
    temp_min = result['main.temp_min'].apply(lambda x: x - 273.15).round(2).iloc[0]
    temp_max = result['main.temp_max'].apply(lambda x: x - 273.15).round(2).iloc[0]

    weather_summary = f'Weather: {desc}\nTemperature: {temp} C\nFeels Like: {temp_now} C\nMin Temp: {temp_min} C\nMax Temp: {temp_max} C'
    print(weather_summary)
    csv_buffer = StringIO()
    result.to_csv(csv_buffer, index=False)


    #call your s3 bucket
    s3 = boto3.client('s3', aws_access_key_id='key here', aws_secret_access_key='secret key here')
    bucket = 'bucket name'
    key = f'{date_now}.csv'

    s3.put_object(Bucket=bucket, Key=key, Body=csv_buffer.getvalue())
    
    print('csv upload worked!!!')
    
    # call sns service and send sms to subscribed numbers using topic
    client = boto3.client('sns')
    response = client.publish (
      TargetArn = "Topic ARN here",
      Message = json.dumps({'default': weather_summary}),
      MessageStructure = 'json'
    )
    print('SMS sent')
    
    return {
      'statusCode': 200,
      'body': json.dumps(response)
    }

lambda_handler()