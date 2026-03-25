from typing import Optional

from pydantic import BaseModel, ConfigDict


class DigestBase(BaseModel):
    chapter_id: int
    paragraph_number: int
    digest: str

    model_config = ConfigDict(from_attributes=True, strict=True)


class DigestCreate(DigestBase):
    pass


class DigestUpdate(DigestBase):
    chapter_id: Optional[int] = None
    paragraph_number: Optional[int] = None
    digest: Optional[str] = None


class Digest(DigestBase):
    id: int
