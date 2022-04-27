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
  uint16_t time_hit; //When the alarm activates its callback (unit defined in onTimer)
  uint8_t outlet; //Which outlet the alarm refers to
  uint32_t repeat_period; //How oftern the timer repeats
  virt_alarm* end_post; //Either the ending timer or void
} virt_alarm;

const uint16_t TIMER_SCALAR = 40000; //Timer ticks every half a millisecond
const uint16_t SECOND = 80000000/TIMER_SCALAR; //Timer ticks in a second
const uint32_t TEN_MIN = 10*60*SECOND; //Timer ticks in 10 minutes
const uint64_t DAY = 24*60*60*SECOND; //Timer ticks in a day

hw_timer_t * timer = NULL;
volatile SemaphoreHandle_t timerSemaphore;
portMUX_TYPE timerMux = portMUX_INITIALIZER_UNLOCKED;
virt_alarm al_list[500];
uint32_t current_list = 0;
uint8_t day_offset = 0; //Changes every time a message is sent, used to place alarms
uint16_t state = 0; //Outlet state (MSB is outlet[9])
uint16_t permanence_toggle = 0; //Whether a pin is in a permanent state (MSB is outlet[9])
uint16_t permanent_state = 0; //What permanent state a pin should be at (MSB is outlet[9])
bool setting = false;

BLEServer *pServer = NULL;
BLEService *pService = NULL;
BLECharacteristic *pCharacteristic = NULL;
BLEAdvertising *pAdvertising = NULL;
uint32_t message;
const int outputs[10] = {15, 2, 0, 4, 16, 17, 5, 18, 19, 21};
//const int outputs[10] = {23, 22, 14, 32, 15, 33, 27, 12, 13, 21};

void IRAM_ATTR onTimer(){
  // Increment the counter and set the time of ISR
  portENTER_CRITICAL_ISR(&timerMux);
  Serial.print(millis()/1000);
  Serial.println(" Seconds");
  virt_alarm curr_alarm = al_pop();
  al_insert(curr_alarm.time_hit + curr_alarm.repeat_period, curr_alarm.outlet, curr_alarm.repeat_period, curr_alarm.end_post); 
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

  set_reset(curr_alarm.outlet, !(curr_alarm.end_post == NULL), &state);
  
  if (((permanence_toggle >> curr_alarm.outlet) & 1) == 0) {
    set_outlet_to_state(curr_alarm.outlet, state);
  }

  Serial.print("Outlets: ");
  for (int i = 0; i < sizeof(outputs)/sizeof(outputs[0]); i++){
    Serial.print(digitalRead(outputs[i]));
  } 
  Serial.println();
  Serial.println(curr_alarm.outlet);
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

        uint16_t blue_part = (message >> 2) & 0x3FF; //Usually outlet in binary
        uint16_t red_part = (message >> 12) & 0x3FF;
        uint16_t brown_part = (message >> 22) & 0x3FF;
        
        Serial.println(message, BIN);
        Serial.print("Outlet: ");
        Serial.println(blue_part);
        Serial.print("Red: ");
        Serial.println(red_part);
        Serial.print("Brown: ");
        Serial.println(brown_part);
        Serial.println("*********");

        virt_alarm end_post{0, 0, 10, NULL};
        virt_alarm start_post{0, 0, 10, &end_post};

        if ((message & 3) == 0) {
          reset_virt();
          day_offset = red_part;
        } else if ((message & 3) == 1) {
            start_post.repeat_period = red_part;
            start_post.outlet = blue_part;
        } else if ((message & 3) == 2) {
            start_post.outlet = blue_part;
            end_post.outlet = blue_part;
            if (red_part + day_time() + brown_part > 143) {
              
            } else {
              start_post.time_hit = red_part;
              end_post.time_hit = red_part + brown_part;
          }
        } else if ((message & 3) == 3) {
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
        Serial.println("Start Outlet: ");
        Serial.println(start_post.outlet);
        Serial.println("End Outlet: ");
        Serial.println(end_post.outlet);
        
        al_insert(start_post);
        al_insert(end_post);
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

virt_alarm* al_insert(uint32_t count, uint16_t outlet, uint32_t repeat_period, virt_alarm* end_post) {
  uint8_t pos = 0;
  virt_alarm* inserted = new virt_alarm{count, outlet, repeat_period, end_post};
  if (current_list == 0) {
    al_list[0] = *inserted;
    current_list++;
    return inserted;
  }
  for (size_t i = 0; i < current_list && al_list[i].time_hit < count; i++) {
    pos++;
  }
  for (size_t i = current_list; i > pos; i--) {
    al_list[i] = al_list[i - 1];
  }
  al_list[pos] = *inserted;
  current_list++;
  return inserted;
}

void al_insert(virt_alarm alarm) {
  al_insert(alarm.time_hit, alarm.outlet, alarm.repeat_period, alarm.end_post);
}

virt_alarm al_pop(void) {
  virt_alarm ret = al_list[0];
  for (size_t i = 0; i < current_list; i++) {
    al_list[i] = al_list[i + 1];
  }
  current_list --;
  return ret;
}

uint8_t day_time() {
  return (millis() * 2 / SECOND + day_offset) % 144;
}

void reset_virt() {
  current_list = 0;
  return;
}

void setup() {
  for (int i = 0; i < 10; i++){
    pinMode(outputs[i], OUTPUT);
  } 
  Serial.begin(115200);

  delay(10000);

  Serial.println("dies bruh");

  virt_alarm* end1 = al_insert(1, 8, 5, NULL);
  virt_alarm* end2 = al_insert(2, 7, 5, NULL);
  virt_alarm* end3 = al_insert(3, 6, 5, NULL);
  virt_alarm* end4 = al_insert(4, 5, 5, NULL);
  virt_alarm* start1 = al_insert(0, 8, 5, end1);
  virt_alarm* start2 = al_insert(0, 7, 5, end2);
  virt_alarm* start3 = al_insert(0, 6, 5, end3);
  virt_alarm* start4 = al_insert(0, 5, 5, end4);

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
  delay(10000);
}
