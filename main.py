# Importamos las librerías necesarias
from configs.server import app
import uvicorn
import colorama

# Inicializamos colorama para colorear los mensajes en consola
colorama.init()

# Iniciamos el servidor cuando este archivo se ejecuta directamente
if __name__ == "__main__":
    portNumber = 8000
    print(colorama.Fore.BLUE + "   Tu server está corriendo en el puerto:", portNumber)
    uvicorn.run(app, host="0.0.0.0", port=portNumber)
