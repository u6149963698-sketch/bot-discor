import subprocess
import threading

def ejecutar_babachops():
    subprocess.run(["python", "babachopsbot.py"])

def ejecutar_dogday():
    subprocess.run(["python", "dogdaybot.py"])

if __name__ == "__main__":
    hilo_1 = threading.Thread(target=ejecutar_babachops)
    hilo_2 = threading.Thread(target=ejecutar_dogday)

    hilo_1.start()
    hilo_2.start()

    hilo_1.join()
    hilo_2.join()
  
