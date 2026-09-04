#!/usr/bin/env python3
from server.us_rotating_sensor import USRotatingSensor
import asyncio
from time import sleep



async def main():
    with USRotatingSensor() as hw:  # ← cleanup automático al salir
        try:
            hw.MAX_DISTANCE_M = 2.0  # Ajusta la distancia máxima según tus necesidades
            hw.setup()
            while True:
                #print(await hw.LecturaUScmRaw())
                Datos = await hw.realizar_barrido(0, 180, 20, False)
                print(Datos)

                Datos = await hw.realizar_barrido(180, 0, -20, False)
                print(Datos)
                #print(await hw.LecturaUScmRaw())
                #print(await hw.realizar_barrido())
                '''
                a = int(input("ángulo: "))
                print(a)
                print(hw.servo.angle)

                hw.gira_sensor(a)
                '''
                '''
                for a in range(0, 180+1, 20):
                    await hw.gira_sensor(a)
                    await asyncio.sleep(0.2)
                for a in range(180, -1, -20):
                    await hw.gira_sensor(a)
                    await asyncio.sleep(0.2)                
                '''            
                await asyncio.sleep(0.9)
        except KeyboardInterrupt:
            print("\n🛑 Saliendo...")
    # ← hw.cleanup() se llama automáticamente aquí



# Para lanzar el programa
if __name__ == "__main__":
   #asyncio.run(main())
    with USRotatingSensor() as hw:  # ← cleanup automático al salir   
        hw.run(main())