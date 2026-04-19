## 🚀 Guía de Inicio Rápido (Backend)

Este proyecto utiliza **FastAPI** y requiere un entorno virtual para aislar las dependencias y evitar conflictos con el sistema operativo.

### Pasos para levantar el servidor en Windows:

**1. Crear el Entorno Virtual (Solo la primera vez)**
Crea una carpeta aislada para las librerías del proyecto.
\`\`\`
python -m venv venv
\`\`\`

**2. Activar el Entorno Virtual (Siempre que abras la terminal)**
Antes de instalar o ejecutar cualquier cosa, debes activar el entorno. Sabrás que está activo porque aparecerá `(venv)` al inicio de tu línea de comandos.
\`\`\`
.\venv\Scripts\activate
\`\`\`

**3. Instalar Dependencias**
Instala FastAPI, el servidor Uvicorn y las herramientas de base de datos.
\`\`\`
pip install fastapi uvicorn sqlalchemy pydantic
\`\`\`
pip install google-genai
\`\`\`

**4. Levantar el Servidor en Modo Desarrollo**
Ejecuta la aplicación. El flag `--reload` hará que el servidor se reinicie automáticamente cada vez que guardes un cambio en el código.
\`\`\`
uvicorn main:app --reload
\`\`\`

> **Nota:** Para probar los endpoints visualmente, visita `http://localhost:8000/docs` en tu navegador.