"""FastAPI entrypoint for the Translator API."""

import logging

import uvicorn
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from models import ErrorResponse, LanguagesResponse, TranslationRequest, TranslationResponse
from translator import TranslationError, TranslatorService

logger = logging.getLogger("translator_api")
logging.basicConfig(level=logging.INFO)

settings = get_settings()

app = FastAPI(title=settings.app_name, debug=settings.debug)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

translator_service = TranslatorService()


@app.get("/api/health")
def health_check() -> dict:
    """Simple uptime check."""
    return {"status": "ok"}


@app.get(
    "/api/languages",
    response_model=LanguagesResponse,
    responses={500: {"model": ErrorResponse}},
)
def get_languages() -> LanguagesResponse:
    """Return the list of languages supported for translation."""
    try:
        languages = translator_service.get_supported_languages()
    except TranslationError as exc:
        logger.exception("Failed to load supported languages")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc
    return LanguagesResponse(languages=languages)


@app.post(
    "/api/translate",
    response_model=TranslationResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
def translate_text(payload: TranslationRequest) -> TranslationResponse:
    """Translate the given text from source_lang to target_lang."""
    try:
        translated = translator_service.translate(
            text=payload.text,
            source_lang=payload.source_lang,
            target_lang=payload.target_lang,
        )
    except TranslationError as exc:
        # Bad/unsupported language codes or an empty result -> client-facing 400.
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:  # truly unexpected -> 500
        logger.exception("Unexpected error during translation")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again.",
        ) from exc

    return TranslationResponse(translated_text=translated)


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=settings.debug)