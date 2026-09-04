from gpiozero              import AngularServo,DistanceSensor
from gpiozero.pins.pigpio  import PiGPIOFactory
from gpiozero.exc          import DistanceSensorNoEcho
from contextlib            import contextmanager
from time                  import sleep
import asyncio
import statistics
import warnings
import atexit

import logging

#Para evitar los mensajes por pantalla de:
#   /home/uiegalicia/Documents/RepositoriosGIT/RoombaExtension/.venv/lib/python3.13/site-packages/gpiozero/input_devices.py:975: DistanceSensorNoEcho: no echo received
#       warnings.warn(DistanceSensorNoEcho('no echo received')) 
warnings.filterwarnings("ignore", category=DistanceSensorNoEcho)


class USRotatingSensor:
    def __init__(self):
        # Inicialización de atributos de la clase
        self.DEBUG                  = True # Para activar el registro de actividad en fichero de log

        # Parámteros configuración hardware del sensor US
        self.PIN_ECHO_US            = 27   # Pin de la raspberry conectado al pin ECHO del sensor ultrasónico
        self.PIN_TRIGGER_US         = 17   # Pin de la raspberry conectado al pin TRIGGER del sensor ultrasónico

        # Parámteros configuración hardware y auxiliares del servo
        self.PIN_SERVO_GPIO         = 18   # Pin de la raspberry conectado al pin de control del servo

        self.MAX_DISTANCE_M         = 2.0  # Distancia máxima en metros para el sensor ultrasónico
        
        self.MIN_ANGLE              = 0    # Angulo mínimo de giro del servo (0 grados) 
        self.MAX_ANGLE              = 180  # Angulo máximo de giro del servo (180 grados)

        self.servo_last_pos         = 0    # Variable para almacenar la última posición del servo ya que se pierde al ejecutar el detach para evitar la vibración

        # Registrar cleanup en atexit como red de seguridad para liberar recursos
        atexit.register(self.cleanup)

        # Configuramos fichero de log, nivel y formato
        logging.basicConfig(
            filename='LibRoombaExtension.log', 
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Para configurar el acceso al GPIO de la Raspberry, mejora la precisión en los cálculos de temporización
        # Necesita que esté en funcionamiento el demonio pigpiod
        self.factory = PiGPIOFactory()
        
        self.sensor  = None
        self.servo   = None
        self.logea('USRotatingSensor.__init__: USRotatingSensor Instance created.')

    # Método para loguear mensajes
    def logea(self, mens):
        if self.DEBUG:
            logging.info(mens) 

    def cleanup(self):
        """
        Limpieza EXPLÍCITA y SEGURA de todos los recursos hardware.
        Debe llamarse antes de que el programa termine.
        """
        self.logea("=" * 60)
        self.logea("USRotatingSensor.cleanup: INICIANDO LIMPIEZA DE RECURSOS...")
        self.logea("=" * 60)
        
        # Orden inverso al de creación + try/except individual por recurso
        # Esto evita que un error en uno impida limpiar los demás
        recursos = [
            ('servo', self.servo),
            ('sensor', self.sensor),
            ('factory', self.factory)
        ]
        
        for nombre, obj in recursos:
            try:
                if obj is not None:
                    obj.close()
                    self.logea(f"USRotatingSensor.cleanup: ✓ {nombre}.close() ejecutado correctamente")
                else:
                    self.logea(f"USRotatingSensor.cleanup: ⚠ {nombre}: ya era None, saltando")
            except Exception as e:
                # Logear pero NO propagar: queremos limpiar todo lo posible
                self.logea(f"USRotatingSensor.cleanup: ⚠ ERROR cerrando {nombre}: {type(e).__name__}: {e}")
        
        # Resetear estados
        self.sensor  = None
        self.servo   = None
        self.factory = None
        
        self.logea("=" * 60)
        self.logea("USRotatingSensor.cleanup: LIMPIEZA COMPLETADA EXITOSAMENTE.")
        self.logea("=" * 60)
    
    # =============================================================================
    # PROTOCOLO DE CONTEXT MANAGER (para usar con 'with')
    # =============================================================================
    
    def __enter__(self):
        """Se llama al entrar en el bloque 'with'."""
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Se llama al salir del bloque 'with', incluso si hay excepción."""
        self.cleanup()
        return False  # No suprimir excepciones

    # Para llamar después de crear la instancia y antes de usarla, para inicializar el hardware de los dispositivos (sensor, servo)
    def setup(self):
        try:
            # Inicializa el sensor de distancia utilizando la librería GPIO Zero
            self.logea("USRotatingSensor.setup: Configurando sensor: ")
            self.logea(f"   Pin ECHO: {self.PIN_ECHO_US}")
            self.logea(f"   Pin TRIGGER: {self.PIN_TRIGGER_US}")
            self.logea(f"   MAX_DISTANCE (m): {self.MAX_DISTANCE_M}")

            self.sensor = DistanceSensor(echo=self.PIN_ECHO_US, trigger=self.PIN_TRIGGER_US, max_distance=self.MAX_DISTANCE_M, queue_len=5, pin_factory=self.factory)        
            
            # Inicializar el Servo
            # Ajustamos min_pulse y max_pulse para servos estándar de 180 grados
            self.logea("USRotatingSensor.setup: Configurando servo: ")
            self.logea(f"   Pin Servo GPIO: {self.PIN_SERVO_GPIO}")
            self.logea(f"   Ángulo Inicio: {self.MIN_ANGLE}")
            self.logea(f"   Ángulo Fin: {self.MAX_ANGLE}")

            self.servo = AngularServo(self.PIN_SERVO_GPIO, min_angle=0, max_angle=180,
                                    min_pulse_width=0.0005, max_pulse_width=0.0025,
                                    pin_factory=self.factory)
            # Inicializamos el servo a la posición 0 grados y guardamos esta posición como última conocida
            self.servo.angle    = 0
            self.servo_last_pos = 0  
        except Exception as e:
            self.logea(f"USRotatingSensor.setup: ✗ ERROR crítico en inicialización: {e}")
            raise RuntimeError(f"USRotatingSensor.setup: Fallo en inicialización de hardware: {e}")            

    async def gira_servo_raw(self, angle):
        """
        Para acceso directo al servo
        """
        # Validar ángulo solicitado 
        if (angle < self.MIN_ANGLE) or (angle > self.MAX_ANGLE):
            raise ValueError(format("USRotatingSensor.gira_servo_raw: Ángulo pasado (%d) incorrecto. Debe estar entre {self.ANGULO_MINIMO} y {self.ANGULO_MAXIMO} grados."))

        self.servo.angle = angle
        self.servo_last_pos = angle


    async def gira_servo(self, angle):
        try:
            #Validar ángulo solicitado 
            if (angle < self.MIN_ANGLE) or (angle > self.MAX_ANGLE):
                raise ValueError(format("Ángulo pasado (%d) incorrecto. Debe estar entre {self.ANGULO_MINIMO} y {self.ANGULO_MAXIMO} grados."))
            
            #Cálculo de pausa para el movimiento pedido, 0,003 sg por grado de movimiento
            pausa = abs(angle - self.servo_last_pos) * 0.003

            self.servo.angle    = angle
            self.servo_last_pos = angle

            await asyncio.sleep(pausa)
            #self.servo.detach() #se ha quitado porque con los servos pequeños, durante el barrido hacía movimientos extraños
        except asyncio.CancelledError:
            # Limpieza del servo al cancelar
            self.servo.detach()  # o self.servo.mid(), según prefieras
            raise  # Importante: re-lanzar para que asyncio gestione bien la cancelación

    async def LecturaUScmRaw(self): # Función para obtener la lectura del sensor ultrasónico en centímetros, sin filtrar ni procesar
        resultado = round(self.sensor.distance * 100, 1)  # Convertimos a cm y redondeamos a 1 decimal
        self.logea(f"USRotatingSensor.LecturaUScmRaw: Resultado final: {resultado}")
        return round(resultado)

    async def LecturaUScm_Filtrada(self, num_medidas=5, umbral_tolerancia=2.0):
        """
        Guarda una serie de medidas seguidas en una lista, filtra valores espúreos y devuelve el promedio de los restantes.
        
        :param num_medidas: número de tomas de medida del sensor para procesar.
        :param umbral_tolerancia: Cuánto puede alejarse un valor de la mediana para ser aceptado.
        """
    
        #Comprobamos que tenemos un número correcto de medidas 
        if num_medidas<1:
            return -1
    
        #Sacamos lecturas consecutivas del sensor 
        Lecturas = []
        i = 0
        while i <num_medidas:
            LecturaSensor = await self.LecturaUScmRaw()
            Lecturas.append(LecturaSensor)
            await asyncio.sleep(0.03)
            i += 1

        self.logea(f"LecturaUScm_Filtrada: Lecturas directas sensor US:{Lecturas}")

        # Hacemos un filtrado de las lecturas para descartar valores espúreos del sensor 

        # 1. Calculamos la mediana (el valor central, menos afectado por errores extremos)
        mediana = statistics.median(Lecturas)
    
        # 2. Filtramos: solo nos quedamos con valores que no se alejen demasiado de la mediana
        # Usamos una diferencia porcentual o absoluta según necesites.
        valores_validos = [
            x for x in Lecturas 
            if abs(x - mediana) <= umbral_tolerancia
        ]
        self.logea(f"LecturaUScm_Filtrada: Lecturas filtradas:{Lecturas} ")
    
        # 3. Si por algún motivo todos fueran descartados, usamos la mediana como plan B
        if not valores_validos:
            Resultado = round(mediana,1)
            self.logea(f"LecturaUScm_Filtrada: todas las medidas descartadas, devolvemos mediana{Resultado} ")
            return Resultado

        # 4. Devolvemos el promedio de los valores que sobrevivieron al filtro
        Resultado = round(statistics.mean(valores_validos),1)
        self.logea(f"LecturaUScm_Filtrada: resultado lectura sensor US por promedio de medidas:{Resultado} ")
        return Resultado

    async def realizar_barrido(self, ang_inicio=0, ang_fin=180, salto_angulo=20, retorno_final=True):
        #función auxiliar para que el while funcione con incrementos positivos o negativos según el sentido del barrido
        def continuar(ang_actual, ang_fin, salto):
            if salto > 0:
                return ang_actual <= ang_fin
            else:
                return ang_actual >= ang_fin
            
        #Comprobamos que los parámetros de barrido son correctos
        if ang_inicio<self.MIN_ANGLE or ang_inicio>self.MAX_ANGLE:
            raise ValueError(f"Parámetros de barrido incorrectos: inicio={ang_inicio}. Debe estar entre {self.MIN_ANGLE} y {self.MAX_ANGLE}.")
        if ang_fin<self.MIN_ANGLE or ang_fin>self.MAX_ANGLE:
            raise ValueError(f"Parámetros de barrido incorrectos: fin={ang_fin}. Debe estar entre {self.MIN_ANGLE} y {self.MAX_ANGLE}.")
        
        if ang_inicio>=ang_fin and salto_angulo>0:
            raise ValueError(f"Parámetros de barrido incorrectos: inicio={ang_inicio} debe ser menor que fin={ang_fin} para un salto positivo.")
        if ang_inicio<=ang_fin and salto_angulo<0:
            raise ValueError(f"Parámetros de barrido incorrectos: inicio={ang_inicio} debe ser mayor que fin={ang_fin} para un salto negativo.")

        self.logea(f"USRotatingSensor.realizar_barrido: Iniciando barrido desde {ang_inicio}° hasta {ang_fin}° con paso de {salto_angulo}°.")

        Angulos_Lecturas = []
        Lecturas_Sensor = []
        
        ang = ang_inicio
        while continuar(ang, ang_fin, salto_angulo):
            #Movemos el servo al ángulo deseado y esperamos a que se estabilice
            await self.gira_servo(ang)

            #Tomamos lectura del sensor ultrasónico filtrada y la guardamos junto con el ángulo correspondiente
            lectura = await self.LecturaUScm_Filtrada()
            Angulos_Lecturas.append(ang)
            Lecturas_Sensor.append(lectura)
            
            # Esperamos a que los ecos ultrasónicos se disipen antes del siguiente disparo.
            await asyncio.sleep(0.1)
            
            self.logea(f"USRotatingSensor.realizar_barrido: Ángulo {ang}° -> Lectura {lectura} cm")
            ang += salto_angulo

        self.logea(f"USRotatingSensor.realizar_barrido: Barrido completado. Ángulos: {Angulos_Lecturas}, Lecturas: {Lecturas_Sensor}")

        if retorno_final:
            await self.gira_servo(ang_inicio) #Volvemos a la posición inicial    

        return (Angulos_Lecturas, Lecturas_Sensor)


    def run(self, coro):
        """Punto de entrada que gestiona Ctrl-C limpiamente."""
        try:
            asyncio.run(coro)
        except KeyboardInterrupt:
            pass    
