import tensorflow.keras as keras
import numpy as np
import cv2
import requests

# URL del servidor Flask al que se enviará la notificación
url = 'http://localhost:5000/upload'

# Cargar el modelo exportado desde Teachable Machine
model = keras.models.load_model('model/keras_model.h5')
class_names = ['Vaca', 'Gallina', 'Caballo', 'Ningún animal']  # Cambia según tus clases

# Iniciar la cámara
cap = cv2.VideoCapture(0)

# Tamaño esperado por el modelo (224x224 para Teachable Machine)
input_size = (224, 224)

previous_prediction = None

while True:
    # Leer el frame de la cámara
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

    # Mostrar la clase en el frame
    cv2.putText(
        frame, f'Detectado: {class_names[predicted_class]}',
        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2
    )

    # Enviar notificación si cambia la predicción
    if class_names[predicted_class] != previous_prediction:
        data = {'message': f'Se detectó: {class_names[predicted_class]}'}
        try:
            requests.post(url, json=data)
            previous_prediction = class_names[predicted_class]
        except Exception as e:
            print(f"Error enviando notificación: {e}")

    # Mostrar el frame
    cv2.imshow('Detección de Objeto', frame)

    # Salir con la tecla 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Liberar la cámara y cerrar las ventanas
cap.release()
cv2.destroyAllWindows()