# ECR Gallery https://gallery.ecr.aws/lambda/python
# There's no such "slim" Lambda Python base image
# Note that the base image on ECR gallery is around 180MB, this is the compressed size
# If you pull it from ECR, it will be around 650MB on your local machine.
# If you push it back to your own ECR, it will be around 180MB again.
FROM public.ecr.aws/lambda/python:3.9

# We need these two environment variables to run unit test
# you can always override it in Batch job definition or in submit job API
ARG USER_ENV_NAME=""
ARG PARAMETER_NAME=""

# if "run unit test" is part of the docker build process, we may need to give
# the container AWS credential. these env vars are only required in stage 1
# we will not include them in stage 2
ARG AWS_REGION=""
ARG AWS_ACCESS_KEY_ID=""
ARG AWS_SECRET_ACCESS_KEY=""
ARG AWS_SESSION_TOKEN=""

# !! don't leave it uncommented in CI, this is for local debug, use it with caution
RUN env

# copy the following file to working directory
# these file are not changing frequently, so it should go to the top of Dockerfile as a layer cache
# the ${LAMBDA_TASK_ROOT} is the path where the runtime searches dependencies first
# see https://docs.aws.amazon.com/lambda/latest/dg/python-image.html
COPY pyproject.toml \
    requirements.txt \
    requirements-dev.txt \
    requirements-test.txt \
    ${LAMBDA_TASK_ROOT}

# install virtualenv, then create virtualenv, install main and test dependencies
# since we are using Poetry to resolve the deterministic dependency,
# this layer is not chaging frequently as before
RUN pip install --quiet --no-cache-dir -r requirements.txt

# copy the source code to the working directory
# this folder is chaging frequently, so we put it at the bottom of Dockerfile
# to utilize the build cache
COPY simple_lbd_container/ ${LAMBDA_TASK_ROOT}/simple_lbd_container
COPY lambda_app/lambda_function.py ${LAMBDA_TASK_ROOT}

# install the source package itself
RUN pip install --quiet -e ${LAMBDA_TASK_ROOT}

# setup COMMAND to the test handler, we will override this when deploying using CDK
CMD [ "lambda_function.handler" ]

# what's next
# build this image locally using docker build
#   make build-image
# run lambda container locally for testing
#   python debug/run_container_local_test_step1_initialize_container.py
# run test by picking lambda function handler and custom event
#   python debug/run_container_local_test_step2_run_test.py
# stop the local lambda container
#   python debug/run_container_local_test_step3_stop_container.py
