Welcome to ``dynamodbsnaplake`` Documentation
==============================================================================
The DynamoDB Snapshot Data Lake SAAS Product Source Code.

Use this `CloudFormation Template <https://us-east-1.console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/create?stackName=dynamodbsnaplake&templateURL=https://bmt-app-dev-us-east-1-doc-host.s3.us-east-1.amazonaws.com/projects/tmp/cfn.json>`_ to deploy this solution.

Then you can just use:

.. code-block:: python

    import json
    import boto3

    sfn_client = boto3.client('stepfunctions')
    sfn_client.start_execution(
        stateMachineArn='arn:aws:states:us-east-1:123456789012:stateMachine:dynamodb_to_datalake',
        input=json.dumps({
            "table_arn": "arn:aws:dynamodb:us-east-1:123456789012:table/MyTable",
            "export_time": "2024-08-13T04:00:00Z"
        })
    )