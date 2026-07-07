#!/usr/bin/env python3
"""
test_anonymizer.py — Valida la precisión y recall de SistacAnonymizer (OE3).

Prueba el módulo sobre un golden set local con formatos rioplatenses
(Uruguay y Argentina) de nombres, correos, documentos (CI y DNI),
teléfonos y códigos postales.
"""

import sys
from pathlib import Path

# Agregar sistac/ al path (INV-16)
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "python"))

from sistac.pii.anonymizer import SistacAnonymizer

# Golden set de prueba con entidades anotadas
# Cada tupla contiene: (texto_original, entidades_esperadas)
GOLDEN_SET = [
    (
        "Mi nombre es Juan Pérez y mi correo es juan.perez@gmail.com",
        {"PERSONA": "Juan Pérez", "EMAIL": "juan.perez@gmail.com"}
    ),
    (
        "Llamar a María Noel de León al celular 099 123 456 para coordinar.",
        {"PERSONA": "María Noel de León", "TELEFONO": "099 123 456"}
    ),
    (
        "El candidato es Mateo Rodríguez, CI 4.876.543-2 y vive en Montevideo.",
        {"PERSONA": "Mateo Rodríguez", "DNI": "4.876.543-2"}
    ),
    (
        "Sofía González, DNI 39.123.456, egresada de UdelaR.",
        {"PERSONA": "Sofía González", "DNI": "39.123.456"}
    ),
    (
        "Contacto: +598 94 888 777. Correo: info@empresa.com.uy",
        {"TELEFONO": "+598 94 888 777", "EMAIL": "info@empresa.com.uy"}
    ),
    (
        "Comunicarse con Martín Silva al 15 5432 1098 en Buenos Aires.",
        {"PERSONA": "Martín Silva", "TELEFONO": "15 5432 1098"}
    ),
    (
        "Mi código postal en Montevideo es 11300.",
        {"CP": "11300"}
    ),
    (
        "Enviar CV a reclutamiento.matriz@gmail.com o llamar al 091456789.",
        {"EMAIL": "reclutamiento.matriz@gmail.com", "TELEFONO": "091456789"}
    ),
]


def run_pii_tests():
    print("=== SISTAC — Test Unitario de Anonimización PII (OE3) ===\n")
    print("Cargando SistacAnonymizer...")
    anon = SistacAnonymizer()
    print("\nEjecutando pruebas sobre el Golden Set Rioplatense...")

    total_entities = 0
    true_positives = 0
    false_positives = 0
    false_negatives = 0

    for idx, (text, expected) in enumerate(GOLDEN_SET, start=1):
        print(f"\n[Test {idx}] Texto original:")
        print(f"  \"{text}\"")
        
        # Anonimizar
        anon_text = anon.anonymize(text)
        print("Texto anonimizado:")
        print(f"  \"{anon_text}\"")
        
        # Evaluar detección
        for entity_type, raw_val in expected.items():
            total_entities += 1
            # Verificar si el valor original desapareció y fue reemplazado por un placeholder
            placeholder = f"<{entity_type}>"
            
            # Si el texto original sigue ahí -> False Negative
            if raw_val in anon_text:
                print(f"  [FAIL] FALLO: Entidad '{raw_val}' ({entity_type}) no fue anonimizada.")
                false_negatives += 1
            # Si el texto original se fue y el placeholder está presente -> True Positive
            elif placeholder in anon_text:
                true_positives += 1
            else:
                print(f"  [FAIL] FALLO: Entidad '{raw_val}' ({entity_type}) se eliminó pero falta el placeholder {placeholder}.")
                false_negatives += 1

        # Verificar falsos positivos (placeholders que aparecieron y no correspondían a lo esperado)
        # Contamos cuántos de cada tipo de placeholder hay en el texto anonimizado
        for placeholder_key, placeholder_val in [("PERSONA", "<PERSONA>"), ("EMAIL", "<EMAIL>"), ("TELEFONO", "<TELEFONO>"), ("DNI", "<DNI>"), ("CP", "<CP>")]:
            expected_count = sum(1 for et in expected if et == placeholder_key)
            actual_count = anon_text.count(placeholder_val)
            if actual_count > expected_count:
                fps = actual_count - expected_count
                false_positives += fps
                print(f"  [WARN] ALERTA: {fps} falso(s) positivo(s) de tipo {placeholder_val} detectado(s).")

    # Calcular métricas
    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    print("\n================ REPORT REPORT ================")
    print(f"Total de entidades esperadas : {total_entities}")
    print(f"Verdaderos Positivos (TP)    : {true_positives}")
    print(f"Falsos Positivos (FP)        : {false_positives}")
    print(f"Falsos Negativos (FN)        : {false_negatives}")
    print("-----------------------------------------------")
    print(f"Precisión                    : {precision:.4f} (Meta: >= 0.95)")
    print(f"Recall (Sensibilidad)        : {recall:.4f} (Meta: >= 0.95)")
    print(f"F1-score                     : {f1:.4f}")
    print("===============================================")
    
    if precision >= 0.95 and recall >= 0.95:
        print("\n  [SUCCESS] OE3 cumplido con éxito. Precisión y recall superan el umbral de 0.95.")
    else:
        print("\n  [FAIL] El módulo PII no alcanzó el umbral del 0.95 en precisión o recall.")


if __name__ == "__main__":
    run_pii_tests()
