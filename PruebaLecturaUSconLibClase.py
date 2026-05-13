#!/usr/bin/env python3
from LibRoombaExtensionConClases import USRotatingSensor
import asyncio
from time import sleep



async def main():
    #with USRotatingSensor() as hw:  # ← cleanup automático al salir
        try:
            hw.setup()
            while True:
                # print(hw.realizar_barrido())
                '''
                a = int(input("ángulo: "))
                print(a)
                print(hw.servo.angle)

                hw.gira_sensor(a)
                '''
                for a in range(0, 180+1, 20):
                    await hw.gira_sensor(a)
                    await asyncio.sleep(0.2)
                for a in range(180, -1, -20):
                    await hw.gira_sensor(a)
                    await asyncio.sleep(0.2)                
            
                sleep(3)
        except KeyboardInterrupt:
            print("\n🛑 Saliendo...")
    # ← hw.cleanup() se llama automáticamente aquí



# Para lanzar el programa
if __name__ == "__main__":
   #asyncio.run(main())
    with USRotatingSensor() as hw:  # ← cleanup automático al salir   
        hw.run(main())