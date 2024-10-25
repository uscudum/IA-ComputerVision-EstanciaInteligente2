## **Pasos para Implementar el Proyecto**

### **Paso 1: Estructura del Proyecto**

Crea la siguiente estructura de carpetas para mantener todo organizado:

```
/estancia-inteligente
│
├── /model                    # Carpeta del modelo entrenado con Teachable Machine
│   └── keras_model.h5        # Archivo del modelo
├── /templates                # Carpeta para las plantillas HTML
│   └── index.html            # Interfaz de la granja inteligente
├── app.py                    # Código del servidor Flask
├── detector.py               # Código para la detección en tiempo real
└── requirements.txt          # Dependencias del proyecto
```

---

### **Paso 2: Código Completo del Proyecto**

#### **1. `detector.py` - Detección en Tiempo Real**

```python
import tensorflow.keras as keras
import numpy as np
import cv2
import requests

# URL del servidor Flask al que se enviará la notificación
url = 'http://localhost:5000/upload'

# Cargar el modelo entrenado desde Teachable Machine
model = keras.models.load_model('model/keras_model.h5')
class_names = ['Vaca', 'Gallina', 'Caballo', 'Ningún animal']

# Iniciar la cámara
cap = cv2.VideoCapture(0)
input_size = (224, 224)
previous_prediction = None

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Preprocesar la imagen para el modelo
    resized_frame = cv2.resize(frame, input_size)
    normalized_frame = np.array(resized_frame, dtype=np.float32) / 255.0
    input_data = np.expand_dims(normalized_frame, axis=0)

    # Realizar la predicción
    predictions = model.predict(input_data)
    predicted_class = np.argmax(predictions[0])

    # Mostrar el nombre del animal detectado
    cv2.putText(
        frame, f'Detectado: {class_names[predicted_class]}',
        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2
    )

    # Enviar notificación si hay un cambio en la detección
    if class_names[predicted_class] != previous_prediction:
        data = {'message': f'Se detectó: {class_names[predicted_class]}'}
        try:
            requests.post(url, json=data)
            previous_prediction = class_names[predicted_class]
        except Exception as e:
            print(f"Error enviando notificación: {e}")

    # Mostrar el frame en pantalla
    cv2.imshow('Detección de Objeto', frame)

    # Salir con 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```

---

#### **2. `app.py` - Servidor Flask con Socket.IO**

```python
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import eventlet

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    data = request.json
    if data and 'message' in data:
        socketio.emit('object_detected', {'message': data['message']})
        return 'Mensaje recibido', 200
    return 'No se recibió ningún mensaje', 400

if __name__ == "__main__":
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
```

---

#### **3. `templates/index.html` - Interfaz HTML**

```html
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Detección de Animales en la Granja</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.0/socket.io.min.js"></script>
    <style>
        body {
            font-family: 'Comic Sans MS', cursive, sans-serif;
            background: url('https://cdn.pixabay.com/photo/2024/01/09/14/44/cow-8497722_1280.jpg') no-repeat center center fixed;
            background-size: cover;
            margin: 0;
            padding: 0;
            color: white;
        }
        .container {
            background-color: rgba(0, 0, 0, 0.6);
            padding: 40px;
            margin: 100px auto;
            width: 80%;
            max-width: 600px;
            text-align: center;
            border-radius: 15px;
            box-shadow: 0px 0px 15px 5px rgba(0, 0, 0, 0.5);
        }
        h1 {
            font-size: 3em;
            margin-bottom: 20px;
            color: #FFD700;
            text-shadow: 2px 2px 4px #000;
        }
        p {
            font-size: 1.5em;
            margin-bottom: 30px;
        }
        .status {
            font-size: 1.2em;
            background-color: rgba(255, 255, 255, 0.8);
            color: #333;
            padding: 10px;
            border-radius: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Granja Inteligente</h1>
        <p id="status" class="status">Esperando detección de animales...</p>
    </div>

    <script type="text/javascript">
        document.addEventListener('DOMContentLoaded', () => {
            const socket = io();

            socket.on('connect', () => {
                console.log('Conectado a Socket.IO');
            });

            socket.on('object_detected', data => {
                console.log('Datos recibidos:', data);
                document.getElementById('status').innerText = data.message;
            });

            socket.on('disconnect', () => {
                console.log('Desconectado de Socket.IO');
            });
        });
    </script>
</body>
</html>
```

---

#### **4. `requirements.txt` - Dependencias del Proyecto**

```
flask
flask-socketio
eventlet
tensorflow
opencv-python
requests
```

---

#### **5. Configura tu Entorno de Python**
Debemos segurarnos de tener instaladas las librerías necesarias:

```
pip install tensorflow opencv-python-headless numpy
```
