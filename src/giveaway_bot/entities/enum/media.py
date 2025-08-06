from enum import StrEnum


class MediaType(StrEnum):
    PHOTO = "photo"

    @property
    def extension(self) -> str:
        if self == MediaType.PHOTO:
            return "jpg"

