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
  uint16_t time_hit;
  uint8_t outlet;
  uint32_t pump_repeat;
  bool end_post;
  bool pump;
} virt_alarm;

const uint16_t TIMER_SCALAR = 40000; //Timer ticks every half a millisecond
const uint16_t SECOND = 80000000/TIMER_SCALAR;
const uint32_t TEN_MIN = 10*60*SECOND;
const uint64_t DAY = 24*60*60*SECOND; //Timer ticks in a day

hw_timer_t * timer = NULL;
volatile SemaphoreHandle_t timerSemaphore;
portMUX_TYPE timerMux = portMUX_INITIALIZER_UNLOCKED;
virt_alarm al_list[500];
uint32_t current_list = 0;
uint64_t ref_time = 0; //Offset for day_time
uint8_t day_time = 0; //Changes every time a message is sent, used to place alarms
uint16_t state = 0; //Outlet state (MSB is outlet[9])
uint16_t permanence_toggle = 0; //Whether a pin is in a permanent state (MSB is outlet[9])
uint16_t permanent_state = 0; //What permanent state a pin should be at (MSB is outlet[9])
bool setting = false;

BLEServer *pServer = NULL;
BLEService *pService = NULL;
BLECharacteristic *pCharacteristic = NULL;
BLEAdvertising *pAdvertising = NULL;
uint32_t message;
const int outputs[10] = {15, 2, 4, 16, 17, 5, 18, 19, 21, 20};
//const int outputs[10] = {23, 22, 14, 32, 15, 33, 27, 12, 13, 21};

void IRAM_ATTR onTimer(){
  // Increment the counter and set the time of ISR
  portENTER_CRITICAL_ISR(&timerMux);
  Serial.print(millis());
  Serial.println(" ms");
  virt_alarm curr_alarm = al_pop();
  uint8_t outlet = curr_alarm.outlet;
  if (curr_alarm.pump) {
    al_insert(curr_alarm.time_hit + curr_alarm.pump_repeat, outlet, curr_alarm.pump_repeat, curr_alarm.end_post, true);
  } else {
    al_insert(curr_alarm.time_hit + 20, outlet, 0, curr_alarm.end_post, false);
  }
  portEXIT_CRITICAL_ISR(&timerMux);
  // Give a semaphore that we can check in the loop
  //xSemaphoreGiveFromISR(timerSemaphore, NULL);

  /*
  if (curr_alarm.end_post) {
    state &= ~(1<<outlet);
  } else {
    state |= 1<<outlet;
  }
  */

  set_reset(outlet, !curr_alarm.end_post, &state);
  
  if (((permanence_toggle >> outlet) & 1) == 0) {
    set_outlet_to_state(outlet, state);
  }
  
  for (int i = 9; i >= 0; i--){
    Serial.print(digitalRead(outputs[i]));
  } 
  Serial.println();
  if (current_list > 0) {
    timerAlarmWrite(timer, al_list[0].time_hit * SECOND, false);
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
        message = 0;
        for (int i = 0; i < value.length(); i++) {
          message <<= 8;
          message |= value[i]; 
        }

        uint16_t blue_part = (message >> 2) & 0x3FF;
        uint16_t red_part = (message >> 12) & 0x3FF;
        uint16_t brown_part = (message >> 22) & 0x3FF;
        
        Serial.println(message, BIN);
        Serial.println("*********");

        virt_alarm start_post{0, 0,  0, false, false};
        virt_alarm end_post{0, 0,  0, true, false};

        uint32_t day_time = ((SECOND/1000) * millis()) % DAY;

        if (message & 3 == 0) {
          reset_virt();
        } else if (message & 3 == 1) {
          start_post.pump = true;
          start_post.pump_repeat = red_part;
          start_post.outlet = blue_part;
        } else if (message & 3 == 2) {
          start_post.outlet = blue_part;
          end_post.outlet = blue_part;
          start_post.time_hit = red_part;
          end_post.time_hit = red_part + brown_part;
        } else if (message & 3 == 3) {
          set_reset(blue_part, brown_part, &permanent_state);
          set_reset(blue_part, red_part, &permanence_toggle);
          //permanent_state = red_part;
          //permanence_toggle = blue_part;
          if ((permanence_toggle >> blue_part) & 1) {
            set_outlet_to_state(brown_part, permanent_state);
          } else {
            set_outlet_to_state(brown_part, state);
          }
          Serial.println(permanent_state, BIN);
          Serial.println(permanence_toggle, BIN);
          return;
        }
        al_insert(start_post);
        al_insert(end_post); //Change later to account for pumps
        }
      }
};

void set_reset(uint8_t outlet, bool set, uint16_t* changed){
  if (set) {
    *changed |= 1<<outlet;
  } else {
    *changed &= ~(1<<outlet);
  }
}

void set_outlet_to_state(uint16_t outlet, uint16_t state){
  digitalWrite(outputs[outlet], ((state >> outlet) & 1));
}

void al_insert(uint32_t count, uint16_t outlet, uint32_t pump_repeat, bool end_post, bool pump) {
  uint8_t pos = 0;
  virt_alarm inserted = virt_alarm{count, outlet, pump_repeat, end_post, pump};
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

void al_insert(virt_alarm alarm) {
  al_insert(alarm.time_hit, alarm.outlet, alarm.pump_repeat, alarm.end_post, alarm.pump);
}

virt_alarm al_pop(void) {
  virt_alarm ret = al_list[0];
  for (size_t i = 0; i < current_list; i++) {
    al_list[i] = al_list[i + 1];
  }
  current_list --;
  return ret;
}

void reset_virt() {
  ref_time = millis();
  current_list = 0;
  return;
}

void setup() {
  for (int i = 0; i < 10; i++){
    pinMode(outputs[i], OUTPUT);
  } 
  Serial.begin(115200);

  pinMode(11, OUTPUT);

  al_insert(4, 8, 0, false, false);
  al_insert(4, 7, 0, false, false);
  al_insert(4, 6, 0, false, false);
  al_insert(4, 5, 0, false, false);
  al_insert(8, 8, 0, true, false);
  al_insert(8, 7, 0, true, false);
  al_insert(8, 6, 0, true, false);
  al_insert(8, 5, 0, true, false);

  timerSemaphore = xSemaphoreCreateBinary();

  timer = timerBegin(0, TIMER_SCALAR, true);

  timerAttachInterrupt(timer, &onTimer, true);

  timerAlarmWrite(timer, al_list[0].time_hit * SECOND, false);

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
  //if (pServer->getConnectedCount() == 0) {
  //  pAdvertising->stop();
  //  pAdvertising->start();
  //  Serial.println("Restarting Advertising");
  //}
  digitalWrite(11, 1);
  delay(10000);
}
