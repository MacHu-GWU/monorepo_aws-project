
Request

.. code-block:: python

    {
        "aws_account_id": "123456789012",
        "aws_region": "us-east-1",
        "api_key": "your_api_key",
        "product_name": "dynamodbsnaplake",
        "version": "latest",
    }

Response

.. code-block:: python


    {
        "${artifact_name}_${artifact_attribute}": "...",
    }

Example Response

.. code-block:: python

    {
        "LambdaFunctionContainerUri": "...",
        "LicenseUrl": "...",
    }

