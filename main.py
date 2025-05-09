from configs.server import app
import uvicorn
import colorama

colorama.init()

if __name__ == "__main__":
    portNumber = 8000
    print(colorama.Fore.BLUE + "   Tu server esta corriendo en el puerto: ", portNumber)
    uvicorn.run(app, host="0.0.0.0", port=portNumber)