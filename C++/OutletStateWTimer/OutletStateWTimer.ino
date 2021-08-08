
/*
    Based on Neil Kolban example for IDF: https://github.com/nkolban/esp32-snippets/blob/master/cpp_utils/tests/BLE%20Tests/SampleWrite.cpp
    Ported to Arduino ESP32 by Evandro Copercini
*/

#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEServer.h>

// See the following for generating UUIDs:
// https://www.uuidgenerator.net/

#define SERVICE_UUID        "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
#define CHARACTERISTIC_UUID "beb5483e-36e1-4688-b7f5-ea07361b26a8"

typedef struct virt_alarm {
  uint32_t time_hit;
  uint16_t state;
} virt_alarm;

hw_timer_t * timer = NULL;
volatile SemaphoreHandle_t timerSemaphore;
portMUX_TYPE timerMux = portMUX_INITIALIZER_UNLOCKED;
virt_alarm al_list[500];
uint32_t current_list = 0;

unsigned long myTime;

BLEServer *pServer = NULL;
BLEService *pService = NULL;
BLECharacteristic *pCharacteristic = NULL;
BLEAdvertising *pAdvertising = NULL;

uint32_t time_state;
const int outputs[10] = {34, 35, 32, 21, 19, 25, 18, 5, 27, 2};

void IRAM_ATTR onTimer(){
  // Increment the counter and set the time of ISR
  portENTER_CRITICAL_ISR(&timerMux);
  Serial.print(millis());
  Serial.println(" ms");
  uint16_t state = al_pop();
  portEXIT_CRITICAL_ISR(&timerMux);
  // Give a semaphore that we can check in the loop
  //xSemaphoreGiveFromISR(timerSemaphore, NULL);
  for (int i = 9; i>= 0; i--) {
    digitalWrite(outputs[9-i], ((state >> i) & 1));
  }
  for (int i = 0; i < 10; i++){
    Serial.print(digitalRead(outputs[i]));
  } 
  Serial.println();
  if (current_list > 0) {
    timerAlarmWrite(timer, al_list[0].time_hit, false);
    timerAlarmEnable(timer);
  }
  // It is safe to use digitalRead/Write here if you want to toggle an output
}

class MyCallbacks: public BLECharacteristicCallbacks {
    void onWrite(BLECharacteristic *pCharacteristic) {
      std::string value = pCharacteristic->getValue();

      if (value.length() > 0) {
        Serial.println("*********");
        Serial.print("New value: ");
        time_state = 0;
        
        for (int i = 0; i < value.length(); i++) {
          time_state <<= 8;
          time_state |= value[i]; 
        }

        Serial.println(time_state, BIN);

        uint16_t temp_state = time_state & 0x3FF;

        Serial.println();
        Serial.println("*********");
        
        uint32_t timed = time_state >> 10;
        Serial.println(timed);
        al_insert(timed, temp_state);
      }
    }
};

void al_insert(uint32_t count, uint16_t state) {
  uint8_t pos = 0;
  virt_alarm inserted = virt_alarm {count, state};
  if (current_list == 0) {
    al_list[0] = inserted;
    current_list++;
    return;
  }
  for (size_t i = 0; i < current_list && al_list[i].time_hit < count; i++) {
    pos++;
  }
  for (size_t i = current_list; i > pos; i--) {
    al_list[i] = al_list[i - 1];
  }
  al_list[pos] = inserted;
  current_list++;
}

uint16_t al_pop(void) {
  uint16_t ret = al_list[0].state;
  for (size_t i = 0; i < current_list; i++) {
    al_list[i] = al_list[i + 1];
  }
  current_list --;
  return ret;
} 

void setup() {
  for (int i = 0; i < 10; i++){
    pinMode(outputs[i], OUTPUT);
  } 
  Serial.begin(115200);

  al_insert(15000, 10);
  al_insert(100000, 4095);

  timerSemaphore = xSemaphoreCreateBinary();

  timer = timerBegin(0, 8000, true);

  timerAttachInterrupt(timer, &onTimer, true);
  Serial.println("huh?");

  timerAlarmWrite(timer, al_list[0].time_hit, false);

  // Start an alarm
  timerAlarmEnable(timer);

  BLEDevice::init("MyESP32");
  pServer = BLEDevice::createServer();

  pService = pServer->createService(SERVICE_UUID);

  pCharacteristic = pService->createCharacteristic(
                               CHARACTERISTIC_UUID,
                               BLECharacteristic::PROPERTY_READ |
                               BLECharacteristic::PROPERTY_WRITE
                             );

  pCharacteristic->setCallbacks(new MyCallbacks());

  pCharacteristic->setValue("Hello WOrld");
  pService->start();

  pAdvertising = pServer->getAdvertising();
  pAdvertising->start();
}

void loop() {
  if (pServer->getConnectedCount() == 0) {
    pAdvertising->stop();
    pAdvertising->start();
    Serial.println("Restarting Advertising");
  }
  delay(10000);
}
