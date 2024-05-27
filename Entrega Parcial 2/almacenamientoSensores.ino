#include "Arduino.h"
#include "DHT.h"
#include "NewPing.h"
#include <ArduinoJson.h>
#include <SD.h>
#include <SPI.h>

// Declaración de pines
#define DHT_PIN_DATA 2
#define HCSR04_PIN_TRIG 4
#define HCSR04_PIN_ECHO 3
#define MQ135_PIN A5
#define SD_CS_PIN 10

// Definición de variables globales
DHT dht(DHT_PIN_DATA, DHT22);
NewPing hcsr04(HCSR04_PIN_TRIG, HCSR04_PIN_ECHO);
const int alarm = 10;
long distance;
float temperature;
float humidity;
int airQuality;
File dataFile;

const int dataSize = 10; // Tamaño de los arrays de datos
long distanceData[dataSize];
float temperatureData[dataSize];
float humidityData[dataSize];
int airQualityData[dataSize];
int dataIndex = 0; // Índice para los arrays de datos


void setup() {
    Serial.begin(9600);

    // Inicializa sensores
    dht.begin();
    pinMode(alarm, OUTPUT);

    // Inicializa tarjeta SD
    if (!SD.begin(SD_CS_PIN)) {
        Serial.println("SD card initialization failed!");
        return;
    }
    Serial.println("SD card initialized.");

    // Crear o abrir el archivo
    dataFile = SD.open("sensores_datos.json", FILE_WRITE);
    if (!dataFile) {
        Serial.println("Error opening file for writing.");
    }
}

void loop() {
    // Leer la distancia
    distance = hcsr04.ping_cm();
    Serial.print("Distance: ");
    Serial.print(distance);
    Serial.println(" cm");

    // Leer temperatura y humedad
    humidity = dht.readHumidity();
    temperature = dht.readTemperature();
    Serial.print("Humidity: ");
    Serial.print(humidity);
    Serial.print(" %\t");
    Serial.print("Temperature: ");
    Serial.print(temperature);
    Serial.println(" °C");

    // Leer calidad del aire
    airQuality = analogRead(MQ135_PIN);
    Serial.print("Air Quality: ");
    Serial.println(airQuality);

    // Controlar alarma basándose en la calidad del aire
    if (airQuality < 930) {
        noTone(alarm);
        Serial.println("Air Quality: Safe");
    } else if (airQuality >= 930 && airQuality < 960) {
        noTone(alarm);
        Serial.println("Air Quality: Warning");
    } else { 
        tone(alarm, 440);
        Serial.println("Air Quality: Danger");
    }

    // Almacenar los datos en los arrays
    distanceData[dataIndex] = distance;
    airQualityData[dataIndex] = airQuality;
    temperatureData[dataIndex] = temperature;
    humidityData[dataIndex] = humidity;
    dataIndex++;

    // Verificar si el array de datos está lleno
    if (dataIndex >= dataSize) {
        // Crear el documento JSON
        StaticJsonDocument<2048> doc;
        JsonArray sensors = doc.to<JsonArray>();

        // Agregar datos de ultrasonido
        JsonObject ultrasonicSensor = sensors.createNestedObject();
        ultrasonicSensor["sensor"] = "ultrasonido";
        JsonArray ultrasonicData = ultrasonicSensor.createNestedArray("datos");
        for (int i = 0; i < dataSize; i++) {
            ultrasonicData.add(distanceData[i]);
        }

        // Agregar datos de calidad de aire
        JsonObject airQualitySensor = sensors.createNestedObject();
        airQualitySensor["sensor"] = "calidad_aire";
        JsonArray airQualityJsonArray = airQualitySensor.createNestedArray("datos");
        for (int i = 0; i < dataSize; i++) {
            airQualityJsonArray.add(airQualityData[i]);
        }

        // Agregar datos de humedad y temperatura
        JsonObject humidityTemperatureSensor = sensors.createNestedObject();
        humidityTemperatureSensor["sensor"] = "humedad_temperatura";
        JsonArray humidityTemperatureData = humidityTemperatureSensor.createNestedArray("datos");
        for (int i = 0; i < dataSize; i++) {
            JsonObject htData = humidityTemperatureData.createNestedObject();
            htData["temperatura"] = temperatureData[i];
            htData["humedad"] = humidityData[i];
        }

        // Serializar el documento JSON y escribir en el archivo
        if (dataFile) {
            serializeJson(doc, dataFile);
            dataFile.println();
            dataFile.flush();
        } else {
            Serial.println("Error writing to file.");
        }

        // Reiniciar el índice de datos
        dataIndex = 0;
    }

    delay(500);
}
