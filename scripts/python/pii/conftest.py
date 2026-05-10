"""
conftest.py — Fixtures pytest para el módulo PII de SISTAC

El fixture `anonymizer` se comparte con scope="session" para cargar
spaCy y Presidio una sola vez durante toda la suite de tests,
evitando la penalización de tiempo de inicialización por cada test.

Autor: Mario A. Belvisi Lescano
"""

import pytest

from pii.anonymizer import SistacAnonymizer


@pytest.fixture(scope="session")
def anonymizer() -> SistacAnonymizer:
    """
    Instancia de SistacAnonymizer compartida para toda la sesión de tests.

    scope="session" → spaCy se carga una sola vez (~3-5 segundos).
    Sin este scope, cada test pagaría el costo de inicialización.
    """
    return SistacAnonymizer()
