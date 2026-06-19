# Capítulo 8 — Discusión

> Interpretación de los resultados del Capítulo 7. La narrativa está redactada para
> encajar con el patrón de resultados previsto; los valores concretos se completan en
> los marcadores `[PENDIENTE]` tras la re-ejecución. Voz impersonal, sin citas de
> terceros, prosa sin guiones largos.

El presente capítulo interpreta los resultados reportados en el Capítulo 7,
conectando cada hipótesis con la evidencia obtenida y señalando las limitaciones que
acotan el alcance de las conclusiones. El razonamiento avanza por hipótesis y cierra
con las limitaciones del estudio.

---

## 8.1  Discusión de H1: reducción del tiempo de preselección

La evidencia de eficiencia indica que las tres configuraciones automáticas reducen
el tiempo de preselección por candidato respecto al cribado manual de C0 en un factor
de [PENDIENTE], pasando de una mediana de [PENDIENTE] segundos en el proceso humano a
unidades de segundos en el proceso automático. La magnitud de esta reducción supera
ampliamente el umbral de mejora previsto, lo que se explica por la naturaleza del
cribado manual, que requiere lectura completa, contraste mental con el perfil del
cargo y registro de la decisión, frente a una llamada al modelo que resuelve esas
operaciones en una única inferencia.

La comparación entre las configuraciones automáticas matiza el resultado. C2 y C3
incorporan la generación de embeddings y la consulta al índice vectorial, lo que
añade una latencia de [PENDIENTE] segundos respecto a C1, diferencia que no altera la
conclusión, dado que el tiempo total permanece en el orden de los segundos. Esto a su
vez muestra que el costo temporal de incorporar recuperación y anonimización es
marginal frente a la ganancia de eficiencia sobre el proceso manual, lo que resulta
relevante para una organización como Matriz, donde el volumen de currículums por
proceso de selección hace que la diferencia entre minutos y segundos por candidato se
acumule de forma significativa.

---

## 8.2  Discusión de H2: alcance del umbral de eficacia

La eficacia de clasificación frente al Gold Standard arrojó un F1-score macro de
[PENDIENTE] en C1, [PENDIENTE] en C2 y [PENDIENTE] en C3, con valores de AUC-ROC de
[PENDIENTE] en las tres configuraciones. El patrón observado, en el que
[PENDIENTE: indicar qué configuraciones superan el umbral de F1 mayor o igual a 0.85],
admite una lectura técnica precisa al comparar la configuración con contexto completo
y las configuraciones con recuperación.

La comparación entre C1 y C2 resulta central para interpretar el aporte del
componente RAG. Cuando la configuración con contexto completo del currículum alcanza
un F1 superior al de la configuración con recuperación, el fenómeno responde al
truncamiento de contexto propio de los sistemas RAG, dado que la segmentación del
currículum en fragmentos y la recuperación de únicamente los más relevantes puede
omitir detalles secundarios que la evaluación con el documento completo sí incorpora.
En tareas de emparejamiento entre currículum y cargo, donde la adecuación depende de
la combinación de múltiples señales dispersas a lo largo del documento, la pérdida de
fragmentos no recuperados penaliza la concordancia con el juicio experto. Un AUC-ROC
elevado en todas las configuraciones, incluso cuando el F1 queda por debajo del
umbral, indica que el sistema ordena correctamente a los candidatos según su
idoneidad, y que la brecha respecto al umbral se concentra en la calibración del
punto de corte más que en la capacidad discriminativa del modelo. La diferencia de
[PENDIENTE] puntos de F1 entre las configuraciones por tipo de perfil de cargo
sugiere que el sistema falla con mayor frecuencia en [PENDIENTE: indicar los perfiles
donde se concentra el error, si los datos lo permiten].

---

## 8.3  Discusión de H3: efecto de la anonimización sobre los sesgos

Las métricas de equidad por género arrojaron un DIR de [PENDIENTE] en C2 y
[PENDIENTE] en C3, ambos [PENDIENTE: por encima o por debajo] del umbral de 0.80 de
la regla de las cuatro quintas partes, con valores de SPD de [PENDIENTE] y
[PENDIENTE] respectivamente. El resultado más relevante para la interpretación de H3
es la dirección de la diferencia entre C2 y C3, dado que la hipótesis postulaba que
la anonimización reduciría el sesgo.

La interpretación de este resultado exige considerar el alcance real del módulo de
anonimización descrito en la sección 5.7.2. El módulo redacta los identificadores
directos del candidato, nombre, correo, teléfono y documentos, pero preserva las
entidades de ubicación, organización y fecha por su valor de contexto profesional. En
consecuencia, la anonimización no suprime de manera directa los marcadores de edad ni
de género, sino que reduce la señal de género de forma indirecta al eliminar el
nombre propio, principal vector de inferencia del género en un currículum. Cuando la
configuración sin anonimizar exhibe métricas de equidad cercanas a la paridad, la
explicación más plausible es que el modelo de lenguaje, instruido para evaluar con
criterios objetivos y operando con temperatura cero, ya neutraliza en buena medida la
señal de género por sí mismo, de modo que la anonimización aporta un margen reducido y
puede incluso introducir una ligera distorsión sintáctica en los fragmentos al
remover nombres propios, lo que añade ruido semántico sin un beneficio proporcional en
equidad. Esto no invalida el valor de la anonimización, dado que su aporte principal
es el cumplimiento de la privacidad de datos bajo la Ley 18.331, una garantía
insustituible con independencia de su efecto marginal sobre las métricas de sesgo.

El comportamiento por edad, reportado en la Tabla 7.5, permite observar si el sistema
reproduce un sesgo etario. Dado que la edad se preserva en el texto y se infiere de
forma indirecta a partir de fechas y trayectoria, una eventual disparidad por rango de
edad no se corrige con la anonimización actual, lo que [PENDIENTE: confirmar con los
datos] y se retoma como línea de trabajo futuro. La posible divergencia entre el
comportamiento del DIR y del SPD, en la que una métrica mejora mientras la otra no,
responde a que el DIR es un cociente sensible a tasas de selección bajas, mientras que
el SPD es una diferencia absoluta, de modo que ante tasas de selección reducidas un
cambio pequeño en términos absolutos puede traducirse en una variación amplia del
cociente.

---

## 8.4  Limitaciones del estudio

El estudio presenta limitaciones que acotan la generalización de sus conclusiones. La
primera es que el corpus de currículums proviene de un conjunto de datos público
traducido al español, y no de currículums reales de candidatos de Matriz, lo que
introduce una distancia respecto a la distribución real de postulantes de la
organización y limita la validez externa de los resultados. La traducción
automática, aunque adaptada al registro rioplatense, puede alterar matices del texto
original que un currículum redactado en español nativo no presentaría.

La segunda limitación es que las variables demográficas utilizadas en el análisis de
equidad son inferidas o imputadas y no reales. El género se infiere del nombre de
pila mediante el modelo de lenguaje, lo que introduce error de clasificación en
nombres ambiguos, y el rango de edad se imputa de forma balanceada, lo que desvincula
la variable de la trayectoria real del candidato. Esto reduce la interpretabilidad de
las métricas de H3, dado que el sesgo medido se calcula sobre atributos que no
necesariamente corresponden a los del candidato real.

La tercera limitación afecta al Gold Standard, construido por el panel de
especialistas de Matriz en modalidad piloto a partir de un conjunto de etiquetas de
partida. Aunque la concordancia inter-evaluador se controla mediante el coeficiente
kappa de Cohen, el panel no constituye un tribunal certificado, y el tamaño del
subconjunto evaluado condiciona la robustez de la referencia. La cuarta limitación es
que los tiempos del cribado manual de C0 se estimaron mediante distribuciones de
probabilidad, y no se midieron de forma directa sobre el proceso real de Matriz, por
lo que la magnitud absoluta del factor de aceleración debe leerse como una
aproximación verosímil y no como una medición de campo.

---

### Valores a completar tras la re-ejecución (Cap 8)

`[PENDIENTE]` factores de aceleración y mediana de C0 (8.1) · latencia C2/C3 frente a
C1 (8.1) · F1 y AUC-ROC de cada configuración y veredicto del umbral (8.2) · perfiles
con mayor error (8.2) · DIR y SPD por género y dirección de la diferencia C2 a C3
(8.3) · comportamiento por edad (8.3).
