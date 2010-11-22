from django.conf import settings

DBF_SETTINGS = {
	"DATABASE_FILES_CACHE" : getattr(settings, "DATABASE_FILES_CACHE", False),
	"DATABASE_FILES_CACHE_UNENCRYPTED" : getattr(settings, "DATABASE_FILES_CACHE_UNENCRYPTED", False),
	"DATABASE_FILES_COMPRESSION_EXCLUDE" : getattr(settings, "DATABASE_FILES_COMPRESSION_EXCLUDE", ("zip", "gz", "rar", "jpg", "jpeg", "gif", "png", "mpg", "mpeg", "qt", "avi", "mov", "mkv")),
	"DATABASE_FILES_SECRET_KEY" : getattr(settings, "DATABASE_FILES_SECRET_KEY", getattr(settings, "SECRET_KEY", None)),
	"DATABASE_FILES_COMPRESSION" : getattr(settings, "DATABASE_FILES_COMPRESSION", False),
	"DATABASE_FILES_ENCRYPTION" : getattr(settings, "DATABASE_FILES_ENCRYPTION", False),
}
