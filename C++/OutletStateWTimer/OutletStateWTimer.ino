
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
  uint8_t time_hit;
  uint16_t state;
} virt_alarm;

typedef struct schedule {
  uint8_t time_hit;
  uint16_t state;
  char repeat;
} schedule;

const uint64_t DAY = ;
const uint64_t WEEK = ;
const uint16_t TIMER_SCALAR = ;

hw_timer_t * timer = NULL;
volatile SemaphoreHandle_t timerSemaphore;
portMUX_TYPE timerMux = portMUX_INITIALIZER_UNLOCKED;
virt_alarm al_list[500];
schedule daily_schedule[200];
uint32_t current_list = 0;
uint64_t ref_time = millis();
uint8_t week_time = 0;
uint8_t day_time = 0;
uint8_t scheduled = 0;
uint16_t permanence_toggle = 0;
uint16_t permanent_state = 0;

unsigned long myTime;

BLEServer *pServer = NULL;
BLEService *pService = NULL;
BLECharacteristic *pCharacteristic = NULL;
BLEAdvertising *pAdvertising = NULL;

uint64_t time_state;
const int outputs[10] = {12, 13, 14, 15, 16, 17, 18, 19, 20, 21};

void IRAM_ATTR onTimer(){
  // Increment the counter and set the time of ISR
  portENTER_CRITICAL_ISR(&timerMux);
  Serial.print(millis());
  Serial.println(" ms");
  curr_alarm = al_pop();
  uint16_t state = curr_alarm.state;
  al_insert(curr_alarm.time_hit + DAY, state);
  portEXIT_CRITICAL_ISR(&timerMux);
  // Give a semaphore that we can check in the loop
  //xSemaphoreGiveFromISR(timerSemaphore, NULL);
  for (int i = 9; i>= 0; i--) {
    if ((permanence_toggle >> i) & 1 == 0) {
      digitalWrite(outputs[9-i], ((state >> i) & 1));
    }
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

        uint16_t outlet_state = (time_state >> 2) & 0x3FF;
        
        Serial.println();
        Serial.println("*********");

        uint16_t timed;
        char repeat;
        bool setting = false;

        if (time_state & 3 == 1) {
          repeat = 'w';
          timed = (time_state >> 12) & 0x3FF;
          setting = true
        } else if (time_state & 3 == 2) {
          repeat = 'd';
          timed = (time_state >> 12) & 0xFF;
          setting = true;
        } else if (time_state & 3 == 3) {
          permanence_toggle = outlet_state
          permanent_state = (time_state >> 12) & 0x3FF;
          digitalWrite(outputs[9-i], ((permanent_state >> i) & 1));
        } else {
          
        }

        week_time = timed >> 22 & 0x3FF;
        day_time = week_time % 144;
        Serial.println(timed);
        if (setting) {
          schedule_insert(timed, outlet_state, repeat);
          //timed *= 600000; //every 10 minutes
          al_insert(timed, outlet_state);
        }
      }
    }
};

void al_insert(uint16_t count, uint16_t state) {
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

<<<<<<< HEAD
void schedule_insert(uint8_t time_hit, uint16_t state, char repeat) {
  uint8_t pos = 0;
  schedule inserted = schedule {time_hit, state, repeat};
  if (current_schedule == 0) {
    daily_schedule[0] = inserted;
    scheduled++;
    return;
  }
  for (size_t i = 0; i < scheduled && daily_schedule[i].time_hit < count; i++) {
    pos++;
  }
  for (size_t i = scheduled; i > pos; i--) {
    daily_schedule[i] = daily_schedule[i - 1];
  }
  daily_schedule[pos] = inserted;
  scheduled++;
}

virt_alarm al_pop(void) {
  virt_alarm ret = al_list[0];
  for (size_t i = 0; i < current_list; i++) {
    al_list[i] = al_list[i + 1];
  }
  current_list --;
  return ret;
}

void schedule_remove(uint16_t time_hit) {
  uint16_t removal_index = 65536
  for (size_t i = 0; i < schdeuled; i++) {
    if daily_schedule[i].time_hit == time_hit {
      uint16_t removal_index = i;
    }
  }
  if (removal_index == 65536) {
    return;
  }
  for (size_t i = removal_index; i < scheduled; i++) {
    daily_schedule[i] = daily_schedule[i + 1];
  }
  scheduled--;
}

void reset_virt() {
  ref_time = millis();
  current_list = 0;
  //reset the timer lsit somehow
  for (int i = 0; i < scheduled; i++) {
    al_insert(ref_time + scheduled[i].time_hit, scheduled[i].state);
  }
  return;
}

void setup() {
  for (int i = 0; i < 10; i++){
    pinMode(outputs[i], OUTPUT);
  } 
  Serial.begin(115200);

  al_insert(15000, 10);
  al_insert(100000, 127);

  timerSemaphore = xSemaphoreCreateBinary();

  timer = timerBegin(0, 8000, true);

  timerAttachInterrupt(timer, &onTimer, true);

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
