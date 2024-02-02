About the ``cookiecutter`` Folder
==============================================================================


Overview
------------------------------------------------------------------------------
The automation scripts in this folder are designed to assist you in creating a new project using a seed project as a template. For example, if you wish to create a new AWS Lambda project based on the `simple_lambda-project <../projects/simple_lambda-project>`_, you can simply run ``python new_project_like_simple_lambda.py`` (Python can be any Python interpreter; the automation script will automatically create a new virtual environment and install the required dependencies). It will prompt you for some information and then create a new project in the ``tmp`` folder.


Seeding a Project
------------------------------------------------------------------------------
To add the capability to create a new project from a specific project template, you need to register it as a seed project. Here are the steps to follow:

1. Create a new Python module ``more_project_like_this/seeds/${project_name}.py`` in the `more_project_like_this/seeds <./more_project_like_this/seeds>`_ folder, and define the template string mapping accordingly. Ensure that the ``project_name`` aligns with the Python module file name.
2. Create a new ``new_project_like_${project_name}.py`` file, similar to `new_project_like_simple_lambda.py <./new_project_like_simple_lambda.py>`_, and modify its content as needed.

With these steps completed, developers can use the ``new_project_like_${project_name}.py`` script to create a new project based on the selected seed project.
