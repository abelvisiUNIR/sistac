"""
anonymizer.py — Módulo de anonimización PII para SISTAC (Configuración C3)

Detecta y redacta entidades de información personal identificable (PII)
en CVs en español, preservando el contexto profesional necesario para
el scoring semántico del sistema RAG+LLM.

Entidades redactadas → placeholder:
    PERSON          → <PERSONA>
    EMAIL_ADDRESS   → <EMAIL>
    PHONE_NUMBER    → <TELEFONO>
    ES_PHONE        → <TELEFONO>
    ES_DNI          → <DNI>
    ES_NIE          → <NIE>
    ES_CP           → <CP>

Entidades NO redactadas (preservadas):
    LOCATION        — ciudades y nombres de empresas (contexto profesional)
    DATE_TIME       — años de experiencia y educación
    ORGANIZATION    — nombres de empresas y universidades

Stack: Microsoft Presidio + spaCy es_core_news_lg

Autor: Mario A. Belvisi Lescano
Hipótesis: H3 — La anonimización PII reduce DIR y SPD respecto a C1 y C2
"""

import sys
from collections import Counter

from loguru import logger
from presidio_analyzer import AnalyzerEngine, RecognizerResult
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

from pii.recognizers import SISTAC_RECOGNIZERS

# ── Constantes ────────────────────────────────────────────────────────────────

# Entidades a redactar (las demás se ignoran)
_ENTITIES_TO_REDACT = [
    "PERSON",
    "EMAIL_ADDRESS",
    "PHONE_NUMBER",
    "ES_PHONE",
    "ES_DNI",
    "ES_NIE",
    "ES_CP",
]

# Mapa entidad → placeholder legible
_PLACEHOLDER_MAP: dict[str, str] = {
    "PERSON":         "<PERSONA>",
    "EMAIL_ADDRESS":  "<EMAIL>",
    "PHONE_NUMBER":   "<TELEFONO>",
    "ES_PHONE":       "<TELEFONO>",
    "ES_DNI":         "<DNI>",
    "ES_NIE":         "<NIE>",
    "ES_CP":          "<CP>",
}

# Tokens que indican que una entidad PERSON detectada es en realidad
# el nombre de una organización (falso positivo del NER de spaCy)
_ORG_KEYWORDS = {
    "universidad", "universitat", "university",
    "instituto", "institute", "escuela", "school",
    "empresa", "compañia", "compañía", "company",
    "s.a.", "s.l.", "s.a.u.", "s.l.u.", "s.c.", "ltd", "inc", "corp",
    "grupo", "group", "asociación", "asociacion", "fundación", "fundacion",
    "ministerio", "ayuntamiento", "gobierno", "agencia",
    "hospital", "clínica", "clinica", "centro",
    "accenture", "deloitte", "kpmg", "ibm", "microsoft", "google",
}


# ── Clase principal ───────────────────────────────────────────────────────────

class SistacAnonymizer:
    """
    Anonimizador de CVs en español para la configuración C3 de SISTAC.

    Carga spaCy y Presidio una sola vez en `__init__` para ser reutilizado
    eficientemente durante el experimento (≥ 300 CVs).

    Uso básico:
        anon = SistacAnonymizer()
        texto_limpio = anon.anonymize(cv_text)

    Uso con reporte:
        reporte = anon.get_redaction_report(cv_text)
    """

    def __init__(
        self,
        language: str = "es",
        score_threshold: float = 0.4,
    ) -> None:
        """
        Inicializa el motor de análisis y anonimización.

        Args:
            language:        Idioma de análisis (por defecto "es" para español).
            score_threshold: Confianza mínima para considerar una detección
                             como PII. Valor más bajo → más recall, más
                             falsos positivos. Recomendado: 0.4.
        """
        self.language = language
        self.score_threshold = score_threshold

        logger.info("Inicializando SistacAnonymizer con spaCy es_core_news_lg...")

        # Motor NLP — spaCy en español
        nlp_config = {
            "nlp_engine_name": "spacy",
            "models": [
                {"lang_code": "es", "model_name": "es_core_news_lg"},
            ],
        }
        nlp_engine = NlpEngineProvider(nlp_configuration=nlp_config).create_engine()

        # Motor de análisis — Presidio con reconocedores custom
        self._analyzer = AnalyzerEngine(
            nlp_engine=nlp_engine,
            supported_languages=["es"],
        )
        for recognizer in SISTAC_RECOGNIZERS:
            self._analyzer.registry.add_recognizer(recognizer)

        # Motor de anonimización — operadores Replace por entidad
        self._anonymizer = AnonymizerEngine()
        self._operators = {
            entity: OperatorConfig("replace", {"new_value": placeholder})
            for entity, placeholder in _PLACEHOLDER_MAP.items()
        }

        logger.info("SistacAnonymizer listo.")

    # ── Interfaz pública ──────────────────────────────────────────────────────

    def anonymize(self, text: str) -> str:
        """
        Anonimiza un texto de CV en español.

        Redacta PII identificada y la sustituye por placeholders legibles.
        Preserva contexto profesional (títulos, años, campos de estudio).

        Args:
            text: Texto del CV en español (texto plano).

        Returns:
            Texto con PII reemplazada por placeholders.
        """
        if not text or not text.strip():
            return text

        results = self.detect_entities(text)
        if not results:
            return text

        anonymized = self._anonymizer.anonymize(
            text=text,
            analyzer_results=results,
            operators=self._operators,
        )
        return anonymized.text

    def detect_entities(self, text: str) -> list[RecognizerResult]:
        """
        Detecta entidades PII en el texto sin anonimizar.

        Útil para auditoría, debugging y validación del módulo.

        Args:
            text: Texto del CV.

        Returns:
            Lista de RecognizerResult con entidad, posición y score.
        """
        if not text or not text.strip():
            return []

        raw_results = self._analyzer.analyze(
            text=text,
            language=self.language,
            entities=_ENTITIES_TO_REDACT,
            score_threshold=self.score_threshold,
        )

        # Filtrar falsos positivos de PERSON que son nombres de organizaciones
        return [r for r in raw_results if not self._is_org_false_positive(text, r)]

    def get_redaction_report(self, text: str) -> dict:
        """
        Genera un reporte de lo que se redactaría en el texto dado.

        Útil para análisis cuantitativo del módulo y para el paper
        (p. ej.: cuántas entidades por tipo se detectaron en el corpus).

        Args:
            text: Texto del CV.

        Returns:
            Diccionario con estadísticas de detección:
            {
              "n_entities_detected": int,
              "entities_by_type": {"PERSON": 2, "EMAIL_ADDRESS": 1, ...},
              "original_length": int,
              "anonymized_length": int,
              "compression_ratio": float,  # anonymized_length / original_length
            }
        """
        entities = self.detect_entities(text)
        entity_counts = Counter(r.entity_type for r in entities)

        original_length = len(text)
        anonymized_text = self.anonymize(text)
        anonymized_length = len(anonymized_text)

        compression = (
            anonymized_length / original_length if original_length > 0 else 1.0
        )

        return {
            "n_entities_detected": len(entities),
            "entities_by_type": dict(entity_counts),
            "original_length": original_length,
            "anonymized_length": anonymized_length,
            "compression_ratio": round(compression, 4),
        }

    # ── Métodos auxiliares ────────────────────────────────────────────────────

    def _is_org_false_positive(
        self, text: str, result: RecognizerResult
    ) -> bool:
        """
        Determina si una detección PERSON es en realidad el nombre de
        una organización (falso positivo del NER de spaCy en español).

        El NER de es_core_news_lg confunde frecuentemente nombres de
        universidades y empresas con entidades PERSON.

        Args:
            text:   Texto completo del CV.
            result: Resultado de detección de Presidio.

        Returns:
            True si la entidad debe descartarse (es una organización).
        """
        if result.entity_type != "PERSON":
            return False

        # Ventana de contexto: 60 caracteres antes y después de la entidad
        start = max(0, result.start - 60)
        end = min(len(text), result.end + 60)
        context_window = text[start:end].lower()

        # Si algún keyword organizacional aparece en el contexto → FP
        return any(keyword in context_window for keyword in _ORG_KEYWORDS)


# ── Demo / test rápido ────────────────────────────────────────────────────────

if __name__ == "__main__":
    logger.remove()
    logger.add(sys.stderr, level="INFO")

    SAMPLE_CV = """
María García López
Calle Mayor 45, 3ºB, 28013 Madrid
maria.garcia@email.com | +34 612 345 678
DNI: 12345678A

EXPERIENCIA PROFESIONAL
Accenture (2021-2024): Analista de Datos Senior
Universidad Complutense de Madrid — Egresada 2020

EDUCACIÓN
Máster en Ciencia de Datos, UCM, 2020
Licenciatura en Matemáticas, Universidad de Granada, 2018

HABILIDADES
Python, SQL, Machine Learning, Power BI
"""

    print("=" * 60)
    print("SISTAC — Demo de anonimización PII")
    print("=" * 60)

    anon = SistacAnonymizer()

    print("\n--- TEXTO ORIGINAL ---")
    print(SAMPLE_CV)

    print("\n--- TEXTO ANONIMIZADO ---")
    resultado = anon.anonymize(SAMPLE_CV)
    print(resultado)

    print("\n--- REPORTE DE REDACCION ---")
    reporte = anon.get_redaction_report(SAMPLE_CV)
    for k, v in reporte.items():
        print(f"  {k}: {v}")
