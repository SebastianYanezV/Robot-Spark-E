#include <SoftwareSerial.h>
#include <DHT.h>
#include <Servo.h>

// Declaración de los pines para los Motores Izq y Der
#define INT1 5
#define INT2 6
#define INT3 9
#define INT4 10
// Declaración del pin del Servo motor
#define SERVO 11
// Declaración de los pines del sensor Ultrasonido
#define TRIGGER 13
#define ECHO 12
// Declaración del pin del sensor de temperatura y humedad DHT11
#define DHTPIN 8
// Declaración de los pines para SoftwareSerial
#define RX 2
#define TX 3
// Declaración de las direcciones con respecto al mapa
#define U 0  //Arriba
#define R 1  //Derecha
#define D 2  //Abajo
#define L 3  //Izquierda
// Declaración de las direcciones con respecto al robot
#define AVANZAR 'A'
#define RETROCEDER 'R'
#define IZQUIERDA 'I'
#define DERECHA 'D'
#define PARAR 'P'
// Declaración de las marcas en el mapa
#define DESCONOCIDO "D"
#define CONOCIDO "C"
#define OBSTACULO "O"
#define TEMP_ALTA "T_A"
#define TEMP_MEDIA "T_M"
#define GAS_ALTO "G_A"
#define GAS_MEDIO "G_M"

// Inicializar la instancia de SoftwareSerial
SoftwareSerial mySerial(TX, RX);

// Crear una instancia de DHT
DHT dht(DHTPIN, DHT11);

// Crear una instancia de Servo
Servo myServo;

// Declarar las variables para los sensores y actuadores
float temperatura = 0;
float humedad = 0;
int gases = 300;
int velocidad = 0;
int direccion_global = U;
float distancia = 0;
int tiempo = 0;
int servoPosition = 0;

// Declarar la estructura para moverse
struct Movimiento {
  bool enMovimiento = false;
  int delay = 0;
  char dir;
};

Movimiento mov;

void setup() {
  // Configurar el baud rate del puerto serial
  Serial.begin(9600);
  mySerial.begin(9600);

  // Configuración de los pines para los Motores Izq y Der
  pinMode(INT1, OUTPUT);
  pinMode(INT2, OUTPUT);
  pinMode(INT3, OUTPUT);
  pinMode(INT4, OUTPUT);
  analogWrite(INT1, LOW);
  analogWrite(INT2, LOW);
  analogWrite(INT3, LOW);
  analogWrite(INT4, LOW);

  // Configuración de los pines del sensor Ultrasonido
  pinMode(TRIGGER, OUTPUT);
  pinMode(ECHO, INPUT);

  // Iniciar el sensor DHT
  dht.begin();

  // Adjuntar el servomotor al pin especificado
  //myServo.attach(SERVO);
  // Inicializar la posición del servo
  //myServo.write(servoPosition);
}

void loop() {
  distancia = Ultrasonido();
  mySerial.println(String(distancia) + " " + String(mov.enMovimiento));
  // Si la distancia frente al robot es mayor de 1.5m, avanzará
  if (distancia > 60){
    String rutaString = "<R," + String(direccion_global) + "," + CONOCIDO + ">";
    mySerial.println(rutaString);
    moverse(AVANZAR);
  } else {
    String rutaString = "<R," + String(direccion_global) + "," + OBSTACULO + ">";
    mySerial.println(rutaString);
    String direccionesString = mySerial.readStringUntil('\n'); // Leer hasta el salto de línea
    direccionesString.trim(); // Eliminar espacios en blanco iniciales y finales

    // Verificar que la cadena está en el formato correcto
    if (direccionesString.startsWith("<") && direccionesString.endsWith(">")) {
      direccionesString = direccionesString.substring(1, direccionesString.length() - 1); // Eliminar los caracteres '<' y '>'
      Serial.println("Cadena recibida: " + direccionesString);

      // Dividir la cadena en las direcciones individuales
      int startIndex = 0;
      int endIndex = 0;
      while ((endIndex = direccionesString.indexOf(',', startIndex)) != -1) {
          String direccion = direccionesString.substring(startIndex, endIndex);
          Serial.println("Direccion: " + direccion);
          moverse(direccion.charAt(0));
          startIndex = endIndex + 1;
      }
      // Obtener la última dirección
      String direccion = direccionesString.substring(startIndex);
      Serial.println("Direccion: " + direccion);
      moverse(direccion.charAt(0));
    }
  }

  // Enviar la cadena a través de Bluetooth
  String dataString = capturaData();
  mySerial.println(dataString);
  delay(1000);  // Enviar datos cada segundo
}

String capturaData() {
  // Leer los datos del sensor DHT11
  humedad = dht.readHumidity();
  temperatura = dht.readTemperature();
  // Leer los datos del sensor MQ-135

  // Leer los datos del Ultrasonido
  distancia = Ultrasonido();

  return "<T," + String(temperatura) + ",H," + String(humedad) + ",G," + String(gases) + ",D," + String(distancia) + ">";
}

long Ultrasonido() {
  long duration;  // Tiempo que demora en llegar el eco
  long distance;  // Distancia en centímetros
  digitalWrite(TRIGGER, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIGGER, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIGGER, LOW);
  duration = pulseIn(ECHO, HIGH);  // Obtenemos el ancho del pulso
  distance = (duration * .0343) / 2;
  return distance;
}

// Motor Izquierdo
void motorA(char d, int vel) {
  if (d == 'A') {
    analogWrite(INT1, LOW);
    analogWrite(INT2, vel);
  } else if (d == 'R') {
    analogWrite(INT1, vel);
    analogWrite(INT2, LOW);
  } else {
    analogWrite(INT1, LOW);
    analogWrite(INT2, LOW);
  }
}

// Motor Derecho
void motorB(char d, int vel) {
  if (d == 'A') {
    analogWrite(INT3, LOW);
    analogWrite(INT4, vel);
  } else if (d == 'R') {
    analogWrite(INT3, vel);
    analogWrite(INT4, LOW);
  } else {
    analogWrite(INT3, LOW);
    analogWrite(INT4, LOW);
  }
}

void cambiarDirGlobal(int cambio) {
  direccion_global += cambio;
  if (direccion_global < 0) {
    direccion_global += 4;
  }
  if (direccion_global > 3) {
    direccion_global -= 4;
  }
}

void moverse(char d) {
  mov.enMovimiento = true;
  mov.dir = d;
  while (mov.enMovimiento) {
    if (mov.dir == AVANZAR) {
      if (mov.delay > 20) {
        mov.enMovimiento = false;
        mov.delay = 0;
      } else {
        mov.delay += 1;
        motorA('A', 255);
        motorB('A', 255);
      }
    }

    if (mov.dir == DERECHA) {
      if (mov.delay > 10) {
        cambiarDirGlobal(-1);
        mov.enMovimiento = false;
        mov.delay = 0;
      } else {
        mov.delay += 1;
        motorA('R', 150);
        motorB('A', 150);
      }
    }

    if (mov.dir == IZQUIERDA) {
      if (mov.delay > 10) {
        cambiarDirGlobal(1);
        mov.enMovimiento = false;
        mov.delay = 0;
      } else {
        mov.delay += 1;
        motorA('A', 150);
        motorB('R', 150);
      }
    }

    if (mov.dir == PARAR){
      mov.enMovimiento = false;
      mov.delay = 0;
    }

    delay(100);
  }

  motorA('P', 0);
  motorB('P', 0);
}
