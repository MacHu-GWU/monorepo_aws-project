# -*- coding: utf-8 -*-

from simple_lambda.vendor.aws_ops_alpha.runtime import runtime


class Runtime:
    def test(self):
        _ = runtime.is_aws_codebuild
        _ = runtime.is_github_action
        _ = runtime.is_gitlab_ci
        _ = runtime.is_bitbucket_pipeline
        _ = runtime.is_circleci
        _ = runtime.is_jenkins
        _ = runtime.is_ci
        _ = runtime.is_aws_lambda
        _ = runtime.is_aws_batch
        _ = runtime.is_aws_glue
        _ = runtime.is_aws_cloud9
        _ = runtime.is_aws_ec2
        _ = runtime.is_aws_ecs
        _ = runtime.is_local
        _ = runtime.current_runtime

        # none or only one of CI environment could be TRUE
        assert (
            sum(
                [
                    runtime.is_github_action,
                    runtime.is_gitlab_ci,
                    runtime.is_bitbucket_pipeline,
                    runtime.is_circleci,
                    runtime.is_jenkins,
                ]
            )
            <= 1
        )

        # either local, either ci
        assert (
            sum(
                [
                    runtime.is_local,
                    runtime.is_ci,
                ]
            )
            == 1
        )


if __name__ == "__main__":
    from simple_lambda.tests import run_cov_test

    run_cov_test(__file__, "simple_lambda.vendor.aws_ops_alpha.runtime", preview=False)
