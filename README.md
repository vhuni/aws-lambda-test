# Testing AWS Lambda, Cloudwatch and SNS Services using Python code to fetch weather data for London and upload it to an S3 bucket while notifying subscribers via SNS.

 This code fetches the weather data for London from the OpenWeather API and formats the data into a Pandas DataFrame. The formatted data is then uploaded to an S3 bucket and sent via SNS.

## Prerequisites
- A valid OpenWeather API key.
- A configured AWS S3 bucket.
- Python 3.x.
- Required libraries: Pandas, Boto3, Requests, and StringIO.


## Function
The lambda_handler() function is the main function that performs the following tasks:

- Fetches the weather data for London from the OpenWeather API.
- Formats the data into a Pandas DataFrame.
- Uploads the formatted data to an S3 bucket.
- Sends SNS notification of the weather.

## S3 bucket code

```python
    # Setting up boto3 to connect to S3 Bucket
    s3 = boto3.client('s3', aws_access_key_id='key here', aws_secret_access_key='secret key here')
    bucket = 'bucket name'
    key = f'{date_now}.csv'

    # Upload object to S3
    s3.put_object(Bucket=bucket, Key=key, Body=csv_buffer.getvalue())
```

## SNS Notification Code

```python
    # Setting up boto3 to connect to AWS SNS service
    client = boto3.client('sns')
    response = client.publish (
      TargetArn = "Topic ARN here",
      Message = json.dumps({'default': weather_summary}),
      MessageStructure = 'json'
    )
    # Format return response
    return {
      'statusCode': 200,
      'body': json.dumps(response)
    }

```
