# ⚡ Medidor de Velocidad de Mano

Una aplicación web que utiliza inteligencia artificial para medir la velocidad con la que bajas tu mano, calculando tiempo, distancia y velocidad en tiempo real.

## 🌟 Características

- **Detección de manos en tiempo real** usando MediaPipe Hands
- **Cálculo de velocidad** instantánea y máxima
- **Medición de distancia** recorrida por la mano
- **Cronómetro preciso** en milisegundos
- **Historial de mediciones** para comparar tus resultados
- **Interfaz moderna y responsive** que funciona en cualquier dispositivo
- **Sin instalación** - funciona directamente en el navegador

## 🚀 Cómo usar

### Opción 1: Usar directamente desde GitHub Pages

1. Visita: [TU_USUARIO.github.io/retroalimentacion-academica-ia/speed-measurement/](https://jorgeQuintero87.github.io/retroalimentacion-academica-ia/speed-measurement/)

### Opción 2: Ejecutar localmente

1. Clona este repositorio:
```bash
git clone https://github.com/JorgeQuintero87/retroalimentacion-academica-ia.git
cd retroalimentacion-academica-ia/speed-measurement
```

2. Abre `index.html` en tu navegador web moderno (Chrome, Firefox, Edge, Safari)

3. Permite el acceso a la cámara cuando te lo solicite

## 📋 Instrucciones de medición

1. **Permite el acceso a la cámara** cuando el navegador te lo solicite
2. **Posiciona tu mano** en la parte superior del encuadre de la cámara
3. **Espera a que se detecte** tu mano (verás "Mano detectada - Listo para medir")
4. **Haz clic en "Iniciar Medición"**
5. **Baja tu mano rápidamente** hacia abajo
6. El sistema calculará automáticamente:
   - Velocidad instantánea
   - Velocidad máxima alcanzada
   - Distancia total recorrida
   - Tiempo transcurrido
7. Puedes **reiniciar** y volver a medir cuantas veces quieras

## 🎯 Métricas mostradas

- **Velocidad**: Velocidad instantánea en cm/s
- **Distancia**: Distancia total recorrida en cm
- **Tiempo**: Tiempo transcurrido en milisegundos
- **Velocidad Máxima**: La velocidad pico alcanzada durante el movimiento

## 🛠️ Tecnologías utilizadas

- **HTML5/CSS3**: Estructura y diseño
- **JavaScript**: Lógica de la aplicación
- **MediaPipe Hands**: Detección y tracking de manos
- **Canvas API**: Renderizado de video y detección visual

## 📱 Compatibilidad

- ✅ Google Chrome (recomendado)
- ✅ Microsoft Edge
- ✅ Firefox
- ✅ Safari
- ✅ Dispositivos móviles con cámara

**Nota**: Se requiere un navegador que soporte WebRTC y getUserMedia API.

## 🔒 Privacidad

- Todo el procesamiento se realiza **localmente en tu navegador**
- **No se envían datos** a ningún servidor
- **No se graban videos** ni se almacenan imágenes
- El acceso a la cámara es **solo para detección en tiempo real**

## 💡 Consejos para mejores mediciones

1. Asegúrate de tener **buena iluminación**
2. Usa un **fondo que contraste** con tu mano
3. Mantén tu **mano visible** durante todo el movimiento
4. **Baja la mano en línea recta** para mediciones más precisas
5. Realiza el movimiento de forma **fluida y continua**

## 🎓 Aplicaciones

Esta aplicación puede ser útil para:
- **Entrenamiento deportivo**: Medir velocidad de reflejos
- **Fisioterapia**: Evaluar progreso en recuperación
- **Juegos y desafíos**: Competir con amigos
- **Educación**: Aprender sobre física y movimiento
- **Investigación**: Estudios sobre velocidad de reacción

## 🐛 Solución de problemas

### La cámara no funciona
- Verifica que hayas dado permisos de cámara al navegador
- Revisa que ninguna otra aplicación esté usando la cámara
- Intenta recargar la página

### La mano no se detecta
- Mejora la iluminación del ambiente
- Acerca más la mano a la cámara
- Usa un fondo que contraste con tu piel

### Las mediciones parecen incorrectas
- La conversión de píxeles a centímetros es aproximada
- Para mayor precisión, ajusta el factor de conversión en el código
- Asegúrate de que tu mano esté a distancia constante de la cámara

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Si tienes ideas para mejorar esta aplicación:

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo LICENSE para más detalles.

## 👨‍💻 Autor

**Ing. Jorge Quintero**
- Email: lucho19q@gmail.com
- GitHub: [@JorgeQuintero87](https://github.com/JorgeQuintero87)

## 🙏 Agradecimientos

- [MediaPipe](https://mediapipe.dev/) por su increíble librería de detección de manos
- [Google](https://google.com) por proporcionar MediaPipe de forma gratuita

---

⭐ Si te gusta este proyecto, ¡dale una estrella en GitHub!
