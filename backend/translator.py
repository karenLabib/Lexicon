"""Translation logic, backed by the deep-translator library (Google Translate,
no API key required)."""

from deep_translator import GoogleTranslator
from deep_translator.exceptions import LanguageNotSupportedException, NotValidPayload


class TranslationError(Exception):
    """Raised when a translation request cannot be fulfilled, with a
    user-friendly message safe to return to the client."""


class TranslatorService:
    """Thin wrapper around deep_translator.GoogleTranslator."""

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """Translate `text` from `source_lang` to `target_lang`.

        `source_lang` may be "auto" to request language auto-detection.
        Raises TranslationError on any failure.
        """
        try:
            translator = GoogleTranslator(source=source_lang, target=target_lang)
            result = translator.translate(text)
        except (LanguageNotSupportedException, NotValidPayload) as exc:
            raise TranslationError(str(exc)) from exc
        except Exception as exc:  # deep-translator can raise plain Exceptions
            # (e.g. network errors) that aren't part of its typed exception set.
            raise TranslationError(
                "Translation failed. Please check the selected languages and try again."
            ) from exc

        if not result:
            raise TranslationError("Translation returned an empty result.")

        return result

    def get_supported_languages(self) -> dict[str, str]:
        """Return a mapping of language code -> display name, with an
        "auto" (detect language) option prepended."""
        try:
            languages = GoogleTranslator().get_supported_languages(as_dict=True)
        except Exception as exc:
            raise TranslationError("Could not load the list of supported languages.") from exc

        # deep-translator returns {"name": "code"}; invert to {"code": "Name"}.
        code_to_name = {code: name.title() for name, code in languages.items()}
        return {"auto": "Detect Language", **code_to_name}