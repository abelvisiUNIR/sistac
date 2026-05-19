"""
data/synthetic_corpus_generator.py — Generación del corpus sintético SISTAC

Genera 300 CVs sintéticos en español rioplatense para el experimento factorial C0-C3.

Cada CV incluye:
  - Texto libre en español (para pipeline RAG)
  - PII real: nombre, email, teléfono, dirección (para módulo H3)
  - Atributos demográficos: género, grupo etario (para cálculo DIR/SPD)
  - Etiqueta Gold Standard: APTO / NO_APTO (para H1/H2)

Diseño del corpus:
  - 5 perfiles de cargo (JDs): Analista de Datos, Backend Python, RRHH,
    Contador, Ingeniería de Software
  - 60 CVs por JD: 30 APTO + 30 NO_APTO
  - Género: 50% M / 50% F dentro de cada grupo (para balancear H3)
  - 3 grupos etarios: 23-35, 36-45, 46-58

Lógica de etiquetado (transparente, documentada en sección 5.9 del TFE):
  Score = experiencia_relevante(0-50) + coincidencia_skills(0-30)
          + nivel_educativo(0-15) + certificaciones(0-5)
  APTO si Score >= 60

Outputs:
  data/raw/cvs/CV_001.txt ... CV_300.txt
  data/raw/job_descriptions/JD_001.txt ... JD_005.txt
  data/raw/gold_standard/ground_truth.csv
  data/raw/gold_standard/c0_times.csv  (tiempos simulados screening manual C0)

Reproducible con RANDOM_SEED = 42 (INV-14).

Autores: Mario A. Belvisi Lescano + David I. Madrid Oyanadel
"""

from __future__ import annotations

import csv
import io
import random
import sys
from pathlib import Path

# Forzar salida UTF-8 en Windows (evita UnicodeEncodeError con caracteres como →)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import numpy as np

# ── INV-14: Semilla global ────────────────────────────────────────────────────
random.seed(42)
np.random.seed(42)

# ── INV-16: Rutas via PROJECT_ROOT ────────────────────────────────────────────
_SCRIPTS_DIR = Path(__file__).parent.parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from config import (
    CVS_RAW,
    JOB_DESCRIPTIONS,
    GOLD_STANDARD_DIR,
    RANDOM_SEED,
    ensure_dirs,
)

# ── Parámetros del corpus ─────────────────────────────────────────────────────
N_TOTAL        = 300   # CVs totales
N_JDS          = 5     # Perfiles de cargo
N_PER_JD       = 60    # CVs por JD
N_APTO_PER_JD  = 30    # APTO por JD
N_NOAP_PER_JD  = 30    # NO_APTO por JD
SCORE_THRESHOLD = 60   # Umbral Gold Standard (igual que config.SCORE_THRESHOLD=70
                        # pero aquí usamos 60 para generar distribución natural;
                        # el threshold del pipeline es 70)

# ── Datos demográficos rioplatenses ───────────────────────────────────────────

NOMBRES_F = [
    "Ana Laura", "María José", "Valentina", "Florencia", "Camila",
    "Lucía", "Sofía", "Natalia", "Carolina", "Gabriela",
    "Verónica", "Alejandra", "Patricia", "Jimena", "Romina",
    "Cecilia", "Claudia", "Andrea", "Silvana", "Daniela",
    "Paola", "Leticia", "Valeria", "Mónica", "Fernanda",
    "Mariana", "Laura", "Paula", "Graciela", "Beatriz",
]

NOMBRES_M = [
    "Santiago", "Martín", "Alejandro", "Federico", "Nicolás",
    "Gonzalo", "Pablo", "Sebastián", "Diego", "Matías",
    "Andrés", "Carlos", "Jorge", "Roberto", "Hernán",
    "Rodrigo", "Gustavo", "Leonardo", "Javier", "Ricardo",
    "Emiliano", "Tomás", "Maximiliano", "Ignacio", "Agustín",
    "Ramiro", "Facundo", "Damián", "Germán", "Bruno",
]

APELLIDOS = [
    "González", "Rodríguez", "García", "Fernández", "López",
    "Martínez", "Sánchez", "Pérez", "Gómez", "Díaz",
    "Hernández", "Álvarez", "Romero", "Alonso", "Gutiérrez",
    "Navarro", "Torres", "Domínguez", "Vázquez", "Ramos",
    "Ramírez", "Moreno", "Muñoz", "Álvarez", "Ruiz",
    "Suárez", "Molina", "Morales", "Ortega", "Delgado",
    "Castro", "Ortiz", "Rubio", "Marín", "Sanz",
    "Iglesias", "Núñez", "Medina", "Garrido", "Cortés",
]

BARRIOS_MVD = [
    "Pocitos", "Punta Carretas", "Malvín", "Buceo", "Carrasco",
    "Centro", "Cordón", "Palermo", "Parque Rodó", "Tres Cruces",
    "La Blanqueada", "Villa Española", "Sayago", "Colón", "Cerro",
]

CALLES_MVD = [
    "Av. Brasil", "Bulevar Artigas", "Av. Italia", "Av. Gral. Flores",
    "Av. 18 de Julio", "Calle Colonia", "Rivera", "Av. Libertador",
    "Punta Gorda", "Ellauri", "Rambla República del Perú",
    "Av. Uruguay", "Constituyente", "Jackson", "Calle Durazno",
]

UNIVERSIDADES_UY = [
    "Universidad de la República (UdelaR)",
    "Universidad ORT Uruguay",
    "Universidad Católica del Uruguay (UCU)",
    "Universidad de Montevideo (UM)",
    "Universidad Tecnológica (UTEC)",
    "Instituto Tecnológico Superior (ITS)",
]

EMPRESAS_UY = [
    "Tata Consultancy Services Uruguay", "Globant Uruguay", "PedidosYa",
    "ANTEL", "ANCAP", "Banco República (BROU)", "Itaú Uruguay",
    "Santander Uruguay", "BBVA Uruguay", "Grupo Disco-Devoto",
    "Mercado Libre Uruguay", "OCA", "Cutcsa", "UPM Uruguay",
    "Conaprole", "El Observador", "Aeropuertos del Uruguay",
    "Ministerio de Economía y Finanzas", "AGESIC", "Infocorp",
    "Pragma Consultores", "Snoop Consulting", "Overactive",
    "GeneXus", "Hexacta", "Tryolabs", "Baufest Uruguay",
]

# ── Definición de JDs ─────────────────────────────────────────────────────────

JDS = {
    "JD_001": {
        "titulo":       "Analista de Datos",
        "empresa":      "DataVision Uruguay",
        "skills_req":   ["Python", "SQL", "Power BI", "pandas", "análisis estadístico",
                         "visualización de datos", "Excel avanzado", "machine learning básico"],
        "min_exp":      2,
        "min_edu":      "Bachelors",
        "descripcion":  (
            "DataVision Uruguay busca un/a Analista de Datos para integrarse al equipo de "
            "Inteligencia de Negocios. El/la candidato/a será responsable de analizar grandes "
            "volúmenes de datos, generar reportes ejecutivos y construir dashboards estratégicos "
            "para la toma de decisiones.\n\n"
            "RESPONSABILIDADES:\n"
            "- Diseñar y mantener dashboards en Power BI para distintas áreas de negocio.\n"
            "- Desarrollar scripts de análisis y automatización en Python (pandas, numpy).\n"
            "- Consultar y optimizar bases de datos relacionales con SQL avanzado.\n"
            "- Realizar análisis estadísticos descriptivos e inferenciales.\n"
            "- Colaborar con equipos de negocio para traducir necesidades en métricas.\n\n"
            "REQUISITOS:\n"
            "- Licenciatura en Sistemas, Estadística, Matemática o carrera afín.\n"
            "- Mínimo 2 años de experiencia en análisis de datos.\n"
            "- Dominio de Python (pandas, numpy) y SQL avanzado.\n"
            "- Experiencia con herramientas de BI (Power BI o Tableau).\n\n"
            "SE VALORA:\n"
            "- Conocimientos de machine learning (scikit-learn).\n"
            "- Experiencia con bases de datos NoSQL.\n"
            "- Inglés intermedio-avanzado."
        ),
    },
    "JD_002": {
        "titulo":       "Desarrollador/a Backend Python",
        "empresa":      "Solventa Tech",
        "skills_req":   ["Python", "Django", "FastAPI", "PostgreSQL", "Docker",
                         "Git", "APIs REST", "microservicios"],
        "min_exp":      3,
        "min_edu":      "Bachelors",
        "descripcion":  (
            "Solventa Tech busca un/a Desarrollador/a Backend Python para su equipo de "
            "ingeniería de plataformas. Trabajarás en el desarrollo y mantenimiento de APIs "
            "y microservicios que dan soporte a productos fintech con miles de usuarios activos.\n\n"
            "RESPONSABILIDADES:\n"
            "- Desarrollar y mantener APIs REST con Django o FastAPI.\n"
            "- Diseñar esquemas de base de datos en PostgreSQL.\n"
            "- Containerizar servicios con Docker y gestionar despliegues.\n"
            "- Participar en code reviews y garantizar calidad del código.\n"
            "- Integrar servicios de terceros y pasarelas de pago.\n\n"
            "REQUISITOS:\n"
            "- Licenciatura en Informática, Ingeniería de Sistemas o afín.\n"
            "- Mínimo 3 años de experiencia en desarrollo backend con Python.\n"
            "- Dominio de Django o FastAPI, PostgreSQL y Docker.\n"
            "- Conocimiento sólido de Git y metodologías ágiles.\n\n"
            "SE VALORA:\n"
            "- Experiencia con arquitecturas de microservicios.\n"
            "- Conocimiento de AWS o GCP.\n"
            "- Inglés técnico avanzado."
        ),
    },
    "JD_003": {
        "titulo":       "Especialista en Recursos Humanos",
        "empresa":      "Grupo Ánima RR.HH.",
        "skills_req":   ["reclutamiento", "selección de personal", "evaluación de desempeño",
                         "gestión de nóminas", "derecho laboral", "onboarding",
                         "clima organizacional", "entrevistas por competencias"],
        "min_exp":      3,
        "min_edu":      "Bachelors",
        "descripcion":  (
            "Grupo Ánima RR.HH. busca un/a Especialista en Recursos Humanos para gestionar "
            "el ciclo completo de gestión de personas en empresas clientes del sector servicios.\n\n"
            "RESPONSABILIDADES:\n"
            "- Coordinar procesos de reclutamiento y selección end-to-end.\n"
            "- Realizar entrevistas por competencias y evaluaciones psicométricas.\n"
            "- Gestionar procesos de onboarding e inducción de nuevos colaboradores.\n"
            "- Administrar evaluaciones de desempeño y planes de desarrollo.\n"
            "- Asesorar en materia de derecho laboral uruguayo.\n\n"
            "REQUISITOS:\n"
            "- Licenciatura en Psicología, Relaciones Laborales, Administración o afín.\n"
            "- Mínimo 3 años de experiencia en RR.HH. generalista.\n"
            "- Conocimiento de legislación laboral uruguaya.\n"
            "- Experiencia en procesos de selección masiva.\n\n"
            "SE VALORA:\n"
            "- Manejo de ERP de RR.HH. (SAP HR, Workday).\n"
            "- Certificación en entrevistas por competencias.\n"
            "- Inglés intermedio."
        ),
    },
    "JD_004": {
        "titulo":       "Contador/a Senior",
        "empresa":      "Estudio Ferrando & Asociados",
        "skills_req":   ["contabilidad general", "impuestos Uruguay", "auditoría",
                         "Excel avanzado", "NIIF/IFRS", "cierre contable",
                         "DGI", "BPS"],
        "min_exp":      5,
        "min_edu":      "Bachelors",
        "descripcion":  (
            "Estudio Ferrando & Asociados busca un/a Contador/a Senior para brindar servicios "
            "de asesoramiento contable-tributario a empresas medianas del sector comercial e industrial.\n\n"
            "RESPONSABILIDADES:\n"
            "- Elaborar y presentar declaraciones tributarias ante DGI y BPS.\n"
            "- Supervisar cierres contables mensuales y anuales.\n"
            "- Preparar estados financieros bajo NIIF/IFRS.\n"
            "- Asesorar en planificación fiscal y optimización tributaria.\n"
            "- Coordinar auditorías internas y externas.\n\n"
            "REQUISITOS:\n"
            "- Título de Contador Público (CPN) expedido por UdelaR u homologado.\n"
            "- Mínimo 5 años de experiencia en estudio contable o empresa.\n"
            "- Manejo avanzado de Excel y software contable (SAFI, Defontana o similar).\n"
            "- Conocimiento actualizado de normativa DGI y BPS.\n\n"
            "SE VALORA:\n"
            "- Experiencia en auditoría bajo NIIF.\n"
            "- Inglés contable.\n"
            "- Posgrado en tributación."
        ),
    },
    "JD_005": {
        "titulo":       "Ingeniero/a de Software Senior",
        "empresa":      "NovaSys Engineering",
        "skills_req":   ["arquitectura de software", "microservicios", "cloud AWS/GCP",
                         "Python o Java", "CI/CD", "Kubernetes", "diseño de sistemas",
                         "liderazgo técnico"],
        "min_exp":      5,
        "min_edu":      "Bachelors",
        "descripcion":  (
            "NovaSys Engineering busca un/a Ingeniero/a de Software Senior para liderar el "
            "diseño e implementación de sistemas distribuidos en proyectos de alto impacto.\n\n"
            "RESPONSABILIDADES:\n"
            "- Diseñar arquitecturas escalables de microservicios en cloud (AWS o GCP).\n"
            "- Liderar técnicamente equipos de 4-6 desarrolladores.\n"
            "- Implementar pipelines CI/CD y prácticas de DevOps.\n"
            "- Realizar revisiones de arquitectura y code reviews.\n"
            "- Colaborar con Product Managers en la definición técnica de funcionalidades.\n\n"
            "REQUISITOS:\n"
            "- Ingeniería en Sistemas, Computación o afín (Licenciatura mínimo).\n"
            "- Mínimo 5 años de experiencia en desarrollo de software.\n"
            "- Experiencia con arquitecturas de microservicios y cloud (AWS o GCP).\n"
            "- Dominio de Python o Java y herramientas DevOps (Docker, Kubernetes, CI/CD).\n\n"
            "SE VALORA:\n"
            "- Certificaciones cloud (AWS Solutions Architect, GCP Professional).\n"
            "- Experiencia en sistemas de alta disponibilidad.\n"
            "- Inglés avanzado."
        ),
    },
}

# ── Pools de habilidades por dominio ──────────────────────────────────────────

SKILLS_POR_DOMINIO = {
    "datos":     ["Python", "SQL", "Power BI", "Tableau", "pandas", "numpy",
                  "machine learning", "estadística", "Excel avanzado", "R",
                  "scikit-learn", "visualización de datos", "ETL", "BigQuery",
                  "análisis estadístico", "redes neuronales"],
    "backend":   ["Python", "Django", "FastAPI", "Flask", "PostgreSQL", "MySQL",
                  "Docker", "Git", "APIs REST", "microservicios", "Redis",
                  "Celery", "GraphQL", "AWS", "GCP", "Kubernetes", "CI/CD",
                  "testing unitario", "arquitectura de software"],
    "rrhh":      ["reclutamiento", "selección de personal", "entrevistas por competencias",
                  "evaluación de desempeño", "gestión de nóminas", "derecho laboral",
                  "onboarding", "clima organizacional", "SAP HR", "Workday",
                  "desarrollo organizacional", "formación y capacitación",
                  "gestión del cambio", "descripción de puestos"],
    "contabilidad": ["contabilidad general", "impuestos Uruguay", "DGI", "BPS",
                     "auditoría", "Excel avanzado", "NIIF/IFRS", "cierre contable",
                     "SAFI", "Defontana", "SAP FI", "planificación fiscal",
                     "estados financieros", "tesorería", "presupuestación"],
    "software":  ["arquitectura de software", "microservicios", "AWS", "GCP",
                  "Python", "Java", "Kubernetes", "CI/CD", "Docker",
                  "diseño de sistemas", "liderazgo técnico", "patrones de diseño",
                  "DevOps", "Terraform", "event-driven architecture", "DDD"],
    "otro":      ["atención al cliente", "ventas", "marketing digital", "logística",
                  "gestión de proyectos", "SCRUM", "comunicación", "diseño gráfico",
                  "fotografía", "gastronomía", "enfermería", "docencia",
                  "administración general", "secretariado"],
}

DOMINIO_POR_JD = {
    "JD_001": "datos",
    "JD_002": "backend",
    "JD_003": "rrhh",
    "JD_004": "contabilidad",
    "JD_005": "software",
}

TITULOS_APTO = {
    "JD_001": ["Licenciatura en Sistemas", "Licenciatura en Estadística",
               "Ingeniería en Computación", "Licenciatura en Matemática",
               "Ingeniería en Sistemas"],
    "JD_002": ["Ingeniería en Computación", "Licenciatura en Sistemas",
               "Ingeniería en Software", "Tecnólogo en Informática"],
    "JD_003": ["Licenciatura en Psicología", "Licenciatura en Relaciones Laborales",
               "Licenciatura en Administración de Empresas", "Tecnicatura en RR.HH."],
    "JD_004": ["Contador Público (CPN)", "Licenciatura en Contabilidad"],
    "JD_005": ["Ingeniería en Computación", "Ingeniería en Sistemas",
               "Licenciatura en Ciencias de la Computación"],
}

TITULOS_NOAP = [
    "Licenciatura en Comunicación", "Tecnicatura en Diseño Gráfico",
    "Bachillerato Tecnológico", "Licenciatura en Turismo",
    "Tecnicatura en Administración", "Bachillerato en Humanidades",
    "Licenciatura en Ciencias Sociales", "Curso de Fotografía Profesional",
]

ROLES_PREVIOS_APTO = {
    "JD_001": ["Analista de Datos Jr.", "Data Analyst", "Analista de Business Intelligence",
               "Especialista en Reportería", "Data Engineer Jr."],
    "JD_002": ["Desarrollador Python", "Backend Developer", "Desarrollador Full Stack",
               "Ingeniero de Software", "Programador Senior"],
    "JD_003": ["Analista de RR.HH.", "Reclutador/a", "Generalista de RR.HH.",
               "Coordinador/a de Selección", "Business Partner de Personas"],
    "JD_004": ["Contador/a Jr.", "Auxiliar Contable Sr.", "Analista Contable",
               "Asesor/a Tributario", "Contador/a Público"],
    "JD_005": ["Ingeniero/a de Software Sr.", "Tech Lead", "Arquitecto/a de Software",
               "Desarrollador/a Senior", "Engineering Manager"],
}

ROLES_PREVIOS_NOAP = [
    "Encargado/a de Depósito", "Vendedor/a", "Atención al Cliente",
    "Cocinero/a", "Recepcionista", "Auxiliar Administrativo/a",
    "Operario/a de Producción", "Chofer de Reparto", "Community Manager Jr.",
    "Profesor/a de Inglés", "Técnico/a en Refrigeración",
]


# ── Funciones de generación ───────────────────────────────────────────────────

def gen_personal_info(gender: str, age: int, rng: random.Random) -> dict:
    """Genera datos personales con PII para un candidato."""
    nombre = rng.choice(NOMBRES_F if gender == "F" else NOMBRES_M)
    apellido1 = rng.choice(APELLIDOS)
    apellido2 = rng.choice(APELLIDOS)
    nombre_completo = f"{nombre} {apellido1} {apellido2}"

    # Email derivado del nombre (PII detectada por Presidio)
    email_local = (
        nombre.split()[0].lower() + "." +
        apellido1.lower() +
        str(rng.randint(1, 99))
    )
    dominios = ["gmail.com", "hotmail.com", "outlook.com", "yahoo.com", "ort.edu.uy"]
    email = f"{email_local}@{rng.choice(dominios)}"

    # Teléfono UY (09X XXX XXX — también incluimos formato +34 para que lo detecte el recognizer)
    # Usamos formato español para compatibilidad con EsPhoneRecognizer actual
    telefono = f"+34 6{rng.randint(10,99)} {rng.randint(100,999)} {rng.randint(100,999)}"

    # Dirección Montevideo
    calle = rng.choice(CALLES_MVD)
    numero = rng.randint(800, 3500)
    apto = rng.randint(1, 20) if rng.random() > 0.5 else None
    barrio = rng.choice(BARRIOS_MVD)
    direccion = f"{calle} {numero}" + (f", Apto. {apto}" if apto else "") + f", {barrio}, Montevideo"

    return {
        "nombre":    nombre_completo,
        "email":     email,
        "telefono":  telefono,
        "direccion": direccion,
        "edad":      age,
    }


def gen_cv_text(personal: dict, jd_id: str, label: str, rng: random.Random) -> tuple[str, int, int]:
    """
    Genera texto libre de CV en español rioplatense.

    Returns:
        (texto_cv, years_exp, relevant_skills_count)
    """
    dominio = DOMINIO_POR_JD[jd_id]
    jd      = JDS[jd_id]
    skills_req = jd["skills_req"]
    min_exp    = jd["min_exp"]

    if label == "APTO":
        # Experiencia suficiente
        years_exp = rng.randint(min_exp, min(min_exp + 8, 15))

        # Skills: mayoría relevantes
        n_relevant   = rng.randint(max(4, len(skills_req) - 2), len(skills_req))
        skills_sel   = rng.sample(skills_req, n_relevant)
        extra_skills = rng.sample(SKILLS_POR_DOMINIO[dominio], rng.randint(1, 3))
        all_skills   = list(dict.fromkeys(skills_sel + extra_skills))

        # Formación
        titulo    = rng.choice(TITULOS_APTO[jd_id])
        univ      = rng.choice(UNIVERSIDADES_UY)
        year_grad = personal["edad"] - rng.randint(3, 8)

        # Experiencia laboral: 2-3 roles previos relevantes
        roles_pool = ROLES_PREVIOS_APTO[jd_id]
        n_roles    = rng.randint(2, 3)
        roles      = rng.sample(roles_pool * 2, n_roles)  # puede repetir pool
        empresas_sel = rng.sample(EMPRESAS_UY, n_roles)

        # Certificaciones con 60% de probabilidad
        tiene_cert = rng.random() < 0.6
        certs_pool = {
            "datos":        ["Google Data Analytics", "Microsoft Power BI", "IBM Data Science"],
            "backend":      ["AWS Certified Developer", "Docker Certified Associate", "Python Institute PCEP"],
            "rrhh":         ["SHRM-CP", "DDI Certified Interviewer", "Coaching Ontológico"],
            "contabilidad": ["NIIF para PyMEs", "DGI Tributación Avanzada", "CPA"],
            "software":     ["AWS Solutions Architect", "GCP Professional", "Kubernetes CKAD"],
        }
        cert_text = ""
        if tiene_cert:
            cert = rng.choice(certs_pool.get(dominio, ["Certificación profesional"]))
            cert_text = f"\nCERTIFICACIONES:\n- {cert} ({rng.randint(2019, 2024)})\n"

    else:  # NO_APTO
        # Tres tipos de NO_APTO
        tipo = rng.choice(["sin_exp", "campo_errado", "educacion"])

        if tipo == "sin_exp":
            years_exp  = rng.randint(0, min_exp - 1)
            n_relevant = rng.randint(1, 3)
            skills_sel = rng.sample(skills_req, min(n_relevant, len(skills_req)))
            extra      = rng.sample(SKILLS_POR_DOMINIO["otro"], rng.randint(1, 3))
            all_skills = list(dict.fromkeys(skills_sel + extra))
            titulo     = rng.choice(TITULOS_APTO[jd_id])  # buena educación, poca exp
        elif tipo == "campo_errado":
            years_exp  = rng.randint(3, 12)
            n_relevant = rng.randint(0, 2)
            skills_sel = rng.sample(skills_req, min(n_relevant, len(skills_req)))
            dominio_alt = rng.choice([d for d in SKILLS_POR_DOMINIO if d != dominio and d != "otro"])
            extra       = rng.sample(SKILLS_POR_DOMINIO[dominio_alt], rng.randint(3, 5))
            all_skills  = list(dict.fromkeys(skills_sel + extra))
            titulo      = rng.choice(TITULOS_NOAP)
        else:  # educacion
            years_exp  = rng.randint(1, min_exp)
            n_relevant = rng.randint(1, 3)
            skills_sel = rng.sample(skills_req, min(n_relevant, len(skills_req)))
            extra       = rng.sample(SKILLS_POR_DOMINIO["otro"], rng.randint(2, 4))
            all_skills  = list(dict.fromkeys(skills_sel + extra))
            titulo      = "Bachillerato Tecnológico"

        univ      = rng.choice(UNIVERSIDADES_UY + ["Bachillerato", "Liceo N°12 de Montevideo"])
        year_grad = personal["edad"] - rng.randint(2, 10)

        n_roles      = rng.randint(1, 2)
        roles        = [rng.choice(ROLES_PREVIOS_NOAP) for _ in range(n_roles)]
        empresas_sel = rng.sample(EMPRESAS_UY, min(n_roles, len(EMPRESAS_UY)))
        cert_text    = ""
        tiene_cert   = False

    # ── Armar texto del CV ────────────────────────────────────────────────────
    skills_str = " · ".join(all_skills)

    # Resumen profesional
    if label == "APTO":
        resumen = (
            f"Profesional con {years_exp} años de experiencia en {jd['titulo'].lower()}. "
            f"Titulado/a en {titulo} con sólida formación técnica y experiencia comprobable "
            f"en entornos corporativos. Orientado/a a resultados y al trabajo en equipo."
        )
    else:
        if years_exp < min_exp:
            resumen = (
                f"Egresado/a reciente con {years_exp} año{'s' if years_exp != 1 else ''} "
                f"de experiencia laboral. En búsqueda de primera oportunidad estable. "
                f"Proactivo/a y con disposición para aprender."
            )
        else:
            resumen = (
                f"Profesional con {years_exp} años de trayectoria en el mercado laboral uruguayo. "
                f"Experiencia en diversas áreas organizacionales. Flexible y adaptable a nuevos entornos."
            )

    # Sección de experiencia
    exp_lines = []
    years_left = years_exp
    for i, (rol, emp) in enumerate(zip(roles, empresas_sel)):
        dur = min(rng.randint(1, 4), years_left)
        if dur == 0:
            dur = 1
        years_left = max(0, years_left - dur)
        year_fin = 2024 - sum([rng.randint(1, 3) for _ in range(i)])
        year_ini = year_fin - dur
        exp_lines.append(f"- {rol} | {emp} ({year_ini}–{year_fin if i > 0 else 'Actualidad'})")
        if label == "APTO":
            tarea = rng.choice([
                f"Responsable de {rng.choice(skills_req).lower()} y generación de reportes.",
                f"Desarrollo e implementación de soluciones con {rng.choice(all_skills)}.",
                f"Coordinación con equipos multidisciplinarios y presentación de resultados.",
                f"Optimización de procesos mediante {rng.choice(all_skills)}.",
            ])
        else:
            tarea = rng.choice([
                "Gestión de tareas administrativas y atención a clientes internos.",
                "Soporte operativo al equipo y seguimiento de indicadores.",
                "Colaboración en proyectos transversales de la organización.",
            ])
        exp_lines.append(f"  {tarea}")

    cv_text = f"""{personal['nombre']}
{personal['email']} | Tel.: {personal['telefono']}
{personal['direccion']}

RESUMEN PROFESIONAL:
{resumen}

EXPERIENCIA LABORAL ({years_exp} años):
{chr(10).join(exp_lines)}

FORMACIÓN ACADÉMICA:
- {titulo} — {univ} ({year_grad})
{cert_text}
HABILIDADES TÉCNICAS:
{skills_str}
"""
    return cv_text.strip(), years_exp, len([s for s in all_skills if s in skills_req])


def compute_gold_standard_score(years_exp: int, relevant_skills: int,
                                 total_req: int, education: str,
                                 has_cert: bool) -> int:
    """
    Función de puntuación Gold Standard (documentada en sección 5.9 del TFE).

    Score = experiencia(0-50) + skills(0-30) + educación(0-15) + certificaciones(0-5)
    APTO si Score >= 60
    """
    exp_score  = min(years_exp / 10.0, 1.0) * 50
    ski_score  = (relevant_skills / max(total_req, 1)) * 30
    edu_scores = {"Bachillerato": 0, "High School": 0, "Tecnicatura": 5,
                  "Bachelors": 10, "Masters": 13, "PhD": 15}
    edu_score  = next((v for k, v in edu_scores.items() if k in education), 10)
    cert_score = 5 if has_cert else 0
    return round(exp_score + ski_score + edu_score + cert_score)


def simulate_c0_time(label: str, rng: random.Random) -> float:
    """
    Simula el tiempo de screening manual (C0) en segundos.

    Los evaluadores RRHH tardan entre 5 y 20 minutos por CV según complejidad.
    Los NO_APTO se descartan más rápido (5-10 min).
    """
    if label == "APTO":
        return round(rng.uniform(600, 1200), 1)   # 10-20 minutos
    else:
        return round(rng.uniform(300, 700), 1)    # 5-12 minutos


# ── Generación principal ──────────────────────────────────────────────────────

def generate_corpus() -> None:
    """
    Genera el corpus completo de 300 CVs, 5 JDs y archivos Gold Standard.
    """
    ensure_dirs()
    rng = random.Random(RANDOM_SEED)

    ground_truth_rows = []
    c0_times_rows     = []
    cv_counter        = 1

    # ── Guardar JDs ──────────────────────────────────────────────────────────
    print("Guardando Job Descriptions...")
    for jd_id, jd_data in JDS.items():
        jd_path = JOB_DESCRIPTIONS / f"{jd_id}.txt"
        jd_text = (
            f"CARGO: {jd_data['titulo']}\n"
            f"EMPRESA: {jd_data['empresa']}\n\n"
            f"{jd_data['descripcion']}"
        )
        jd_path.write_text(jd_text, encoding="utf-8")
        print(f"  → {jd_path.name}")

    # ── Generar CVs ──────────────────────────────────────────────────────────
    print(f"\nGenerando {N_TOTAL} CVs sintéticos...")

    for jd_id in JDS:
        jd = JDS[jd_id]
        n_skills_req = len(jd["skills_req"])
        evaluadores = [f"EVAL_{i:02d}" for i in range(1, 4)]

        # 30 APTO + 30 NO_APTO, alternando género M/F
        for label in ["APTO", "NO_APTO"]:
            n_per_label = N_APTO_PER_JD if label == "APTO" else N_NOAP_PER_JD

            for i in range(n_per_label):
                cv_id  = f"CV_{cv_counter:03d}"
                gender = "F" if i % 2 == 0 else "M"

                # Grupo etario: distribuido uniformemente
                age_group_idx = i % 3
                age_ranges = [(23, 35), (36, 45), (46, 58)]
                age_min, age_max = age_ranges[age_group_idx]
                age = rng.randint(age_min, age_max)
                group_age = f"{age_min}-{age_max}"

                # Datos personales
                personal = gen_personal_info(gender, age, rng)

                # Texto del CV
                cv_text, years_exp, relevant_skills = gen_cv_text(
                    personal, jd_id, label, rng
                )

                # Score Gold Standard
                education_detected = jd["skills_req"][0]  # proxy para simplificar
                has_cert = "CERTIFICACIONES:" in cv_text
                gs_score = compute_gold_standard_score(
                    years_exp, relevant_skills, n_skills_req,
                    jd["min_edu"], has_cert
                )

                # Guardar CV
                cv_path = CVS_RAW / f"{cv_id}.txt"
                cv_path.write_text(cv_text, encoding="utf-8")

                # Ground truth
                ground_truth_rows.append({
                    "cv_id":          cv_id,
                    "jd_id":          jd_id,
                    "expected_label": label,
                    "expected_score": gs_score,
                    "group_gender":   gender,
                    "group_age":      group_age,
                })

                # Tiempo C0
                t = simulate_c0_time(label, rng)
                c0_times_rows.append({
                    "cv_id":        cv_id,
                    "jd_id":        jd_id,
                    "time_seconds": t,
                    "decision":     label,
                    "evaluator_id": rng.choice(evaluadores),
                })

                cv_counter += 1

        print(f"  [{jd_id}] {jd['titulo']}: 60 CVs generados (30 APTO + 30 NO_APTO)")

    # ── Guardar Ground Truth ──────────────────────────────────────────────────
    gt_path = GOLD_STANDARD_DIR / "ground_truth.csv"
    gt_fields = ["cv_id", "jd_id", "expected_label", "expected_score",
                 "group_gender", "group_age"]
    with open(gt_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=gt_fields)
        writer.writeheader()
        writer.writerows(ground_truth_rows)
    print(f"\n  → {gt_path} ({len(ground_truth_rows)} filas)")

    # ── Guardar Tiempos C0 ────────────────────────────────────────────────────
    c0_path = GOLD_STANDARD_DIR / "c0_times.csv"
    c0_fields = ["cv_id", "jd_id", "time_seconds", "decision", "evaluator_id"]
    with open(c0_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=c0_fields)
        writer.writeheader()
        writer.writerows(c0_times_rows)
    print(f"  → {c0_path} ({len(c0_times_rows)} filas)")

    # ── Resumen ───────────────────────────────────────────────────────────────
    apto_total = sum(1 for r in ground_truth_rows if r["expected_label"] == "APTO")
    noap_total = sum(1 for r in ground_truth_rows if r["expected_label"] == "NO_APTO")
    f_total    = sum(1 for r in ground_truth_rows if r["group_gender"] == "F")
    m_total    = sum(1 for r in ground_truth_rows if r["group_gender"] == "M")
    t_c0_mean  = sum(r["time_seconds"] for r in c0_times_rows) / len(c0_times_rows)

    print(f"""
{'='*55}
CORPUS GENERADO — SISTAC
{'='*55}
  CVs totales:     {cv_counter - 1}
  APTO:            {apto_total} ({apto_total*100//(cv_counter-1)}%)
  NO_APTO:         {noap_total} ({noap_total*100//(cv_counter-1)}%)
  Género F:        {f_total} ({f_total*100//(cv_counter-1)}%)
  Género M:        {m_total} ({m_total*100//(cv_counter-1)}%)
  JDs generadas:   {len(JDS)}
  T_cand C0 prom:  {t_c0_mean:.0f}s ({t_c0_mean/60:.1f} min)
  Seed:            {RANDOM_SEED}
{'='*55}
Outputs:
  data/raw/cvs/            → {cv_counter-1} archivos .txt
  data/raw/job_descriptions/ → {len(JDS)} archivos .txt
  data/raw/gold_standard/ground_truth.csv
  data/raw/gold_standard/c0_times.csv
{'='*55}
""")


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("SISTAC — Generador de Corpus Sintético")
    print(f"Seed: {RANDOM_SEED} | CVs: {N_TOTAL} | JDs: {N_JDS}\n")
    generate_corpus()
    print("Listo. Corpus disponible para el pipeline RAG.")
