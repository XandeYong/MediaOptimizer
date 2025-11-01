class PathManager:
    def __init__(self, root, log, failed_media, temp_media, optimized_media, raw_media, uploaded_media, failed_upload_media):
        self._root: str = root
        self._log: str = log
        self._failed_media: str = failed_media
        self._temp_media: str = temp_media
        self._optimized_media: str = optimized_media
        self._raw_media: str = raw_media
        self._uploaded_media: str = uploaded_media
        self._failed_upload_media: str = failed_upload_media

    def __str__(self):
        return f"""root={self._root}\n
        log={self._log}\n
        failed_media={self._failed_media}\n
        temp_media={self._temp_media}\n
        optimized_media={self._optimized_media}\n
        raw_media={self._raw_media}\n
        uploaded_media={self._uploaded_media}\n
        failed_upload_media={self._failed_upload_media}"""

    @property
    def root(self):
        return self._root

    @property
    def log(self):
        return self._log

    @property
    def failed_media(self):
        return self._failed_media
    
    @property
    def temp_media(self):
        return self._temp_media

    @property
    def optimized_media(self):
        return self._optimized_media
    
    @property
    def raw_media(self):
        return self._raw_media
    
    @property
    def uploaded_media(self):
        return self._uploaded_media
    
    @property
    def failed_upload_media(self):
        return self._failed_upload_media
