"""Pydantic models describing the API's request and response bodies."""

from pydantic import BaseModel, Field, field_validator


class TranslationRequest(BaseModel):
    """Body of POST /api/translate."""

    text: str = Field(..., min_length=1, max_length=5000)
    source_lang: str = Field(default="auto")
    target_lang: str = Field(...)

    @field_validator("text")
    @classmethod
    def text_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("text must not be empty or whitespace only")
        return value

    @field_validator("source_lang", "target_lang")
    @classmethod
    def lang_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("language code must not be empty")
        return value.strip().lower()


class TranslationResponse(BaseModel):
    """Body returned by POST /api/translate on success."""

    translated_text: str


class LanguagesResponse(BaseModel):
    """Body returned by GET /api/languages."""

    languages: dict[str, str]


class ErrorResponse(BaseModel):
    """Body returned on any error response."""

    detail: str