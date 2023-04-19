import requests
import pandas as pd
from datetime import date
import boto3
from io import StringIO


def lambda_handler():
    api_key = 'openweather api'
    url = f'https://api.openweathermap.org/data/2.5/weather?q=London&appid={api_key}'
    date_now = date.today()
    input_file = requests.get(url=url)
    result_json = input_file.json()

    weather_data = pd.json_normalize(data=result_json['weather'])
    df = pd.DataFrame.from_dict(pd.json_normalize(data=result_json), orient='columns')
    df = df.drop(['weather'],1)
    result = pd.concat([weather_data, df], axis=1, join="inner")
    result = result.drop(['id', 'icon', 'cod', 'base', 'sys.country', 'sys.id', 'sys.type'],1)
    result['dt'] = pd.to_datetime(result['dt'], unit='s')
    result['sys.sunrise'] = pd.to_datetime(result['sys.sunrise'], unit='s')
    result['sys.sunset'] = pd.to_datetime(result['sys.sunset'], unit='s')
    result['dt'] = result['dt'].apply(lambda x: x.strftime("%d/%m/%Y %H:%M:%S"))
    result['sys.sunrise'] = result['sys.sunrise'].apply(lambda x: x.strftime("%d/%m/%Y %H:%M:%S"))
    result['sys.sunset'] = result['sys.sunset'].apply(lambda x: x.strftime("%d/%m/%Y %H:%M:%S"))
    print(result.info())
    print(result)
    csv_buffer = StringIO()
    result.to_csv(csv_buffer, index=False)

    #call your s3 bucket
    s3 = boto3.client('s3', aws_access_key_id='key here', aws_secret_access_key='secret key here')
    bucket = 'bucket name'
    key = f'{date_now}.csv'

    s3.put_object(Bucket=bucket, Key=key, Body=csv_buffer.getvalue())


if __name__ == "__main__":
    lambda_handler()
