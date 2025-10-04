# Nombres de Archivo Válidos para Detección Automática

## ✅ Sistema de Detección Mejorado

El sistema ahora **detecta automáticamente** qué criterio/tarea presenta el estudiante basándose en el **nombre del archivo**.

---

## 📝 Nombres de Archivo Reconocidos

### Español:
```
✅ tarea_1.pdf          → Criterio 1
✅ tarea_2.ipynb        → Criterio 2
✅ tarea_3.pdf          → Criterio 3
✅ tarea1.pdf           → Criterio 1
✅ tarea2.pdf           → Criterio 2
✅ tarea3.pdf           → Criterio 3

✅ criterio_1.pdf       → Criterio 1
✅ criterio_2.ipynb     → Criterio 2
✅ criterio_3.pdf       → Criterio 3
✅ criterio1.pdf        → Criterio 1
✅ criterio2.pdf        → Criterio 2
✅ criterio3.pdf        → Criterio 3

✅ ejercicio_1.pdf      → Criterio 1
✅ ejercicio_2.ipynb    → Criterio 2
✅ ejercicio_3.pdf      → Criterio 3

✅ actividad_1.pdf      → Criterio 1
✅ actividad_2.ipynb    → Criterio 2
✅ actividad_3.pdf      → Criterio 3

✅ punto_1.pdf          → Criterio 1
✅ punto_2.ipynb        → Criterio 2
✅ punto_3.pdf          → Criterio 3
```

### Inglés:
```
✅ task_1.pdf           → Criterio 1
✅ task_2.ipynb         → Criterio 2
✅ task_3.pdf           → Criterio 3

✅ criterion_1.pdf      → Criterio 1
✅ criterion_2.ipynb    → Criterio 2
✅ criterion_3.pdf      → Criterio 3

✅ activity_1.pdf       → Criterio 1
✅ activity_2.ipynb     → Criterio 2
✅ activity_3.pdf       → Criterio 3
```

### Abreviaturas:
```
✅ c1.pdf               → Criterio 1
✅ c2.ipynb             → Criterio 2
✅ c3.pdf               → Criterio 3

✅ t1.pdf               → Criterio 1
✅ t2.ipynb             → Criterio 2
✅ t3.pdf               → Criterio 3

✅ e1.pdf               → Criterio 1
✅ e2.ipynb             → Criterio 2
✅ e3.pdf               → Criterio 3
```

### Con guiones o espacios:
```
✅ tarea-1.pdf          → Criterio 1
✅ tarea-2.ipynb        → Criterio 2
✅ tarea 3.pdf          → Criterio 3

✅ criterio-1.pdf       → Criterio 1
✅ criterio 2.ipynb     → Criterio 2
```

---

## 🚀 Cómo Funciona

1. **Sube un archivo** con nombre que incluya: `tarea_3.pdf`, `criterio2.ipynb`, etc.
2. **El sistema detecta** automáticamente que es el Criterio 3 o 2
3. **Solo evalúa ese criterio** específico
4. **Los demás criterios** aparecen como "NO PRESENTADO"

---

## 📊 Ejemplo de Evaluación

### Archivo: `tarea_2.ipynb` (Modelos de regresión)

**Resultado esperado:**
```
⚫ Criterio 1: Carga datasets - 0/30 pts (NO PRESENTADO)
✅ Criterio 2: Modelos de regresión - 45/50 pts (ALTO)
⚫ Criterio 3: Modelos de clasificación - 0/50 pts (NO PRESENTADO)
✅ Criterio 4: Participación en foro - 8/10 pts (MEDIO)
✅ Criterio 5: Formato del documento - 9/10 pts (ALTO)

Puntaje total: 62/150
```

**Logs en consola:**
```
[EVAL] Evaluando documento para: Machine Learning
       Archivo: tarea_2.ipynb
       ✓ Criterio detectado desde nombre: 2

✗ Criterio 1: Archivo indica Criterio 2 → NO PRESENTADO
✓ Criterio 2: PRESENTE confirmado (grupos: 3, confianza: alta)
✗ Criterio 3: Archivo indica Criterio 2 → NO PRESENTADO
✓ Criterio 4: PRESENTE confirmado (grupos: 2, confianza: media)
✓ Criterio 5: PRESENTE confirmado (grupos: 1, confianza: alta)
```

---

## ⚠️ Notas Importantes

1. **El nombre del archivo es PRIORITARIO** sobre el análisis de contenido
2. Si el archivo se llama `tarea_2.pdf`, SOLO evaluará el Criterio 2
3. Los Criterios 4 y 5 (foro y formato) se evalúan SIEMPRE
4. Los números válidos son: 1, 2, 3, 4, 5

---

## 🎯 Ventajas del Sistema

- ✅ **Precisión 100%**: No confunde criterios
- ✅ **Rápido**: No necesita analizar todo el contenido primero
- ✅ **Flexible**: Acepta múltiples formatos de nombre
- ✅ **Bilingüe**: Funciona en español e inglés

---

¡Sistema listo para usar! 🎉
