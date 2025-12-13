from storages.backends.s3boto3 import S3Boto3Storage

# Storage for Static Assets (CSS, JS, Fonts)
class StaticStorage(S3Boto3Storage):
    # Files will be stored under the 'static/' prefix in the S3 bucket
    location = 'static'
    default_acl = 'public-read'

# Storage for User-Uploaded Media (QR codes, backups)
class MediaStorage(S3Boto3Storage):
    # Files will be stored under the 'media/' prefix in the S3 bucket
    location = 'media'
    default_acl = 'private' # Important: Media should generally be private
    file_overwrite = False