#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>

Adafruit_MPU6050 mpu;
Adafruit_MPU6050 mpu2;

unsigned long tiempoActual=0, tiempoAnterior=0, snapShot=0;
unsigned int  intervaloDeTiempo = 100;

char dato;
int Modo = 0;
bool stateLed = 0;

void iniciarSensor(Adafruit_MPU6050 *sensor, uint8_t direccion){
  if (!sensor->begin(direccion)) {
    Serial.println("Failed to find MPU6050 chip");
    pinMode(LED_BUILTIN, OUTPUT);
    bool state = 0;
    while (1) {
      digitalWrite(LED_BUILTIN, !state);
      delay(100);
    }
  }
}

void configurarSensor(Adafruit_MPU6050 *sensor){
  sensor->setAccelerometerRange(MPU6050_RANGE_8_G);
  Serial.print("Accelerometer range set to: ");
  switch (sensor->getAccelerometerRange()) {
  case MPU6050_RANGE_2_G:
    Serial.println("+-2G");
    break;
  case MPU6050_RANGE_4_G:
    Serial.println("+-4G");
    break;
  case MPU6050_RANGE_8_G:
    Serial.println("+-8G");
    break;
  case MPU6050_RANGE_16_G:
    Serial.println("+-16G");
    break;
  }
  sensor->setGyroRange(MPU6050_RANGE_500_DEG);
  Serial.print("Gyro range set to: ");
  switch (sensor->getGyroRange()) {
  case MPU6050_RANGE_250_DEG:
    Serial.println("+- 250 deg/s");
    break;
  case MPU6050_RANGE_500_DEG:
    Serial.println("+- 500 deg/s");
    break;
  case MPU6050_RANGE_1000_DEG:
    Serial.println("+- 1000 deg/s");
    break;
  case MPU6050_RANGE_2000_DEG:
    Serial.println("+- 2000 deg/s");
    break;
  }

  sensor->setFilterBandwidth(MPU6050_BAND_21_HZ);
  Serial.print("Filter bandwidth set to: ");
  switch (sensor->getFilterBandwidth()) {
  case MPU6050_BAND_260_HZ:
    Serial.println("260 Hz");
    break;
  case MPU6050_BAND_184_HZ:
    Serial.println("184 Hz");
    break;
  case MPU6050_BAND_94_HZ:
    Serial.println("94 Hz");
    break;
  case MPU6050_BAND_44_HZ:
    Serial.println("44 Hz");
    break;
  case MPU6050_BAND_21_HZ:
    Serial.println("21 Hz");
    break;
  case MPU6050_BAND_10_HZ:
    Serial.println("10 Hz");
    break;
  case MPU6050_BAND_5_HZ:
    Serial.println("5 Hz");
    break;
  }
}


void setup() {
  pinMode(13, OUTPUT);
  delay(1000);
  Serial.begin(115200);

  // Try to initialize!
  iniciarSensor(&mpu, 0x68);
  iniciarSensor(&mpu2, 0x69);
  Serial.println("Acelerometros Encontrados");
  
  configurarSensor(&mpu);
  configurarSensor(&mpu2);

  Serial.println("");
  delay(100);
  
  Serial.print("\n\nSensor de Aceleracion Principal:\n");
  Serial.print("Presione:\nS:\tIniciar\nT:\tParar");
  Serial.println("\nC:\tTiempo de muestreo en ms");

}

bool cambiarMuestras(){
  if(Serial.available()>0){
    unsigned int tiempoMuestras = Serial.parseInt();

    if (tiempoMuestras > 4 &&  tiempoMuestras <= 1500){
      intervaloDeTiempo = tiempoMuestras;
      Serial.print("Intervalo de tiempo Cambiado a: "); 
      Serial.println(intervaloDeTiempo);
      return true;
    }
    else{
      Serial.println("Error cambiando el tiempo, intente nuevamente");
    }
  }
  return false;
}

void tomarDatos(){
  /* Get new sensor events with the readings */
  sensors_event_t a, g, temp;
  sensors_event_t a2, g2, temp2;
  
  mpu.getEvent(&a, &g, &temp);
  mpu2.getEvent(&a2, &g2, &temp2);


  Serial.print(millis() - snapShot); Serial.print(",\t"); Serial.print(a.acceleration.x);
  Serial.print(",\t"); Serial.print(a2.acceleration.x); Serial.println();

}

void loop() {
  if(Serial.available() > 0){
    dato = Serial.read();
    if(dato == 'S' || dato == 's'){
      //Tomar un SnapShot del tiempo
      snapShot = millis();
      Modo = 1;
    }
    else if(dato == 'T' || dato == 't'){
      Modo = 0;
    }
    else if(dato == 'C' || dato == 'c'){
      Modo = 2;
    }
    
  }

  if( Modo == 2){
    digitalWrite(13, HIGH);
    while(!cambiarMuestras());
    Serial.println("Correctamente");
    digitalWrite(13, LOW);
    Modo = 0;
  }
  else if( Modo == 1){
    tiempoActual = millis();
    if(tiempoActual - tiempoAnterior >= intervaloDeTiempo){
      tomarDatos();
      stateLed = !stateLed;
      digitalWrite(13, stateLed);
      tiempoAnterior = tiempoActual;
    }
  }
}

