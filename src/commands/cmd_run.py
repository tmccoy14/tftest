"""Standard library"""
import os

"""Third party modules"""
import click

"""Internal application modules"""
from src.main import pass_environment
from src.lib import (
    check_tf_extension,
    tf_init,
    tf_apply,
    tf_destroy,
)
from src.lib.subprocess import Command


@click.command("run", short_help="Run the tests.")
@click.option(
    "--path", "-p", required=True, help="Path to Terraform directory.",
)
@click.option(
    "--var", required=False, multiple=True, help="Variables for Terraform files."
)
@pass_environment
def cli(ctx, path, var):
    """Run the tests for the Terraform modules and files"""

    # Total count for successful and failed tests
    result_total = 0

    # Ensure path provided to Terraform directory exists
    tf_directory = os.path.join(path)
    if not os.path.exists(tf_directory):
        raise click.UsageError(
            "Path to Terraform directory does not exist: '%s'" % path
        )

    # Check if Terraform directory contains Terragrunt file
    tf_type = check_tf_extension(ctx, tf_directory)
    if tf_type is None:
        raise click.UsageError(
            "Terraform directory does not contain necessary files: '%s'" % path
        )

    # Setup command subprocess
    if tf_type == "hcl":
        tf_command = Command("terragrunt")
    else:
        tf_command = Command("terraform")

    # Run terraform init command to initialize a working directory
    init_result = tf_init(ctx, tf_command, tf_directory, var)
    result_total += init_result

    # Run terraform/terragrunt apply command to apply new resources or changes
    apply_result = tf_apply(ctx, tf_command, tf_directory, var)
    result_total += apply_result

    # Run terraform/terragrunt destroy to destroy the Terraform-managed infrastructure
    destroy_result = tf_destroy(ctx, tf_command, tf_directory, var)
    result_total += destroy_result

    # Output whether the test ran were succesful or failed
    if result_total == 0:
        ctx.log("TEST SUCCESSFUL")
    else:
        ctx.log("TEST FAILED", level="error")
