# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

"""Module containing configurations."""

import dataclasses
import itertools
import logging
import platform
from enum import Enum
from pathlib import Path
from typing import Literal

from github_runner_image_builder.errors import UnsupportedArchitectureError


class Arch(str, Enum):
    """Supported system architectures.

    Attributes:
        ARM64: Represents an ARM64 system architecture.
        X64: Represents an X64/AMD64 system architecture.
    """

    ARM64 = "arm64"
    X64 = "x64"

    def to_openstack(self) -> str:
        """Convert the architecture to OpenStack compatible arch string.

        Returns:
            The architecture string.
        """  # noqa: DCO050 the ValueError is an unreachable code.
        match self:
            case Arch.ARM64:
                return "aarch64"
            case Arch.X64:
                return "x86_64"
        raise ValueError  # pragma: nocover


ARCHITECTURES_ARM64 = {"aarch64", "arm64"}
ARCHITECTURES_X86 = {"x86_64"}


def get_supported_arch() -> Arch:
    """Get current machine architecture.

    Raises:
        UnsupportedArchitectureError: if the current architecture is unsupported.

    Returns:
        Arch: Current machine architecture.
    """
    arch = platform.machine()
    match arch:
        case arch if arch in ARCHITECTURES_ARM64:
            return Arch.ARM64
        case arch if arch in ARCHITECTURES_X86:
            return Arch.X64
        case _:
            raise UnsupportedArchitectureError()


class BaseImage(str, Enum):
    """The ubuntu OS base image to build and deploy runners on.

    Attributes:
        JAMMY: The jammy ubuntu LTS image.
        NOBLE: The noble ubuntu LTS image.
    """

    JAMMY = "jammy"
    NOBLE = "noble"

    @classmethod
    def get_version(cls, base: "BaseImage") -> Literal["22.04", "24.04"]:
        """Change the codename to version tag.

        Args:
            base: The base image to get the version number for.

        Return:
            The release version of the current base image.
        """
        match base:
            case BaseImage.JAMMY:
                return "22.04"
            case BaseImage.NOBLE:
                return "24.04"

    @classmethod
    def from_str(cls, tag_or_name: str) -> "BaseImage":
        """Retrieve the base image tag from input.

        Args:
            tag_or_name: The base image string option.

        Returns:
            The base image configuration of the app.
        """
        if tag_or_name in LTS_IMAGE_VERSION_TAG_MAP:
            return cls(LTS_IMAGE_VERSION_TAG_MAP[tag_or_name])
        return cls(tag_or_name)


LTS_IMAGE_VERSION_TAG_MAP = {"22.04": BaseImage.JAMMY.value, "24.04": BaseImage.NOBLE.value}
BASE_CHOICES = tuple(
    itertools.chain.from_iterable((tag, name) for (tag, name) in LTS_IMAGE_VERSION_TAG_MAP.items())
)
IMAGE_OUTPUT_PATH = Path("compressed.img")

IMAGE_DEFAULT_APT_PACKAGES = [
    "build-essential",
    "docker.io",
    "gh",
    "jq",
    "npm",
    "python3-dev",
    "python3-pip",
    "python-is-python3",
    "shellcheck",
    "tar",
    "time",
    "unzip",
    "wget",
]

_LOG_LEVELS = (logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR)
LOG_LEVELS = tuple(
    str(level)
    for level in itertools.chain(
        _LOG_LEVELS,
        (logging.getLevelName(level) for level in _LOG_LEVELS),
        (logging.getLevelName(level).lower() for level in _LOG_LEVELS),
    )
)


@dataclasses.dataclass
class Snap:
    """The snap to install.

    Attributes:
        name: The snap to install.
        channel: The snap channel to install from.
        classic: Whether the snap should be installed in --classic mode.
    """

    name: str
    channel: str
    classic: bool

    @classmethod
    def from_str(cls, value: str) -> "Snap":
        """Parse snap datastruct from string.

        Args:
            value: The string value to parse.

        Raises:
            ValueError: if there was an error parsing the snap configuration from input string.

        Returns:
            The parsed snap dataclass.
        """
        values = value.split(":")
        if len(values) < 2:
            raise ValueError("The snap should be in <name>:<channel>:<classic>")
        if len(values) == 2:
            return cls(
                name=values[0],
                channel=values[1],
                classic=False,
            )
        return cls(
            name=values[0],
            channel=values[1],
            classic=values[2].lower() == "true",
        )

    def to_string(self) -> str:
        """Format to cloud-init installable string.

        Returns:
            The <name>:<channel>:<classic> formatted string for cloud-init script.
        """
        return f"{self.name}:{self.channel}:{str(self.classic).lower()}"


@dataclasses.dataclass
class ImageConfig:
    """The build image configuration values.

    Attributes:
        arch: The architecture of the target image.
        base: The ubuntu base OS of the image.
        runner_version: The GitHub runner version to install on the VM. Defaults to latest.
        name: The image name to upload on OpenStack.
        snaps: list of snaps to install.
    """

    arch: Arch
    base: BaseImage
    runner_version: str
    name: str
    snaps: list[Snap]
