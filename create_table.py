import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource(
    'dynamodb',
    endpoint_url="http://localhost:8001",
    region_name="us-west-2",
    aws_access_key_id="dummy",
    aws_secret_access_key="dummy"
)

# -----------------------------
# Create Users Table
# -----------------------------
try:
    users_table = dynamodb.create_table(
        TableName='Users',
        KeySchema=[
            {'AttributeName': 'email', 'KeyType': 'HASH'}
        ],
        AttributeDefinitions=[
            {'AttributeName': 'email', 'AttributeType': 'S'}
        ],
        BillingMode='PAY_PER_REQUEST'
    )
    print("Users table created")

except ClientError as e:
    if e.response['Error']['Code'] == 'ResourceInUseException':
        print("Users table already exists")
    else:
        raise


# -----------------------------
# Create Photographers Table
# -----------------------------
try:
    photographers_table = dynamodb.create_table(
        TableName='Photographers',
        KeySchema=[
            {'AttributeName': 'id', 'KeyType': 'HASH'}
        ],
        AttributeDefinitions=[
            {'AttributeName': 'id', 'AttributeType': 'S'}
        ],
        BillingMode='PAY_PER_REQUEST'
    )
    print("Photographers table created")

except ClientError as e:
    if e.response['Error']['Code'] == 'ResourceInUseException':
        print("Photographers table already exists")
    else:
        raise


# -----------------------------
# Create PhotographerBookings Table
# -----------------------------
try:
    bookings_table = dynamodb.create_table(
        TableName='PhotographerBookings',
        KeySchema=[
            {'AttributeName': 'booking_id', 'KeyType': 'HASH'}
        ],
        AttributeDefinitions=[
            {'AttributeName': 'booking_id', 'AttributeType': 'S'}
        ],
        BillingMode='PAY_PER_REQUEST'
    )
    print("PhotographerBookings table created")

except ClientError as e:
    if e.response['Error']['Code'] == 'ResourceInUseException':
        print("PhotographerBookings table already exists")
    else:
        raise