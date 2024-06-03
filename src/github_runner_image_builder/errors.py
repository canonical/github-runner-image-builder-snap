# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

"""Module containing error definitions."""


class ImageBuilderBaseError(Exception):
    """Represents an error with any builder related executions."""


class BuilderSetupError(ImageBuilderBaseError):
    """Represents an error while setting up host machine as builder."""


# nosec: B603: All subprocess runs are run with trusted executables.
class DependencyInstallError(BuilderSetupError):
    """Represents an error while installing required dependencies."""


class NetworkBlockDeviceError(BuilderSetupError):
    """Represents an error while enabling network block device."""


class UnsupportedArchitectureError(ImageBuilderBaseError):
    """Raised when given machine architecture is unsupported."""


class CleanBuildStateError(ImageBuilderBaseError):
    """Represents an error cleaning up build state."""


class BaseImageDownloadError(ImageBuilderBaseError):
    """Represents an error downloading base image."""


class ImageResizeError(ImageBuilderBaseError):
    """Represents an error while resizing the image."""


class ImageMountError(ImageBuilderBaseError):
    """Represents an error while mounting the image to network block device."""


class ResizePartitionError(ImageBuilderBaseError):
    """Represents an error while resizing network block device partitions."""


class UnattendedUpgradeDisableError(ImageBuilderBaseError):
    """Represents an error while disabling unattended-upgrade related services."""


class SystemUserConfigurationError(ImageBuilderBaseError):
    """Represents an error while adding user to chroot env."""


class PermissionConfigurationError(ImageBuilderBaseError):
    """Represents an error while modifying dir permissions."""


class YQBuildError(ImageBuilderBaseError):
    """Represents an error while building yq binary from source."""


class YarnInstallError(ImageBuilderBaseError):
    """Represents an error installilng Yarn."""


class ImageCompressError(ImageBuilderBaseError):
    """Represents an error while compressing cloud-img."""


class BuildImageError(ImageBuilderBaseError):
    """Represents an error while building the image."""


class OpenstackBaseError(Exception):
    """Represents an error while interacting with Openstack."""


class UnauthorizedError(OpenstackBaseError):
    """Represents an unauthorized connection to Openstack."""


class UploadImageError(OpenstackBaseError):
    """Represents an error when uploading image to Openstack."""


class OpenstackError(OpenstackBaseError):
    """Represents an error while communicating with Openstack."""
