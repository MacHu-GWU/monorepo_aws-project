Centralized Multi Environment Config Management
==============================================================================
POC-style projects often have numerous hardcoded values, with some constant values being used multiple times. This pattern make projects difficult to maintain and prone to errors. In contrast, a production-ready project requires a centralized location to store all configurations. Once configurations are defined, we no longer allow hard-coded values and only reference configurations.

In this project, we use the ``multi environment json`` pattern defined in `config_patterns <https://github.com/MacHu-GWU/config_patterns-project>`_ Python library to manage the configuration. Please read the ``config_patterns`` documentation to learn more about this pattern.

Below are the list of important files related to config management::

    ${python_lib_name}/config # the root folder of the config management system source code
    ${python_lib_name}/config/define # config schema definition
    ${python_lib_name}/config/define/main.py # centralized config object, config fields are break down into sub-modules
    ${python_lib_name}/config/define/app.py # app related configs, e.g. app name, app artifacts S3 bucket
    ${python_lib_name}/config/define/cloudformation.py # CloudFormation related configs
    ${python_lib_name}/config/define/deploy.py # deployment related configs
    ${python_lib_name}/config/define/lbd_deploy.py # Lambda function deployment related configs
    ${python_lib_name}/config/define/lbd_func.py # per Lambda function name, memory size, timeout configs
    ${python_lib_name}/config/define/name.py # AWS Resource name related configs
    ${python_lib_name}/config/init.py # config value initialization
    config/config.json # include the non-sensitive config data
    ${HOME}/.projects/simple_sfn/config-secret.json # include the sensitive config data, the ${HOME} is your user home directory
    tests/config/test_config_init.py # the unit test for config management, everytime you changed any of the config.json, or config/ modules, you should run this test

The ``${python_lib_name}/config`` Python module implemented the "configuration as code" pattern, let's walkthrough the folder structure to get better understanding.

- The ``define`` module defines the configuration data schema (field and value pairs).
    - To improve maintainability, we break down the long list of configuration fields into sub-modules.
    - There are two types of configuration values: constant values and derived values. Constant values are static values that are hardcoded in the ``config.json`` file, typically a string or an integer. Derived values are calculated dynamically based on one or more constant values.
- The ``init`` module defines how to read the configuration data from external storage.
    - On a developer's local laptop, the data is read from a ``config.json`` file.
    - During CI build runtime and AWS Lambda function runtime, the data is read from the AWS Parameter Store.

Below is the implementation of the ``init`` module:

.. literalinclude:: ../../../../simple_sfn/config/init.py
   :language: python
