"""
recognizers.py — Reconocedores de PII específicos para español (SISTAC)

Define PatternRecognizer personalizados para identificadores españoles
no cubiertos por los reconocedores built-in de Presidio:

    EsDniRecognizer   — DNI español  (8 dígitos + letra: 12345678A)
    EsNieRecognizer   — NIE español  (X/Y/Z + 7 dígitos + letra: X1234567L)
    EsPhoneRecognizer — Teléfono ES  (+34 6XX XXX XXX / 9XX XXX XXX)
    EsCpRecognizer    — Código postal (5 dígitos: 28013)

Autor: Mario A. Belvisi Lescano
"""

from presidio_analyzer import Pattern, PatternRecognizer


# ── DNI ───────────────────────────────────────────────────────────────────────

class EsDniRecognizer(PatternRecognizer):
    """
    Reconoce el Documento Nacional de Identidad español.

    Formato: 8 dígitos seguidos de una letra mayúscula.
    Ejemplo: 12345678A

    La letra de control se omite de la validación para maximizar
    el recall — los CVs sintéticos pueden contener DNIs con letras
    aleatorias.
    """

    PATTERNS = [
        Pattern(
            name="dni_standard",
            regex=r"\b\d{8}[A-HJ-NP-TV-Z]\b",   # excluye I, O, U (letras inválidas DNI)
            score=0.85,
        ),
        Pattern(
            name="dni_relaxed",
            regex=r"\b\d{8}[A-Z]\b",
            score=0.6,
        ),
    ]

    CONTEXT = [
        "DNI", "D.N.I", "D.N.I.", "NIF", "N.I.F",
        "documento", "identidad", "número de identificación",
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(
            supported_entity="ES_DNI",
            patterns=self.PATTERNS,
            context=self.CONTEXT,
            supported_language="es",
        )


# ── NIE ───────────────────────────────────────────────────────────────────────

class EsNieRecognizer(PatternRecognizer):
    """
    Reconoce el Número de Identidad de Extranjero español.

    Formato: X, Y o Z + 7 dígitos + letra mayúscula.
    Ejemplo: X1234567L
    """

    PATTERNS = [
        Pattern(
            name="nie_standard",
            regex=r"\b[XYZ]\d{7}[A-HJ-NP-TV-Z]\b",
            score=0.90,
        ),
    ]

    CONTEXT = [
        "NIE", "N.I.E", "N.I.E.", "extranjero",
        "número de identidad", "residencia",
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(
            supported_entity="ES_NIE",
            patterns=self.PATTERNS,
            context=self.CONTEXT,
            supported_language="es",
        )


# ── Teléfono español ──────────────────────────────────────────────────────────

class EsPhoneRecognizer(PatternRecognizer):
    """
    Reconoce números de teléfono españoles.

    Cubre:
    - Móviles: 6XX XXX XXX / 7XX XXX XXX
    - Fijos:   9XX XXX XXX / 8XX XXX XXX
    - Con prefijo internacional: +34 / 0034

    Los separadores admitidos son espacio, guion y punto.
    """

    PATTERNS = [
        Pattern(
            name="es_phone_intl",
            regex=r"(\+34|0034)[\s.\-]?[6-9]\d{2}[\s.\-]?\d{3}[\s.\-]?\d{3}",
            score=0.90,
        ),
        Pattern(
            name="es_phone_local",
            regex=r"\b[6-9]\d{2}[\s.\-]?\d{3}[\s.\-]?\d{3}\b",
            score=0.60,
        ),
    ]

    CONTEXT = [
        "teléfono", "tel", "tel.", "móvil", "movil",
        "phone", "celular", "contacto", "tfno",
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(
            supported_entity="ES_PHONE",
            patterns=self.PATTERNS,
            context=self.CONTEXT,
            supported_language="es",
        )


# ── Código postal ─────────────────────────────────────────────────────────────

class EsCpRecognizer(PatternRecognizer):
    """
    Reconoce códigos postales españoles.

    Formato: 5 dígitos, con el primero entre 0 y 5
    (provincias 01-52, más Ceuta 51 y Melilla 52).

    Se exige contexto cercano para evitar falsos positivos
    con años o cantidades numéricas.
    """

    PATTERNS = [
        Pattern(
            name="es_cp",
            regex=r"\b[0-5]\d{4}\b",
            score=0.50,
        ),
    ]

    CONTEXT = [
        "CP", "C.P.", "código postal", "codigo postal",
        "postal", "zip", "localidad",
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(
            supported_entity="ES_CP",
            patterns=self.PATTERNS,
            context=self.CONTEXT,
            supported_language="es",
        )


# ── Cédula de Identidad Uruguaya (Rioplatense) ──────────────────────────────────

class UyCiRecognizer(PatternRecognizer):
    """
    Reconoce la Cédula de Identidad uruguaya.
    Formatos: X.XXX.XXX-Y, XXX.XXX-Y, XXXXXXX-Y o XXXXXXXY.
    """

    PATTERNS = [
        Pattern(
            name="uy_ci_dots_dash",
            regex=r"\b[1-9]\.?\d{3}\.?\d{3}[-\s]?\d\b",   # inicia con 1-9 para evitar colisión con móviles 09X
            score=0.85,
        ),
    ]

    CONTEXT = [
        "cédula", "cedula", "C.I.", "CI", "documento",
        "identidad", "nro", "número",
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(
            supported_entity="UY_CI",
            patterns=self.PATTERNS,
            context=self.CONTEXT,
            supported_language="es",
        )


# ── DNI Argentino (Rioplatense) ──────────────────────────────────────────────────

class ArDniRecognizer(PatternRecognizer):
    """
    Reconoce el DNI argentino.
    Formatos: XX.XXX.XXX o XXXXXXXX (7 u 8 dígitos).
    """

    PATTERNS = [
        Pattern(
            name="ar_dni_dots",
            regex=r"\b\d{1,2}\.?\d{3}\.?\d{3}\b",
            score=0.80,
        ),
    ]

    CONTEXT = [
        "DNI", "D.N.I.", "D.N.I", "documento",
        "identidad", "número de documento",
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(
            supported_entity="AR_DNI",
            patterns=self.PATTERNS,
            context=self.CONTEXT,
            supported_language="es",
        )


# ── Teléfonos Rioplatenses (Uruguay/Argentina) ──────────────────────────────────

class RioplatensePhoneRecognizer(PatternRecognizer):
    """
    Reconoce teléfonos móviles y fijos de Uruguay (+598 / 09X) y Argentina (+54 / 9 / 15).
    """

    PATTERNS = [
        Pattern(
            name="uy_phone_intl",
            regex=r"(?:\+598|00598)[\s.\-]?9[1-9]\d[\s.\-]?\d{3}[\s.\-]?\d{3}\b",
            score=0.90,
        ),
        Pattern(
            name="uy_phone_local",
            regex=r"\b09[1-9][\s.\-]?\d{3}[\s.\-]?\d{3}\b",
            score=0.80,
        ),
        Pattern(
            name="ar_phone_intl",
            regex=r"(?:\+54|0054)[\s.\-]?9[\s.\-]?\d{2,4}[\s.\-]?\d{6,8}\b",
            score=0.90,
        ),
        Pattern(
            name="ar_phone_local",
            regex=r"\b15[\s.\-]?\d{4,5}[\s.\-]?\d{4}\b",
            score=0.70,
        ),
    ]

    CONTEXT = [
        "teléfono", "tel", "tel.", "móvil", "movil", "celular",
        "cel", "contacto", "teléfono de contacto", "celu",
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(
            supported_entity="RIO_PHONE",
            patterns=self.PATTERNS,
            context=self.CONTEXT,
            supported_language="es",
        )


# ── Códigos Postales Rioplatenses ──────────────────────────────────────────────

class RioplatenseCpRecognizer(PatternRecognizer):
    """
    Reconoce códigos postales de Uruguay (5 dígitos independientes) y Argentina (alfanumérico de 8 car. o 4 dígitos).
    """

    PATTERNS = [
        Pattern(
            name="uy_cp",
            regex=r"\b\d{5}\b",
            score=0.45,
        ),
        Pattern(
            name="ar_cp_intl",
            regex=r"\b[A-HJ-NP-TV-Z]\d{4}[A-Z]{3}\b",
            score=0.85,
        ),
    ]

    CONTEXT = [
        "CP", "C.P.", "código postal", "codigo postal",
        "postal", "zip", "localidad",
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(
            supported_entity="RIO_CP",
            patterns=self.PATTERNS,
            context=self.CONTEXT,
            supported_language="es",
        )


# ── Registro de todos los reconocedores ──────────────────────────────────────

SISTAC_RECOGNIZERS = [
    EsDniRecognizer(),
    EsNieRecognizer(),
    EsPhoneRecognizer(),
    EsCpRecognizer(),
    UyCiRecognizer(),
    ArDniRecognizer(),
    RioplatensePhoneRecognizer(),
    RioplatenseCpRecognizer(),
]

