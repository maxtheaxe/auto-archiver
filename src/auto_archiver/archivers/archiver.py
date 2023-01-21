from __future__ import annotations
from abc import abstractmethod
from dataclasses import dataclass
import os
import mimetypes, requests
from ..core import Metadata
from ..core import Step


@dataclass
class Archiver(Step):
    name = "archiver"

    def __init__(self, config: dict) -> None:
        # without this STEP.__init__ is not called
        super().__init__(config)

    def init(name: str, config: dict) -> Archiver:
        # only for typing...
        return Step.init(name, config, Archiver)

    def setup(self) -> None:
        # used when archivers need to login or do other one-time setup
        pass

    def clean_url(self, url: str) -> str:
        # used to clean unnecessary URL parameters
        return url

    def _guess_file_type(self, path: str) -> str:
        """
        Receives a URL or filename and returns global mimetype like 'image' or 'video'
        see https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types/Common_types
        """
        mime = mimetypes.guess_type(path)[0]
        if mime is not None:
            return mime.split("/")[0]
        return ""

    def download_from_url(self, url: str, to_filename: str = None, item: Metadata = None) -> str:
        """
        downloads a URL to provided filename, or inferred from URL, returns local filename, if item is present will use its tmp_dir
        """
        if not to_filename:
            to_filename = url.split('/')[-1].split('?')[0]
            if len(to_filename) > 64:
                to_filename = to_filename[-64:]
        if item:
            to_filename = os.path.join(item.get_tmp_dir(), to_filename)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'
        }
        d = requests.get(url, headers=headers)
        with open(to_filename, 'wb') as f:
            f.write(d.content)
        return to_filename

    @abstractmethod
    def download(self, item: Metadata) -> Metadata: pass

    # TODO: how to fix allow predictable key
    # def get_key(self, filename):
    #     """
    #     returns a key in the format "[archiverName]_[filename]" includes extension
    #     """
    #     tail = os.path.split(filename)[1]  # returns filename.ext from full path
    #     _id, extension = os.path.splitext(tail)  # returns [filename, .ext]
    #     if 'unknown_video' in _id:
    #         _id = _id.replace('unknown_video', 'jpg')

    #     # long filenames can cause problems, so trim them if necessary
    #     if len(_id) > 128:
    #         _id = _id[-128:]

    #     return f'{self.name}_{_id}{extension}'