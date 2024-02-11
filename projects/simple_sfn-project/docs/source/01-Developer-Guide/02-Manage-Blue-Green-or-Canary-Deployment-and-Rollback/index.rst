Manage Blue / Green, Canary Deployment and Rollback
==============================================================================


Lambda Function Versioning and Alias
------------------------------------------------------------------------------
`Lambda function versioning and alias <https://docs.aws.amazon.com/lambda/latest/dg/configuration-aliases.html>`_ is a powerful feature that allows creating immutable versions of Lambda function deployments. An alias serves as a pointer to a single version of the deployment or can even distribute traffic between two versions. With this feature, switching traffic to a historical version doesn't require redeployment; instead, you simply update the Alias to point to the desired historical version. For canary deployments, updating the routing percentage configuration is all that's needed. This core technique enables blue/green deployments, canary deployments, and rollbacks.


Manage Versioning and Alias in CI/CD
------------------------------------------------------------------------------
To understand how we manage versioned deployment in the code, let's review the following files:

1. ``config/config.json``: This file contains non-sensitive project configuration for each environment. The line ``"*.lambda_functions.*.live_version": null`` indicates that we do not explicitly set a version for the ``LIVE`` alias. By default, the ``LIVE`` alias points to the ``LATEST`` version.

.. literalinclude:: ../../../../config/config.json
   :language: javascript
   :emphasize-lines: 13
   :linenos:

2. ``simple_sfn/iac/define/lbd.py``: This is the CDK stack code where we declare the ``LIVE`` alias and use the value defined in ``"*.lambda_functions.*.live_version"`` as the target version.

.. literalinclude:: ../../../../simple_sfn/iac/define/lbd.py
   :language: python
   :emphasize-lines: 70-79
   :linenos:

3. ``bin/automation/deploy.py``: This section of the CI automation script contains the ``publish_lambda_version()`` function, which publishes a new version from the ``LATEST`` Lambda functions. This function is called only after a successful deployment in the production environment.

.. literalinclude:: ../../../../bin/automation/deploy.py
   :language: python
   :emphasize-lines: 40-62
   :linenos:

With this setup, we always use the ``LATEST`` version in the ``sbx`` and ``tst`` environments for development and testing. For each successful deployment to production, we create an immutable version. To change the target version, update the ``config.json`` file and rerun the CodePipeline. This process does not involve a full deployment; Instead, it just updates the alias and points to the desired version.
