# Capítulo 9 — Conclusiones

> Cierre del trabajo. Narrativa lista para ajustar con los valores reales tras la
> re-ejecución (marcadores `[PENDIENTE]`). Voz impersonal, sin citas de terceros,
> prosa sin guiones largos.

El presente capítulo cierra el trabajo respondiendo de forma directa a la pregunta de
investigación, sintetizando las conclusiones por hipótesis, enunciando las
contribuciones del proyecto y proponiendo líneas de trabajo futuro.

---

## 9.1  Respuesta a la pregunta de investigación

La pregunta de investigación indagaba por el efecto diferencial de cuatro
configuraciones de preselección de currículums, desde el cribado manual hasta un
sistema con recuperación aumentada y anonimización de datos personales, sobre la
eficacia, la eficiencia y la equidad, evaluadas contra un Gold Standard de expertos en
recursos humanos. La evidencia obtenida muestra que la incorporación de modelos de
lenguaje transforma de manera sustancial la eficiencia del proceso, reduciendo el
tiempo por candidato en un factor de [PENDIENTE], mientras que el efecto sobre la
eficacia y la equidad depende de la configuración específica. La configuración que
logró el mejor equilibrio entre las tres dimensiones fue [PENDIENTE: indicar
configuración], que combinó [PENDIENTE: resumir su perfil de F1, tiempo y DIR],
ofreciendo a Matriz una herramienta de cribado primario que acelera el proceso sin
comprometer la equidad por género respecto al umbral regulatorio.

---

## 9.2  Conclusiones por hipótesis

Respecto a la hipótesis H1, sobre eficiencia, la evidencia [PENDIENTE: confirma o
rechaza] que el sistema automático es significativamente más rápido que el cribado
manual, con una reducción del tiempo por candidato de [PENDIENTE] en la mejor
configuración y un p-valor de [PENDIENTE] en la prueba de Mann-Whitney, lo que
sustenta la conclusión sobre la ganancia de eficiencia.

Respecto a la hipótesis H2, sobre eficacia, la evidencia [PENDIENTE: confirma,
rechaza o rechaza parcialmente] que las configuraciones con recuperación alcanzan un
F1-score macro mayor o igual a 0.85 frente al Gold Standard. La configuración
[PENDIENTE] alcanzó el umbral con un F1 de [PENDIENTE], mientras que [PENDIENTE]
quedaron por debajo, manteniendo en todos los casos un AUC-ROC de [PENDIENTE] que
evidencia una capacidad discriminativa elevada.

Respecto a la hipótesis H3, sobre equidad, la evidencia [PENDIENTE: confirma o
rechaza] que la anonimización reduce significativamente el DIR y el SPD respecto a las
configuraciones sin anonimizar. El DIR por género se mantuvo en [PENDIENTE] en la
configuración anonimizada, [PENDIENTE: por encima o por debajo] del umbral de 0.80, y
la comparación con la configuración sin anonimizar mostró que [PENDIENTE: resumir la
dirección del efecto], lo que matiza el alcance de la anonimización como mecanismo de
mitigación de sesgo y confirma su valor principal como garantía de privacidad.

---

## 9.3  Contribuciones del trabajo

El trabajo aporta cuatro contribuciones concretas. La primera es un marco
experimental cuasi-experimental que compara de forma controlada cuatro
configuraciones de automatización del cribado curricular, aislando el efecto del
componente de recuperación y de la anonimización sobre la eficacia, la eficiencia y la
equidad. La segunda es un módulo de anonimización de datos personales integrado al
pipeline de recuperación, con reconocedores adaptados al contexto rioplatense, que
permite cumplir con la Ley 18.331 sin abandonar el entorno local de procesamiento. La
tercera es un protocolo de Gold Standard construido con el panel experto de Matriz a
partir de pares currículum y cargo, que ancla la evaluación en criterios
profesionales reales. La cuarta es evidencia empírica sobre el equilibrio entre
anonimización y eficacia en el contexto latinoamericano, un escenario poco
documentado en la literatura de sistemas de selección de talento asistidos por
inteligencia artificial.

---

## 9.4  Trabajo futuro

El trabajo abre varias líneas de continuación. La primera es la validación del
sistema con currículums reales de Matriz, una vez obtenidas las autorizaciones y
salvaguardas exigidas por la Ley 18.331, lo que reemplazaría el corpus público
traducido por datos de la población real de candidatos y elevaría la validez externa
de los resultados. La segunda es la extensión del corpus a perfiles de cargo no
cubiertos en el experimento, ampliando la variedad de áreas funcionales y de niveles
de seniority para evaluar la generalización del sistema. La tercera es la evaluación
de modelos de embeddings multilingües entrenados específicamente sobre el español
rioplatense, que podrían mejorar la calidad del retrieval y reducir el truncamiento de
contexto observado en las configuraciones con recuperación. La cuarta es la
incorporación de un módulo de explicabilidad que permita a los evaluadores de recursos
humanos auditar las decisiones del sistema, y la extensión de la anonimización a los
marcadores indirectos de edad y género, de modo que la configuración anonimizada
actúe también sobre las señales demográficas que el módulo actual preserva.

---

### Valores a completar tras la re-ejecución (Cap 9)

`[PENDIENTE]` factor de aceleración y mejor configuración (9.1) · veredicto y cifras
de H1, H2 y H3 (9.2). Las contribuciones (9.3) y el trabajo futuro (9.4) no dependen
de los valores del experimento.
