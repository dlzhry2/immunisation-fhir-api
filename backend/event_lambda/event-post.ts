import { DynamoDB } from 'aws-sdk';


const dynamoDB = new DynamoDB.DocumentClient();

export const handler = async (event: any): Promise<any> => {

  const operation = event.httpMethod;
  const dynamoDBTableName = process.env.DYNAMODB_TABLE_NAME || 'DefaultTableName';

  if (event.path === '/_status' && operation === 'GET') {
    const statusResponse = {
      status: 'healthy',
      message: 'Backend is up and running.',
    };
    return {
      statusCode: 200,
      body: JSON.stringify(statusResponse),
    };
  } else if (operation === 'POST' && event.path === '/event') {
    const params = {
      TableName: dynamoDBTableName,
      Item: JSON.parse(event.body),
    };
    try {
      await dynamoDB.put(params).promise();
      return {
        statusCode: 201,
        body: JSON.stringify('Item created successfully.'),
      };
    } catch (error) {
      console.error('Error:', error); // Log the error
      return {
        statusCode: 500,
        body: JSON.stringify('Error creating the item.'),
      };
    };
  };
  return {
    statusCode: 400,
    body: JSON.stringify('Invalid operation.'),
  };
};
