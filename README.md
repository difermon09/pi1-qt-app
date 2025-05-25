# Aplicación de Monitoreo de Sensores

Aplicación de escritorio PyQt6 para visualizar y gestionar datos de sensores ESP32. Proporciona una interfaz gráfica intuitiva para:
- Visualizar lecturas de sensores en tiempo real
- Gestionar sensores y sus configuraciones
- Ver análisis de datos realizados por Llama 3.2
- Exportar datos y gráficos

## Estructura del Proyecto

```
qt_app/
├── main.py          # Punto de entrada de la aplicación
├── views/           # Componentes de interfaz de usuario
│   ├── main_window.py
│   ├── sensor_view.py
│   └── analysis_view.py
├── resources/       # Recursos (imágenes, iconos)
└── requirements.txt # Dependencias
```

## Instalación

### Opción 1: Usar el ejecutable (Recomendado)

1. Ve a la sección [Releases](https://github.com/difermon09/pi1-qt-app/releases) de este repositorio
2. Descarga la última versión del archivo `PI1_app_windows.exe`
3. Ejecuta el archivo descargado

### Opción 2: Instalación desde código fuente

1. Crear un entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

3. Ejecutar la aplicación:
```bash
python main.py
```

## Compilación

Para crear un ejecutable:

1. Instalar PyInstaller:
```bash
pip install pyinstaller
```

2. Crear el ejecutable:
```bash
pyinstaller --onefile --windowed --icon=logotip.ico --add-data "Fons_app.png;." main.py
```

El ejecutable se creará en la carpeta `dist/`.

## Características

- Dashboard en tiempo real
- Gráficos interactivos
- Gestión de sensores
- Visualización de análisis
- Exportación de datos
- Personalización de la interfaz

## Configuración

La aplicación se conecta automáticamente a la API en `http://localhost:8000`. Si necesitas cambiar la URL de la API:

1. Abrir `config.py`
2. Modificar la variable `API_URL`

## Solución de Problemas

1. **Si la aplicación no se inicia**
   - Verificar que Python 3.12+ está instalado
   - Comprobar que todas las dependencias están instaladas
   - Verificar que la API está corriendo

2. **Si no se ven los datos**
   - Verificar la conexión con la API
   - Comprobar que hay sensores registrados
   - Verificar que hay lecturas disponibles

## Contacto

Para soporte o preguntas, contacta con:
- GitHub: [difermon09](https://github.com/difermon09) 