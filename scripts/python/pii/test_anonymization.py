"""
test_anonymization.py — Tests de validación del módulo de anonimización PII

Valida que el anonimizador elimina correctamente las entidades PII
sin destruir contexto útil para el scoring semántico.

Autor: Mario A. Belvisi Lescano

CÓMO EJECUTAR:
    pytest scripts/python/pii/test_anonymization.py -v
"""

import pytest


# ============================================================
# Fixtures de CVs de prueba
# ============================================================

SAMPLE_CV_ES = """
María García López
Calle Mayor 45, 3ºB, 28013 Madrid
maria.garcia@email.com | +34 612 345 678
DNI: 12345678A

EXPERIENCIA PROFESIONAL
Empresa Accenture (2021-2024): Analista de Datos Senior
Universidad Complutense de Madrid — Egresada 2020

EDUCACIÓN
Máster en Ciencia de Datos, UCM, 2020
Licenciatura en Matemáticas, Universidad de Granada, 2018
"""

EXPECTED_REMOVED = ["María García López", "maria.garcia@email.com",
                    "28013", "+34 612 345 678", "12345678A"]

EXPECTED_PRESERVED_KEYWORDS = ["Analista de Datos Senior", "Ciencia de Datos",
                                "Matemáticas", "2021", "2024"]


# ============================================================
# Tests básicos de supresión de PII
# ============================================================

class TestAnonymizationBasic:
    """Tests de que las entidades PII son eliminadas correctamente."""

    def test_name_removed(self, anonymizer):
        """El nombre completo no debe aparecer en el texto anonimizado."""
        result = anonymizer.anonymize(SAMPLE_CV_ES)
        assert "María García López" not in result, \
            "El nombre completo sigue presente tras anonimización"

    def test_email_removed(self, anonymizer):
        """El email no debe aparecer en el texto anonimizado."""
        result = anonymizer.anonymize(SAMPLE_CV_ES)
        assert "maria.garcia@email.com" not in result, \
            "El email sigue presente tras anonimización"

    def test_phone_removed(self, anonymizer):
        """El teléfono no debe aparecer en el texto anonimizado."""
        result = anonymizer.anonymize(SAMPLE_CV_ES)
        assert "+34 612 345 678" not in result, \
            "El teléfono sigue presente tras anonimización"

    def test_dni_removed(self, anonymizer):
        """El DNI no debe aparecer en el texto anonimizado."""
        result = anonymizer.anonymize(SAMPLE_CV_ES)
        assert "12345678A" not in result, \
            "El DNI sigue presente tras anonimización"


class TestContextPreservation:
    """Tests de que el contexto relevante para scoring NO es eliminado."""

    def test_job_title_preserved(self, anonymizer):
        """El título del puesto debe preservarse."""
        result = anonymizer.anonymize(SAMPLE_CV_ES)
        assert "Analista de Datos Senior" in result, \
            "El título del puesto fue eliminado incorrectamente"

    def test_years_preserved(self, anonymizer):
        """Los años de experiencia deben preservarse."""
        result = anonymizer.anonymize(SAMPLE_CV_ES)
        assert "2021" in result or "2024" in result, \
            "Los años de experiencia fueron eliminados"

    def test_field_of_study_preserved(self, anonymizer):
        """El campo de estudio debe preservarse."""
        result = anonymizer.anonymize(SAMPLE_CV_ES)
        assert "Ciencia de Datos" in result, \
            "El campo de estudio fue eliminado incorrectamente"


class TestAnonymizationQuality:
    """Tests de calidad de la anonimización."""

    def test_output_is_string(self, anonymizer):
        """El resultado debe ser una cadena de texto."""
        result = anonymizer.anonymize(SAMPLE_CV_ES)
        assert isinstance(result, str)

    def test_output_not_empty(self, anonymizer):
        """El resultado no debe estar vacío."""
        result = anonymizer.anonymize(SAMPLE_CV_ES)
        assert len(result) > 100, "El texto anonimizado es demasiado corto"

    def test_placeholder_present(self, anonymizer):
        """Los placeholders de sustitución deben estar presentes."""
        result = anonymizer.anonymize(SAMPLE_CV_ES)
        # El anonimizador debe insertar tokens como <PERSON>, <EMAIL>, etc.
        has_placeholder = any(
            token in result for token in ["<PERSON>", "<EMAIL>", "[NOMBRE]", "***"]
        )
        assert has_placeholder, "No se encontraron placeholders de sustitución"


# ============================================================
# Fixture del anonimizador
# (implementar cuando anonymizer.py esté completo)
# ============================================================

@pytest.fixture
def anonymizer():
    """Fixture que provee una instancia del anonimizador SISTAC."""
    try:
        from pii.anonymizer import SistacAnonymizer
        return SistacAnonymizer()
    except ImportError:
        pytest.skip("anonymizer.py no implementado todavía")
