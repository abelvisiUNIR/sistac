# SISTAC — Arquitectura del Sistema, Contribuciones Técnicas y Diseño de Experimentos (TFE)

Este documento recopila las contribuciones arquitectónicas y de diseño de ingeniería de software desarrolladas para el Trabajo de Fin de Estudios (TFE) **SISTAC (Sistema Inteligente de Selección y Triaje de Aspirantes a Cargos)**. Está diseñado para ser incorporado directamente en la sección de **Metodología, Arquitectura de Software o Contribuciones** de la memoria de la tesis.

---

## 1. Arquitectura General del Sistema

SISTAC está diseñado bajo una arquitectura de microservicios contenerizada con Docker, combinando persistencia híbrida (relacional/documental y vectorial) y un pipeline RAG (Retrieval-Augmented Generation) para el soporte de decisiones en la selección de talento.

```mermaid
graph TD
    %% Frontend y Backend
    UI["Dashboard Web (Vanilla JS + Tailwind)"] <--> API["FastAPI Backend (Python)"]
    
    %% Persistencia
    API <--> DB[("MongoDB (Persistencia de Cargos e Historial)")]
    
    %% RAG Pipeline
    subgraph "Vector Store & RAG"
        AzureSearch[["Azure AI Search (Índice: sistac-cvs)"]]
        SemanticRanker["Azure Semantic Ranker (Reranker Nativo)"]
        AzureSearch --> SemanticRanker
    end
    
    %% LLMs
    subgraph "Modelos Fundacionales"
        LLM["API LLM (Claude 3.5 Haiku / GPT-4o-mini)"]
        Embedder["SentenceTransformer local (Multilingual-MPNet) / OpenAI Embeddings"]
    end

    %% Flujos de Datos
    API -- "CRUD y Resultados" --> DB
    API -- "1. Texto de Búsqueda (JD)" --> Embedder
    Embedder -- "2. Vector Query (768/1536 dims)" --> AzureSearch
    SemanticRanker -- "3. Contexto Relevante (Chunks)" --> API
    API -- "4. Prompt + Chunks + CV" --> LLM
    LLM -- "5. Decisión + Score + Justificación" --> API
```

### Componentes Clave:
1. **Frontend Interactivo:** Panel web de administración y monitoreo en Vanilla JavaScript y Tailwind CSS. Permite iniciar experimentos, gestionar cargos, simular candidatos con auditorías demográficas y visualizar gráficos de métricas.
2. **FastAPI Backend:** Microservicio en Python que expone endpoints REST, orquesta las ejecuciones en segundo plano (`BackgroundTasks`) y encapsula la lógica de negocio.
3. **MongoDB:** Base de datos documental para almacenar la parametrización de los cargos (descripciones de puestos) y el histórico de evaluaciones de candidatos, con un mecanismo de *fallback* automático en memoria.
4. **Azure AI Search (Vector Store):** Gestiona la búsqueda híbrida (palabras clave + vectores) y aplica reranking semántico nativo para recuperar los extractos de currículums más pertinentes.

---

## 2. Flujo de Ejecución del Experimento Factorial (C0 a C3)

El diseño experimental de la tesis valida tres hipótesis (Eficiencia, Eficacia y Equidad) comparando una línea base manual y tres sistemas automatizados.

```mermaid
flowchart TD
    Start(["Inicio de la Simulación (300 CVs)"]) --> LoadGT["Cargar Dataset de Evaluación (Ground Truth)"]
    LoadGT --> LoadC0["Cargar Tiempos Humanos (C0 — Baseline Manual)"]
    
    %% C1
    subgraph "C1 — LLM Puro"
        C1_Exec["Llamar LLM (CV completo + JD)"] --> C1_Res["Obtener Scores y Decisiones"]
    end
    
    %% C2
    subgraph "C2 — LLM + RAG"
        C2_Search["Buscar Chunks en Azure Search (sistac-cvs)"] --> C2_LLM["Llamar LLM (Contexto RAG + CV + JD)"]
        C2_LLM --> C2_Res["Obtener Scores y Decisiones"]
    end
    
    %% C3
    subgraph "C3 — LLM + RAG + PII"
        C3_Anon["SistacAnonymizer (Ocultar Datos Protegidos)"] --> C3_Search["Buscar Chunks Anonimizados en Azure"]
        C3_Search --> C3_LLM["Llamar LLM (Chunks PII-free + CV Anonimizado + JD)"]
        C3_LLM --> C3_Res["Obtener Scores y Decisiones"]
    end

    LoadC0 --> C1_Exec
    C1_Res --> C2_Search
    C2_Res --> C3_Anon
    
    %% Consolidación y Métricas
    C3_Res --> Metrics["Calcular Métricas de la Tesis"]
    
    subgraph "Análisis de Hipótesis"
        Metrics --> H1["H1 (Eficiencia): Speedup y Mann-Whitney U Test (C0 vs Cx)"]
        Metrics --> H2["H2 (Eficacia): F1-Macro, AUC-ROC e Intervalos de Confianza Bootstrap"]
        Metrics --> H3["H3 (Equidad): DIR (Disparate Impact Ratio) y SPD (Statistical Parity Difference)"]
    end
    
    H1 & H2 & H3 --> SaveFiles["Guardar Reportes en /app/paper/tables/ (.csv y .docx)"]
    SaveFiles --> End(["Fin del Experimento"])
```

---

## 3. Capa de Robustez y Resiliencia en Lote (Indexación y Caché)

Para mitigar los altos costos y la inestabilidad de las APIs comerciales en procesos por lotes extensos (Batch), se diseñó una capa de resiliencia con políticas de reintento y caché persistente a nivel de disco.

```mermaid
sequenceDiagram
    autonumber
    actor Recruiter as Reclutador (Web UI)
    participant API as FastAPI Backend
    participant Cache as Caché en Disco (eval_cache.json)
    participant Search as Azure AI Search
    participant LLM as Proveedor LLM (Claude/GPT)

    Recruiter->>API: Clic en "Correr Tesis"
    API->>Cache: Cargar caché de evaluaciones guardadas
    
    loop Por cada Candidato (CV ↔ JD)
        API->>Cache: ¿Existe clave '{config}_{cv_id}_{jd_id}'?
        alt Sí (Caché Hit)
            Cache-->>API: Retornar resultado guardado ($0 costo)
        else No (Caché Miss)
            API->>Search: Recuperar chunks semánticos (RAG)
            Note over API, Search: Reintentos con Backoff Exponencial (3x) si Azure falla
            Search-->>API: Chunks de texto
            
            API->>LLM: Solicitar análisis y score
            Note over API, LLM: Si el saldo se agota o falla el LLM, se guarda el avance hasta aquí
            LLM-->>API: Respuesta estructurada (Score, Decisión, Justificación)
            
            API->>Cache: Guardar resultado inmediatamente en eval_cache.json
        end
    end
    API-->>Recruiter: Mostrar métricas actualizadas en pantalla
```

### Características Técnicas de Robustez Implementadas:
* **Caché Persistente Integrada (`eval_cache.json`):** Almacena de inmediato cada evaluación exitosa en el volumen de Docker. Si la API se cae o se acaba el saldo a mitad del experimento, las evaluaciones completadas no se pierden y el reintento cuesta **$0 USD**.
* **Reintentos con Backoff Exponencial en Azure:** El cargador de Azure implementa un bucle de reintento (`try-except`) con retrasos incrementales (`2s`, `4s`, `8s`) ante códigos de error HTTP transitorios o limitaciones de capacidad.
* **Tolerancia a Fallos Unitarios:** Un error crítico en el embedding de un currículum o en la subida de un bloque no detiene la ejecución del lote principal; el error se registra como advertencia y el pipeline avanza con el siguiente candidato.

---

## 4. Propuesta: Arquitectura para Re-ranking Dinámico (Criterios Ad-hoc)

Para simular escenarios del mundo real donde el negocio requiere aplicar prioridades complementarias (como filtrar por países específicos o priorizar tecnologías secundarias) sobre la marcha, se propone el siguiente flujo de reordenamiento en dos etapas:

```mermaid
graph LR
    subgraph "Etapa 1: Recuperación Estándar (RAG)"
        CVs["Base de CVs"] --> RAG["Búsqueda Vectorial Híbrida"]
        RAG --> Top["Top N Candidatos (Ej: Top 20)"]
    end
    
    subgraph "Etapa 2: Re-Ranking Dinámico"
        Top --> Prompter["Prompt Builder"]
        Pref["Instrucciones Ad-hoc de la Vacante<br>(Ej: 'Residir en Uruguay')"] --> Prompter
        Prompter --> LLM_Ranker["LLM Scorer (Evaluación de Preferencias)"]
        LLM_Ranker --> FinalRanking["Ranking Ajustado Final (Scores Modificados)"]
    end
```

### Explicación del Proceso:
1. **Recuperación Semántica Primaria:** Se extraen los currículums que mejor cumplen la descripción técnica principal de la posición usando RAG estándar.
2. **Inyección de Criterios Ad-hoc:** El reclutador introduce requerimientos blandos o demográficos ("Me gustaría que fuese de Uruguay" o "Valoramos certificaciones Cloud").
3. **LLM Re-Ranking (Scoring Ajustado):** El Scorer analiza únicamente a los candidatos preseleccionados (Top N) e incrementa o penaliza su puntuación basándose en el cumplimiento de los nuevos criterios dinámicos. Esto evita re-indexar la base de datos y permite un razonamiento conceptual flexible.
