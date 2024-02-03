# -*- coding: utf-8 -*-

help: ## ** Show this help message
	@perl -nle'print $& if m{^[a-zA-Z_-]+:.*?## .*$$}' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-40s\033[0m %s\n", $$1, $$2}'


info: ## ** Show Project Information
	./.venv/bin/python ./bin/s00_show_project_info.py


venv-create: ## ** Create Virtual Environment
	python ./bin/s01_01_venv_create.py


venv-remove: ## ** Remove Virtual Environment
	python ./bin/s01_02_venv_remove.py


install: ## ** Install main dependencies and Package itself
	python ./bin/s02_01_pip_install.py


install-dev: ## Install Development Dependencies
	python ./bin/s02_02_pip_install_dev.py


install-test: ## Install Test Dependencies
	python ./bin/s02_03_pip_install_test.py


install-doc: ## Install Document Dependencies
	python ./bin/s02_04_pip_install_doc.py


install-automation: ## Install Dependencies for Automation Script
	python ./bin/s02_05_pip_install_automation.py


install-all: ## Install All Dependencies
	python ./bin/s02_06_pip_install_all.py


poetry-export: ## Export requirements-*.txt from poetry.lock file
	python ./bin/s02_07_poetry_export.py


poetry-lock: ## Resolve dependencies using poetry, update poetry.lock file
	python ./bin/s02_08_poetry_lock.py


show-context-info: ## Show Runtime, Environment and Git info
	python ./bin/s02_09_show_context_info.py


test: install install-test test-only ## ** Run test


test-only: ## Run test without checking test dependencies
	./.venv/bin/python ./bin/s03_01_run_unit_test.py


cov: install install-test cov-only ## ** Run code coverage test


cov-only: ## Run code coverage test without checking test dependencies
	./.venv/bin/python ./bin/s03_02_run_cov_test.py


view-cov: ## View code coverage test result in web browser
	./.venv/bin/python ./bin/s03_03_view_cov.py


int: install install-test int-only ## ** Run integration test


int-only: ## Run integration test without checking test dependencies
	./.venv/bin/python ./bin/s03_04_run_int_test.py


build-doc: install install-doc build-doc-only ## Build documentation website locally


build-doc-only: ## Build documentation website locally without checking doc dependencies
	./.venv/bin/python ./bin/s03_11_build_doc.py


view-doc: ## View documentation website locally
	./.venv/bin/python ./bin/s03_12_view_doc.py


deploy-versioned-doc: ## Deploy Documentation Site To S3 as Versioned Doc
	./.venv/bin/python ./bin/s03_13_deploy_versioned_doc.py


deploy-latest-doc: ## Deploy Documentation Site To S3 as Latest Doc
	./.venv/bin/python ./bin/s03_14_deploy_latest_doc.py


view-latest-doc: ## View latest documentation website on S3
	./.venv/bin/python ./bin/s03_15_view_latest_doc.py


build-source: ## Build Lambda source artifacts
	./.venv/bin/python ./bin/s04_03_lambda_build_source.py


deploy-config: ## Deploy versioned config data to parameter store backend.
	./.venv/bin/python ./bin/s04_01_deploy_config.py


delete-config: ## Delete config data from parameter store backend.
	./.venv/bin/python ./bin/s04_02_delete_config.py


deploy-app: ## Deploy Lambda app via CDK deploy
	./.venv/bin/python ./bin/s04_05_deploy_app.py


delete-app: ## Delete Lambda app via CDK destroy
	./.venv/bin/python ./bin/s04_06_delete_app.py


bump-patch: ## Bump patch version
	./.venv/bin/python ./bin/cli bump_version --patch


bump-minor: ## Bump minor version
	./.venv/bin/python ./bin/cli bump_version --minor


bump-major: ## Bump major version
	./.venv/bin/python ./bin/cli bump_version --major
