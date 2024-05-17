# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

"""Image test module."""

import logging
from pathlib import Path
from typing import NamedTuple

import pytest
from openstack.connection import Connection
from pylxd import Client

from github_runner_image_builder.config import IMAGE_OUTPUT_PATH
from tests.integration.helpers import create_lxd_instance, create_lxd_vm_image

logger = logging.getLogger(__name__)


class Commands(NamedTuple):
    """Test commands to execute.

    Attributes:
        name: The test name.
        command: The command to execute.
    """

    name: str
    command: str


# This is matched with E2E test run of github-runner-operator charm.
TEST_RUNNER_COMMANDS = (
    Commands(name="simple hello world", command="echo hello world"),
    Commands(name="file permission to /usr/local/bin", command="ls -ld /usr/local/bin"),
    Commands(
        name="file permission to /usr/local/bin (create)", command="touch /usr/local/bin/test_file"
    ),
    Commands(name="install microk8s", command="sudo snap install microk8s --classic"),
    Commands(name="wait for microk8s", command="microk8s status --wait-ready"),
    Commands(
        name="deploy nginx in microk8s",
        command="microk8s kubectl create deployment nginx --image=nginx",
    ),
    Commands(
        name="wait for nginx",
        command="microk8s kubectl rollout status deployment/nginx --timeout=20m",
    ),
    Commands(name="update apt in docker", command="docker run python:3.10-slim apt-get update"),
    Commands(name="docker version", command="docker version"),
    Commands(name="check python3 alias", command="python --version"),
    Commands(name="pip version", command="python3 -m pip --version"),
    Commands(name="npm version", command="npm --version"),
    Commands(name="shellcheck version", command="shellcheck --version"),
    Commands(name="jq version", command="jq --version"),
    Commands(name="yq version", command="yq --version"),
    Commands(name="apt update", command="sudo apt-get update -y"),
    Commands(name="install pipx", command="sudo apt-get install -y pipx"),
    Commands(name="pipx add path", command="pipx ensurepath"),
    Commands(name="install check-jsonschema", command="pipx install check-jsonschema"),
    Commands(name="check jsonschema", command="check-jsonschema --version"),
    Commands(name="unzip version", command="unzip -v"),
    Commands(name="gh version", command="gh --version"),
    Commands(
        name="test sctp support", command="sudo apt-get install lksctp-tools -yq && checksctp"
    ),
)


@pytest.mark.asyncio
@pytest.mark.usefixtures("cli_run")
async def test_image(image: str, tmp_path: Path):
    """
    arrange: given a built output from the CLI.
    act: when the image is booted and commands are executed.
    assert: commands do not error.
    """
    lxd = Client()
    logger.info("Creating LXD VM Image.")
    create_lxd_vm_image(lxd_client=lxd, img_path=IMAGE_OUTPUT_PATH, image=image, tmp_path=tmp_path)
    logger.info("Launching LXD instance.")
    instance = await create_lxd_instance(lxd_client=lxd, image=image)

    for testcmd in TEST_RUNNER_COMMANDS:
        logger.info("Running command: %s", testcmd.command)
        # run command as ubuntu user. Passing in user argument would not be equivalent to a login
        # shell which is missing critical environment variables such as $USER and the user groups
        # are not properly loaded.
        result = instance.execute(
            ["su", "--shell", "/bin/bash", "--login", "ubuntu", "-c", testcmd.command]
        )
        logger.info("Command output: %s %s %s", result.exit_code, result.stdout, result.stderr)
        assert result.exit_code == 0


@pytest.mark.asyncio
@pytest.mark.usefixtures("cli_run")
async def test_openstack_upload(openstack_connection: Connection, openstack_image_name: str):
    """
    arrange: given a built output from the CLI.
    act: when openstack images are listed.
    assert: the built image is uploaded in Openstack.
    """
    assert len(openstack_connection.get_image(openstack_image_name))


@pytest.mark.asyncio
@pytest.mark.usefixtures("cli_run")
async def test_script_callback(callback_result_path: Path):
    """
    arrange: given a CLI run with script that creates a file.
    act: None.
    assert: the file exist.
    """
    assert callback_result_path.exists()
