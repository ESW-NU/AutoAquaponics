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
  int32_t time_hit_1; //When the alarm activates a light (unit defined in onTimer)
  int32_t time_hit_2; //When the alarm deactivates a light
  uint16_t repeat_period; //How oftern the timer repeats
  bool state;
  bool permanent;
  bool permanence;
} virt_alarm; 

const uint32_t TIMER_SCALAR = 40000; //Timer ticks every half a millisecond
const uint32_t SECOND = 80000000/TIMER_SCALAR; //Timer ticks in a second
const uint32_t TENTH = SECOND/100; //Timer ticks in a second
const uint32_t TEN_MIN = 10*60*SECOND; //Timer ticks in 10 minutes
const uint64_t DAY = 24*60*60*SECOND; //Timer ticks in a day

hw_timer_t * timer = NULL;
volatile SemaphoreHandle_t timerSemaphore;
portMUX_TYPE timerMux = portMUX_INITIALIZER_UNLOCKED;
virt_alarm al_list[10];
uint8_t simul[10] = {11};
uint8_t extension[10] = {3};
uint16_t day_offset = 0; //Changes every time a message is sent, used to place alarms
uint32_t prev_time = 0;
uint16_t next_time = 0;
uint8_t max_index;
uint32_t mods[20] = {0};
uint32_t mod = 0;

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
  if (simul[0] != 255) {
    for (int i = 0; i < sizeof(outputs)/sizeof(outputs[0]); i++){
      if (extension[i] == 1) {
        (al_list[i].time_hit_1 += al_list[i].repeat_period);
        if (al_list[i].time_hit_1 >= 1440) {
          mods[2*i]++;
          al_list[i].time_hit_1 %= 1440;
        }
      }
      else if (extension[i] == 2) {
        (al_list[i].time_hit_2 += al_list[i].repeat_period);
        if (al_list[i].time_hit_2 >= 1440) {
          mods[2*i + 1]++;
          al_list[i].time_hit_2 %= 1440;
        }
      }
    }
    mod = mods[0];
    for (int i = 0; i < 20; i++){
      mod = min(mods[i], mod);
    }
    Serial.println();
    Serial.print("Extension: ");
    for (int i = 0; i < sizeof(outputs)/sizeof(outputs[0]); i++){
      Serial.print(extension[i]);
    }
    Serial.println();
    for (int i = 0; i < max_index; i++){
      al_list[simul[i]].state = !al_list[simul[i]].state; 
    }
    for (int i = 0; i < sizeof(outputs)/sizeof(outputs[0]); i++){
      if (al_list[i].permanence == 1){
        digitalWrite(outputs[i], al_list[i].permanent);
      }
      else{
        digitalWrite(outputs[i], al_list[i].state); 
      }
    }
  }
  max_index = find_closest_timer() + 1;
  portEXIT_CRITICAL_ISR(&timerMux);
  Serial.print("Outlets: ");
  for (int i = 0; i < sizeof(outputs)/sizeof(outputs[0]); i++){
    Serial.print(digitalRead(outputs[i]));
  }
  Serial.println();
  Serial.print("Hit 1: ");
  for (int i = 0; i < sizeof(outputs)/sizeof(outputs[0]); i++){
    Serial.print(al_list[i].time_hit_1);
    Serial.print(" ");
  }
  Serial.println();
  Serial.print("Hit 2: ");
  for (int i = 0; i < sizeof(outputs)/sizeof(outputs[0]); i++){
    Serial.print(al_list[i].time_hit_2);
    Serial.print(" ");
  }
  Serial.println();
  Serial.print("State: ");
  for (int i = 0; i < sizeof(outputs)/sizeof(outputs[0]); i++){
    Serial.print(al_list[i].state);
    Serial.print(" ");
  }
  Serial.println();
  Serial.print("Mods: ");
  for (int i = 0; i < 20; i++){
    Serial.print(mods[i]);
    Serial.print(" ");
  }
  Serial.println();
  Serial.print("Permanence: ");
  for (int i = 0; i < sizeof(outputs)/sizeof(outputs[0]); i++){
    Serial.print(al_list[i].permanence);
    Serial.print(" ");
  }
  Serial.println();
  Serial.print("day time: ");
  Serial.println(day_time() % 1440);
  timerAlarmWrite(timer, ((mod * 1440) + next_time - day_offset) * TENTH, false);
  timerAlarmEnable(timer);
  Serial.print("Next time: ");
  Serial.print(mod * 1440);
  Serial.print('+');
  Serial.println(next_time);
  Serial.println(timerAlarmReadSeconds(timer));
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

        if ((message & 3) == 0) {
          if (red_part == 0){
            Serial.println("Start Message Sent!");
            full_reset();
            day_offset = blue_part;
            timerAlarmDisable(timer);
            timerRestart(timer);
            timerStop(timer);
          }
          if (red_part == 1){
            full_recombobulate();
            max_index = find_closest_timer() + 1;
            timerRestart(timer);
            timerAlarmWrite(timer, (next_time - day_offset) * TENTH, false);
            timerAlarmEnable(timer);
          }
        } else if ((message & 3) == 1) {
          al_list[blue_part].time_hit_1 = 0;
          al_list[blue_part].time_hit_2 = red_part;
          al_list[blue_part].repeat_period = red_part * 2;
        } else if ((message & 3) == 2) {
          al_list[blue_part].time_hit_1 = red_part;
          al_list[blue_part].time_hit_2 = (red_part + brown_part) % 1440;
          al_list[blue_part].repeat_period = 1440;
        } else if ((message & 3) == 3) {
          al_list[blue_part].permanent = brown_part;
          al_list[blue_part].permanence = red_part;
          if (al_list[blue_part].permanence) {
            digitalWrite(outputs[blue_part], al_list[blue_part].permanent);
          }
          Serial.print("Permanence: ");
          Serial.println(al_list[blue_part].permanence);
        }
        Serial.println("Start Outlet: ");
        Serial.println("End Outlet: ");
        }
      }
};

uint32_t day_time() {
  uint32_t d_time = ((timerReadMicros(timer) / 1000) * 2 / TENTH) + day_offset;
  return d_time;
}

void reset_extension() {
  for (int i = 0; i < sizeof(outputs)/sizeof(outputs[0]); i++) {
    extension[i] = 0;
  }
}

uint8_t find_closest_timer() {
  uint16_t running_min = 1500; //Minutes in a day is 1440
  uint8_t index = 0;
  uint8_t max_index = 0;
  uint8_t alarm_index = 11;
  simul[0] = 255;
  
  for (int i = 0; i < sizeof(outputs)/sizeof(outputs[0]); i++) {
    if (day_time() < al_list[i].time_hit_1 + 1440 * mods[2*i]) {
      if ((al_list[i].time_hit_1 + 1440 * mods[2*i] - day_time()) < running_min) {
        index = 0;
        max_index = 0;
        reset_extension();
        alarm_index = i;
        next_time = al_list[i].time_hit_1;
        simul[index] = i;
        extension[i] = 1;
        running_min = al_list[i].time_hit_1 + 1440 * mods[2*i] - day_time();
      }
      else if ((al_list[i].time_hit_1 + 1440 * mods[2*i] - day_time()) == running_min) {
        index++;
        simul[index] = i;
        extension[i] = 1;
      }
    }
    if (day_time() < al_list[i].time_hit_2 + 1440 * mods[2*i + 1]) {
      if ((al_list[i].time_hit_2 + 1440 * mods[2*i + 1] - day_time()) < running_min) {
        index = 0;
        max_index = 0;
        reset_extension();
        alarm_index = i;
        next_time = al_list[i].time_hit_2;
        simul[index] = i;
        extension[i] = 2;
        running_min = al_list[i].time_hit_2 + 1440 * mods[2*i + 1] - day_time();
      }
      else if ((al_list[i].time_hit_2 + 1440 * mods[2*i + 1] - day_time()) == running_min) {
        index++;
        simul[index] = i;
        extension[i] = 2;
      }
    }
    max_index = max(max_index, index);
  }
  return max_index;
}

void full_reset() {
  reset_extension();
  for (int i = 0; i < sizeof(outputs)/sizeof(outputs[0]); i++){
    al_list[i].state = 0;
    digitalWrite(i, LOW);
  }
  for (int i = 0; i < 20; i++) {
    mods[i] = 0;
  }
  mod = 0;
}

void full_recombobulate(){
  for (int i = 0; i < sizeof(outputs)/sizeof(outputs[0]); i++) {
    if (al_list[i].time_hit_2 < al_list[i].time_hit_1) {
      mods[2*i+1]++;
    }
    if (day_offset - al_list[i].time_hit_1 >= 0){
      if(((day_offset - al_list[i].time_hit_1) % al_list[i].repeat_period) < ((1440 + al_list[i].time_hit_2 - al_list[i].time_hit_1) % 1440) % al_list[i].repeat_period) {
        al_list[i].state = true;
        digitalWrite(outputs[i], al_list[i].state);
      }
    }
    if ((day_offset - al_list[i].time_hit_1) >= 0) {
      al_list[i].time_hit_1 = (((day_offset - al_list[i].time_hit_1) / al_list[i].repeat_period + 1) * al_list[i].repeat_period + al_list[i].time_hit_1);
      if (al_list[i].time_hit_1 >= 1440) {
        mods[2*i]++;
      }
      al_list[i].time_hit_1 %= 1440;
    }
    if (al_list[i].time_hit_2 + 1440 * mods[2*i+1] <= al_list[i].time_hit_1 + 1440 * mods[2*i]) {
      if (al_list[i].state) {
        while (al_list[i].time_hit_2 + al_list[i].repeat_period < al_list[i].time_hit_1 + 1440 * mods[2*i]) {
          al_list[i].time_hit_2 += al_list[i].repeat_period;
        }
      } else {
        while (al_list[i].time_hit_2 < al_list[i].time_hit_1 + 1440 * mods[2*i]) {
          al_list[i].time_hit_2 += al_list[i].repeat_period;
        }
      }
      mods[2*i+1] = al_list[i].time_hit_2 / 1440;
      al_list[i].time_hit_2 %= 1440;
    }
  }
  mod = mods[0];
  for (int i = 0; i < 20; i++){
    mod = min(mods[i], mod);
  } 
}

void setup() {
  Serial.begin(115200);
  Serial.println("Beginning!");

  for (int i = 0; i < sizeof(outputs)/sizeof(outputs[0]); i++){
    pinMode(outputs[i], OUTPUT);
  } 

  timerSemaphore = xSemaphoreCreateBinary();

  timer = timerBegin(0, TIMER_SCALAR, true);

  timerAttachInterrupt(timer, &onTimer, true);

  al_list[0] = virt_alarm{(int32_t)0, (int32_t)100, (int32_t)1000, false, false, false};
  al_list[1] = virt_alarm{(int32_t)0, (int32_t)200, (int32_t)1000, false, false, false};
  al_list[2] = virt_alarm{(int32_t)0, (int32_t)300, (int32_t)1000, false, false, false};
  al_list[3] = virt_alarm{(int32_t)300, (int32_t)400, (int32_t)1000, false, false, false};
  al_list[4] = virt_alarm{(int32_t)400, (int32_t)500, (int32_t)1000, false, false, false};
  al_list[5] = virt_alarm{(int32_t)1000, (int32_t)1100, (int32_t)500, false, false, false};
  al_list[6] = virt_alarm{(int32_t)1100, (int32_t)1200, (int32_t)500, false, false, false};
  al_list[7] = virt_alarm{(int32_t)1200, (int32_t)1300, (int32_t)500, false, false, false};
  al_list[8] = virt_alarm{(int32_t)1300, (int32_t)1400, (int32_t)500, false, false, false};
  al_list[9] = virt_alarm{(int32_t)1400, (int32_t)60, (int32_t)500, false, false, false};

  day_offset = 1100;
  full_recombobulate();

  max_index = find_closest_timer() + 1;

  Serial.print("next time: ");
  Serial.println(next_time);

  Serial.print("day time: ");
  Serial.println(day_time() % 1440);

  timerAlarmWrite(timer, ((mod * 1440) + next_time - day_offset) * TENTH, false);

  // Start an alarm
  timerAlarmEnable(timer);
  Serial.println(timerReadSeconds(timer));

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
  /*delay(15000);
  Serial.println("Restarting!");
  Serial.println(prev_time);
  full_reset();
  timerAlarmDisable(timer);
  timerRestart(timer);
  timerStop(timer);
  delay(2000);
  al_list[0] = virt_alarm{(int32_t)0, (int32_t)100, (int32_t)1000, false, false, false};
  al_list[1] = virt_alarm{(int32_t)0, (int32_t)200, (int32_t)1000, false, false, false};
  al_list[2] = virt_alarm{(int32_t)0, (int32_t)300, (int32_t)1000, false, false, false};
  al_list[3] = virt_alarm{(int32_t)300, (int32_t)400, (int32_t)1000, false, false, false};
  al_list[4] = virt_alarm{(int32_t)400, (int32_t)500, (int32_t)1000, false, false, false};
  al_list[5] = virt_alarm{(int32_t)1000, (int32_t)1100, (int32_t)500, false, false, false};
  al_list[6] = virt_alarm{(int32_t)1100, (int32_t)1200, (int32_t)500, false, false, false};
  al_list[7] = virt_alarm{(int32_t)1200, (int32_t)1300, (int32_t)500, false, false, false};
  al_list[8] = virt_alarm{(int32_t)1300, (int32_t)1400, (int32_t)500, false, false, false};
  al_list[9] = virt_alarm{(int32_t)1400, (int32_t)60, (int32_t)500, false, false, false};
  full_recombobulate();
  max_index = find_closest_timer() + 1;
  Serial.println();
  Serial.print("day time: ");
  Serial.println(day_time() % 1440);
  timerRestart(timer);
  timerAlarmWrite(timer, (next_time - day_offset) * TENTH, false);
  timerAlarmEnable(timer);
  timerStart(timer);
  Serial.print("Next time: ");
  Serial.print(mod * 1440);
  Serial.print('+');
  Serial.println(next_time);
  Serial.println(timerReadSeconds(timer));*/
}
