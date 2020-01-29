import os
from tempfile import SpooledTemporaryFile

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from storages.backends.s3boto3 import S3Boto3Storage


class CustomS3Boto3Storage(S3Boto3Storage):
    """
    This is our custom version of S3Boto3Storage that fixes a bug in boto3 where the passed in file is closed upon upload.

    https://github.com/boto/boto3/issues/929
    https://github.com/matthewwithanm/django-imagekit/issues/391
    """

    def _save_content(self, obj, content, parameters):
        """
        We create a clone of the content file as when this is passed to boto3 it wrongly closes
        the file upon upload where as the storage backend expects it to still be open
        """
        # Seek our content back to the start
        content.seek(0, os.SEEK_SET)

        # Create a temporary file that will write to disk after a specified size
        content_autoclose = SpooledTemporaryFile()

        # Write our original content into our copy that will be closed by boto3
        content_autoclose.write(content.read())

        # Upload the object which will auto close the content_autoclose instance
        super(CustomS3Boto3Storage, self)._save_content(
            obj, content_autoclose, parameters
        )

        # Cleanup if this is fixed upstream our duplicate should always close
        if not content_autoclose.closed:
            content_autoclose.close()


class OverwriteStorage(FileSystemStorage):
    """
    Storage class to store files in filesystem with file overwrite
    """

    def get_available_name(self, name, max_length=None):
        """
        Returns a filename that's free on the target storage system, and
        available for new content to be written to.
        """
        # If the filename already exists, remove it as if it was a true file system
        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return name

    def upload_file(self, local_file_path):
        return local_file_path


class MediaStorage(CustomS3Boto3Storage):
    querystring_auth = True
    location = "media"
    default_acl = "private"

    def upload_file(self, local_file_path):
        filename = os.path.basename(local_file_path)
        with open(local_file_path, "rb") as f_in:
            self.save(filename, f_in)
        return self.url(filename)


class PublicMediaStorage(CustomS3Boto3Storage):
    default_acl = "public-read"
    file_overwrite = False

    def __init__(self, folder=""):
        CustomS3Boto3Storage.__init__(self)
        self.location = settings.AWS_PUBLIC_MEDIA_LOCATION + folder

    def upload_file(self, local_file_path):
        filename = os.path.basename(local_file_path)
        with open(local_file_path, "rb") as f_in:
            self.save(filename, f_in)
        return self.url(filename)


class PrivateMediaStorage(CustomS3Boto3Storage):
    location = settings.AWS_PRIVATE_MEDIA_LOCATION
    default_acl = "private"

    def upload_file(self, local_file_path):
        filename = os.path.basename(local_file_path)
        with open(local_file_path, "rb") as f_in:
            self.save(filename, f_in)
        return self.url(filename)


def get_storage_class():
    """
    Returns storage class instance to store files
    :return: Storage class Instance
    """
    # If running in DEBUG mode return File system storage
    if settings.DEBUG:
        # TODO: Change to OverwriteStorage
        return MediaStorage()
    else:
        # Return AWS s3 storage class instance
        return MediaStorage()


def get_public_storage_class():
    # If running in DEBUG mode return File system storage
    if settings.DEBUG:
        return OverwriteStorage()
    else:
        # Return AWS s3 storage class instance
        return PublicMediaStorage()


def get_private_storage_class():
    # If running in DEBUG mode return File system storage
    if settings.DEBUG:
        return OverwriteStorage()
    else:
        # Return AWS s3 storage class instance
        return PrivateMediaStorage()
