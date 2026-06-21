# Fórmulas y Métricas Estadísticas Aplicadas en SISTAC

Este documento recopila las fórmulas matemáticas y estadísticas empleadas en el framework de validación experimental de **SISTAC** para las hipótesis H1 (Eficiencia), H2 (Eficacia) y H3 (Equidad). Puedes copiar estas fórmulas directamente en tu memoria en Word (.docx) o editor de ecuaciones.

---

## 1. Hipótesis H1: Eficiencia

La hipótesis H1 evalúa la reducción en el tiempo de procesamiento por candidato ($T_{cand}$) al automatizar el proceso de cribado frente a la línea base manual ($C_0$).

### 1.1. Mediana del Tiempo ($\text{Mediana}(T)$)
Dado que los tiempos de procesamiento (especialmente el manual) no se distribuyen de forma normal y tienen alta asimetría positiva, la mediana es el estimador de tendencia central más robusto:

$$\text{Mediana}(T) = \begin{cases} 
T_{(n+1)/2} & \text{si } n \text{ es impar} \\
\frac{T_{(n/2)} + T_{(n/2 + 1)}}{2} & \text{si } n \text{ es par} 
\end{cases}$$

Donde $T$ es el vector ordenado de tiempos de procesamiento de los candidatos.

### 1.2. Rango Intercuartílico ($IQR$)
Mide la dispersión estadística de los tiempos de evaluación libre de la influencia de valores atípicos (outliers):

$$IQR = Q_3 - Q_1$$

Donde:
*   $Q_1$ (Primer Cuartil): Percentil 25 de la muestra.
*   $Q_3$ (Tercer Cuartil): Percentil 75 de la muestra.

### 1.3. Factor de Aceleración ($Speedup$)
Indica cuántas veces es más rápido el sistema automatizado ($C_x$) respecto a la evaluación manual ($C_0$):

$$\text{Speedup}(C_x) = \frac{\text{Mediana}(T_{C_0})}{\text{Mediana}(T_{C_x})}$$

### 1.4. Porcentaje de Reducción de Tiempo ($\% \Delta T$)
Representa la ganancia relativa en tiempo de procesamiento:

$$\% \Delta T = \left( 1 - \frac{\text{Mediana}(T_{C_x})}{\text{Mediana}(T_{C_0})} \right) \times 100\%$$

### 1.5. Prueba No Paramétrica U de Mann-Whitney (Unilateral)
Se aplica para determinar si los tiempos de evaluación automáticos son significativamente menores que los manuales. 

Dadas dos muestras de tamaños $n_1$ (sistema) y $n_2$ (humano), el estadístico $U$ se calcula como:

$$U = \min(U_1, U_2)$$

$$U_1 = R_1 - \frac{n_1(n_1 + 1)}{2}$$
$$U_2 = R_2 - \frac{n_2(n_2 + 1)}{2}$$

Donde $R_1$ y $R_2$ representan la suma de los rangos (ranks) asignados a los valores ordenados de ambas muestras combinadas.
La hipótesis nula y alternativa planteadas son:

$$H_0: \theta_{\text{sistema}} \ge \theta_{\text{manual}}$$
$$H_1: \theta_{\text{sistema}} < \theta_{\text{manual}}$$

Donde $\theta$ representa la mediana poblacional del tiempo por candidato. Se rechaza $H_0$ si el $p\text{-valor} < \alpha$ (con $\alpha = 0.05$).

---

## 2. Hipótesis H2: Eficacia Técnica

La hipótesis H2 mide la concordancia de las clasificaciones binarias y la ordenación continua del sistema frente al Gold Standard (criterio experto de recursos humanos).

### 2.1. Métricas de Clasificación Binaria
A partir de la matriz de confusión que define Verdaderos Positivos ($VP$), Falsos Positivos ($FP$), Verdaderos Negativos ($VN$) y Falsos Negativos ($FN$):

*   **Precisión ($Precision$):** Fracción de candidatos clasificados como APTOS que realmente lo son.
    $$P = \frac{VP}{VP + FP}$$

*   **Sensibilidad ($Recall$ o $Tasa\ de\ Verdaderos\ Positivos$):** Fracción de candidatos APTOS reales que el sistema logró recuperar.
    $$R = \frac{VP}{VP + FN}$$

*   **F1-Score:** Media armónica de la precisión y la sensibilidad.
    $$F1 = 2 \times \frac{P \times R}{P + R}$$

*   **F1-Score Macro ($F1_{\text{macro}}$):** Promedio no ponderado del F1 de ambas clases (APTO y NO_APTO). Es la métrica decisiva para evaluar eficacia bajo desbalances de clase:
    $$F1_{\text{macro}} = \frac{F1_{\text{APTO}} + F1_{\text{NO\_APTO}}}{2}$$

### 2.2. Área bajo la Curva ROC ($AUC\text{-}ROC$)
Mide la probabilidad de que el sistema asigne un score de adecuación más alto a un candidato APTO elegido al azar que a un candidato NO_APTO elegido al azar.

$$AUC\text{-}ROC = \int_{0}^{1} TPR(FPR)\ d(FPR)$$

Donde:
*   $TPR$ (True Positive Rate): Sensibilidad.
*   $FPR$ (False Positive Rate): $\frac{FP}{FP + VN}$.

### 2.3. Intervalo de Confianza Bootstrap para AUC-ROC
Para evaluar la estabilidad del $AUC\text{-}ROC$ sin supuestos paramétricos, se realiza un remuestreo bootstrap con reemplazo (con $B = 1000$ iteraciones). El intervalo de confianza al $(1 - \alpha)\%$ se obtiene mediante el método percentil:

$$IC_{1-\alpha} = \left[ \theta^*_{\alpha/2},\ \theta^*_{1-\alpha/2} \right]$$

Donde $\theta^*_p$ es el percentil $p$-ésimo de la distribución empírica de los estadísticos $AUC^*$ recalculados en los remuestreos.

### 2.4. Coeficiente Kappa de Cohen ($\kappa$)
Utilizado para validar la concordancia inter-evaluador en la construcción del Gold Standard:

$$\kappa = \frac{p_o - p_e}{1 - p_e}$$

Donde:
*   $p_o$: Fracción de acuerdo observado.
    $$p_o = \frac{\sum_{i=1}^{k} C_{ii}}{N}$$
*   $p_e$: Probabilidad de acuerdo esperado por azar.
    $$p_e = \sum_{j=1}^{k} \left( \frac{\sum_{\text{eval 1}} C_{j\cdot}}{N} \times \frac{\sum_{\text{eval 2}} C_{\cdot j}}{N} \right)$$

---

## 3. Hipótesis H3: Equidad Algorítmica

Evalúa si las decisiones automatizadas de preselección ($\hat{y} \in \{0, 1\}$) mantienen equidad frente a grupos protegidos (género y rangos de edad).

### 3.1. Tasa de Selección ($SR$)
Representa la probabilidad de que un miembro de un grupo demográfico específico $g$ sea seleccionado como APTO:

$$SR_g = P(\hat{y} = 1 \mid G = g) = \frac{N_{g, \text{seleccionados}}}{N_g}$$

### 3.2. Impacto Dispar o Disparate Impact Ratio ($DIR$)
Es el cociente de tasas de selección entre el grupo protegido ($p$, ej. femenino) y el grupo de referencia/privilegiado ($r$, ej. masculino):

$$DIR = \frac{SR_p}{SR_r} = \frac{P(\hat{y} = 1 \mid G = p)}{P(\hat{y} = 1 \mid G = r)}$$

*   **Criterio de aceptación (Regla 4/5 de la EEOC):**
    $$DIR \ge 0.80$$
    Un valor inferior a 0.80 indica presencia de impacto dispar adverso sobre el grupo protegido.

### 3.3. Diferencia de Paridad Estadística o Statistical Parity Difference ($SPD$)
Es la diferencia absoluta entre las tasas de selección de ambos grupos:

$$SPD = SR_p - SR_r = P(\hat{y} = 1 \mid G = p) - P(\hat{y} = 1 \mid G = r)$$

*   $SPD = 0$: Paridad estadística perfecta.
*   $SPD < 0$: Sesgo adverso hacia el grupo protegido.
*   $SPD > 0$: Sesgo favorable al grupo protegido.
*   **Rango de Aceptación:** Típicamente $[-0.10, 0.10]$.
