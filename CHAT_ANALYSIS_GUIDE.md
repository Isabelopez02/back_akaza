# 📊 Análisis de Chats de Clientes en Telegram

## ¿Qué es?

El admin ahora puede analizar los mensajes de los clientes para entender:
- ❓ **Preguntas más frecuentes**: Qué preguntan los clientes con más frecuencia
- 💬 **Opiniones y sentimientos**: Qué opinan los clientes, nivel de satisfacción
- 🍽️ **Platos más mencionados**: Cuáles son los platos que más piden/mencionan
- 📈 **Estadísticas**: Número total de mensajes, usuarios activos, mesas atendidas

## Comandos disponibles para el Admin

Envía estos comandos desde Telegram al bot:

### 1. `/chat_help`
Muestra la lista de todos los comandos disponibles.

**Resultado:**
```
📊 COMANDOS DE ANÁLISIS DE CHATS DISPONIBLES:

- /chat_reporte - Reporte ejecutivo general
- /chat_preguntas - Preguntas más frecuentes de clientes
- /chat_opiniones - Opiniones y sentimientos de clientes
- /chat_platos - Platos más mencionados y solicitados
- /chat_stats - Estadísticas básicas (últimos 7 días)
```

### 2. `/chat_reporte`
Genera un reporte ejecutivo con estadísticas generales de chats en los últimos 7 días.

**Muestra:**
- Total de mensajes analizados
- Usuarios únicos que conversaron
- Mesas atendidas
- Puertos a análisis detallados

### 3. `/chat_preguntas`
Analiza usando IA las **preguntas más frecuentes** que hacen los clientes.

**Muestra:**
- Top 5 preguntas/temas más frecuentes
- Cuántas veces aparecen
- Ejemplos específicos de lo que preguntan

**Ejemplo de respuesta:**
```
Preguntas Más Frecuentes (Últimos 7 días):

1. ¿Tienen opciones vegetarianas? - ~8 menciones
2. ¿Cuánto demora el ceviche? - ~6 menciones
3. ¿Pueden modificar ingredientes? - ~5 menciones
...
```

### 4. `/chat_opiniones`
Analiza el **sentimiento general** y **opiniones** de los clientes.

**Muestra:**
- Sentimiento general (Positivo/Negativo/Neutral)
- Principales quejas o insatisfacciones
- Aspectos que más les gustan
- Sugerencias implícitas de mejora
- Nivel de satisfacción (escala 1-10)

**Ejemplo de respuesta:**
```
Análisis de Opiniones y Sentimientos:

Sentimiento General: POSITIVO (8/10)

Aspectos Positivos:
- Los clientes elogian la frescura del pescado
- Servicio amable y rápido
- Presentación de los platos

Quejas/Áreas de Mejora:
- Algunos encuentran los precios altos
- Esperan mejores opciones de bebidas
```

### 5. `/chat_platos`
Analiza cuáles son los **platos más mencionados** y solicitados.

**Muestra:**
- Platos más mencionados (con frecuencia)
- Platos que reciben más elogios
- Platos con críticas
- Combinaciones populares
- Pedidos especiales frecuentes

**Ejemplo de respuesta:**
```
Platos Más Mencionados:

Top Pedidos:
- Ceviche Clásico - ~25 menciones
- Tiradito de Atún - ~18 menciones
- Causa Limeña - ~12 menciones

Mejor Valorados:
- Ceviche Akaza - Elogiado por frescura
- Tiradito Especial - Favorito por sabor

Modificaciones Frecuentes:
- "Sin cilantro" en ceviches
- "Más ají" en tiraditos
```

### 6. `/chat_stats`
Muestra **estadísticas básicas** rápidas.

**Muestra:**
- Total de mensajes en los últimos 7 días
- Cantidad de usuarios únicos
- Cantidad de mesas atendidas

---

## 📋 Cómo funciona internamente

1. **Recopilación**: Los chats de clientes se guardan automáticamente en la BD (`ia_historial_chat`)
2. **Análisis**: El servicio `ChatAnalysisService` obtiene los mensajes y los envía a Gemini IA
3. **Procesamiento**: Gemini analiza patrones, frecuencias, sentimientos
4. **Respuesta**: El bot devuelve el análisis al admin en Telegram

---

## 🔐 Seguridad

- ✅ **Solo el admin** (ID configurado en `ID_ADMIN`) puede ver estos análisis
- ✅ Los clientes normales **no ven** estos comandos de análisis
- ✅ Los datos se analizan en tiempo real desde la BD

---

## 📊 Ejemplo de flujo

1. Admin escribe en Telegram: `/chat_preguntas`
2. Bot responde: "🔍 Analizando preguntas frecuentes..." (mientras procesa)
3. Bot envía el análisis con las preguntas más comunes de clientes
4. Admin puede tomar decisiones basadas en estos insights

---

## 📝 Notas

- Los análisis usan los **últimos 7 días** de chats
- Se analizan hasta **100-150 mensajes** para optimizar tiempo
- La IA es **Gemini 2.5 Flash** para análisis rápidos y precisos
- Las respuestas usan **formato HTML** para Telegram

---

## Próximas mejoras sugeridas

- [ ] Análisis por período de tiempo personalizado
- [ ] Exportar reportes como PDF
- [ ] Alertas automáticas si hay muchas quejas
- [ ] Seguimiento de satisfacción por cliente
- [ ] Análisis de performance de platos específicos
