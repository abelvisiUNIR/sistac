# Guía de Integración de Ajustes Metodológicos y Capturas (Capítulos 4 y 6)

Esta guía detalla los cambios necesarios en los **Capítulos 4 y 6** de tu documento Word (`Talento sin nombre...docx`) para unificar la metodología del piloto de 25 CVs cronometrados y resolver las dudas de maquetación de las capturas de pantalla de la aplicación.

---

## 1. Modificación en el Capítulo 4 (Estrategia de datos — Sección 4.2.2)

Busca en tu Word el párrafo central de la sección **4.2.2** (originalmente el párrafo que empieza por *"Las variables demográficas no presentes..."*, que corresponde al Párrafo 400 del análisis) y reemplázalo por el siguiente texto para detallar el diseño mixto de tiempos:

```text
Las variables demográficas no presentes en el conjunto original se imputan de forma controlada para habilitar el análisis de equidad algorítmica. El rango de edad se distribuye de manera balanceada entre tres categorías (de veintitrés a treinta y cinco, de treinta y seis a cuarenta y cinco, y de cuarenta y seis a cincuenta y ocho años). Los tiempos de cribado manual en C0 fueron capturados mediante un diseño mixto: una submuestra piloto de 25 currículums fue evaluada directamente en la aplicación web por los expertos registrando sus tiempos de lectura individuales en tiempo real mediante el cronómetro integrado; para los 125 casos restantes, los tiempos fueron imputados mediante distribuciones uniformes (entre 600 y 1200 segundos para perfiles APTO, y entre 300 y 700 segundos para perfiles NO_APTO) calibradas a partir de la media y rangos empíricos registrados en dicha muestra piloto. La naturaleza inferida del género y la naturaleza imputada de la edad y de los tiempos de control constituyen limitaciones del estudio que se analizan en la sección de discusión.
```

---

## 2. Modificación en el Capítulo 6 (Limitaciones del estudio — Sección 6.1.4)

Busca en tu Word la sección **6.1.4. Limitaciones del estudio**, específicamente el apartado sobre **Imputación de tiempos en la línea base (C0)** (originalmente el párrafo que empieza por *"Imputación de tiempos en la línea base..."*, correspondiente al Párrafo 737 del análisis) y reemplázalo por el siguiente texto para reflejar la validez física del piloto de 25 CVs:

```text
Imputación de tiempos en la línea base (C0): Si bien los tiempos de la condición C0 para la totalidad del corpus se estimaron mediante imputación estadística para evitar sobrecargar al panel durante 25 horas operativas, dicha imputación no se basó en supuestos arbitrarios, sino que fue calibrada a partir de los tiempos de lectura individuales reales cronometrados mediante el módulo integrado en la aplicación sobre una muestra piloto de 25 currículums. De este modo, aunque el speedup del estudio general incluye un componente de simulación a escala, los parámetros de base provienen de mediciones de productividad física reales sobre la interfaz de trabajo.
```

---

## 3. Recomendación de Ubicación de las Capturas de la Aplicación

**¿Es mejor ponerlas en el cuerpo del documento o en el Anexo C?**

**Respuesta académica y recomendada:** **Es mucho mejor colocarlas en el Anexo C.**

### Justificación Metodológica:
1. **Limpieza y Flujo del Texto:** Incluir capturas de interfaces de usuario (como el login, el simulador de candidatos o el panel de control) en medio de los capítulos teóricos o de resultados (Capítulo 4 o 5) interrumpe la lectura formal y le resta un tono puramente científico al texto de la tesis.
2. **Rol del Anexo C:** Tu tesis ya tiene estructurado e indexado el apartado **Anexo C. Pantallas de la aplicación** en la página 86. El propósito académico exacto de este anexo es albergar este tipo de evidencias visuales sin sobrecargar la memoria técnica del trabajo.
3. **Cómo referenciarlas desde el cuerpo:** En lugar de poner la imagen en medio del Capítulo 4 o 5, simplemente coloca referencias breves en el texto. Por ejemplo:
   * *En la sección del módulo de anonimización (Capítulo 4):* "...La interfaz gráfica del simulador de candidatos y el cronómetro de análisis del panel de expertos se detallan visualmente en las capturas del Anexo C."
   * *En la sección de resultados (Capítulo 5):* "...como se observa en el panel de métricas de la interfaz de administración (ver Anexo C)."
