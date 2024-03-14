import boto3
import pandas as pd
import json

s3_client = boto3.client('s3')
sns_client = boto3.client('sns')
sns_arn = 'arn:aws:sns:us-east-1:905418427684:Doordash-delivery'

def lambda_handler(event, context):
    # TODO implement
    print(event)
    try:
        bucket_name = event["Records"][0]["s3"]["bucket"]["name"]
        s3_file_key = event["Records"][0]["s3"]["object"]["key"]
        print(bucket_name)
        print(s3_file_key)
        response = s3_client.get_object(Bucket=bucket_name, Key=s3_file_key)
        json_data = json.loads(response['Body'].read().decode('utf-8'))
        df = pd.json_normalize(json_data)

        # Filter records where status is "delivered"
        filtered_df = df[df['status'] == 'delivered']

        # Specify the path for the output JSON file in S3
        output_S3_bucket='doordash-cicd-output-data'
        output_s3_key = 'DoorDashDelivered_status.json'

        # Write the filtered DataFrame to a new JSON file in S3
        s3_client.put_object(
            Bucket=output_S3_bucket,
            Key=output_s3_key,
            Body=filtered_df.to_json(orient='records'),
            ContentType='application/json'
        )


        message = "Input S3 File {} has been processed succesfuly !!".format("s3://"+bucket_name+"/"+s3_file_key)
        respone = sns_client.publish(Subject="SUCCESS - Daily Data Processing",TargetArn=sns_arn, Message=message, MessageStructure='text')
    except Exception as err:
        print(err)
        message = "Input S3 File {} processing is Failed !!".format("s3://"+bucket_name+"/"+s3_file_key)
        respone = sns_client.publish(Subject="FAILED - Daily Data Processing", TargetArn=sns_arn, Message=message, MessageStructure='text')