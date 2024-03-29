w/*
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
  bool state; //1 when light is on, 0 when off
  bool permanent; //1 if light should be on in permanent mode, 0 if should be off
  bool permanence; //1 if permanently switched on or off, 0 if following schedule
} virt_alarm; 

const uint32_t TIMER_SCALAR = 40000; //Timer ticks every half a millisecond
const uint32_t SECOND = 80000000 / TIMER_SCALAR; //Timer ticks in a second
const uint32_t TENTH = SECOND / 10; //Timer ticks in a second
const uint32_t MIN = SECOND * 60; //Timer ticks in a second
const uint32_t TEN_MIN = 10 * SECOND; //Timer ticks in 10 minutes
const uint64_t DAY = 24 * 60 * 60 * SECOND; //Timer ticks in a day

const uint32_t SCALE = MIN;

const int outputs[16] = {22, 23, 25, 18, 26, 13, 12, 14, 27, 19, 15, 33, 4, 5, 32, 21};

hw_timer_t * timer = NULL;
volatile SemaphoreHandle_t timerSemaphore;
portMUX_TYPE timerMux = portMUX_INITIALIZER_UNLOCKED;
virt_alarm al_list[sizeof(outputs)/sizeof(outputs[0])]; //Initializes the array of alarms, amount equal to how many outputs there are
uint8_t simul[sizeof(outputs)/sizeof(outputs[0])] = {11}; //Array used to see which lights switch simultaneously (e.g. holds [1,6] if lights 1 and 6 need to toggle)
uint8_t extension[sizeof(outputs)/sizeof(outputs[0])] = {3}; //Array used to keep track of which timers need to be extended, with index being output number and holding 1 or 2
uint16_t day_offset = 0; //The offset from the start of the day (timers start at 0 time, but is not always sent at 12 am)
uint16_t next_time = 0; //The next timer value the timer goes off
uint8_t max_index; //Tells simul how many timers go off at the same time
uint32_t mods[2*sizeof(outputs)/sizeof(outputs[0])] = {0}; //Holds the number to be multiplied by 1440 (10 min-intervals in a day) for the absolute time
uint32_t mod = 0; //The smallest number in mods[]

BLEServer *pServer = NULL;
BLEService *pService = NULL;
BLECharacteristic *pCharacteristic = NULL;
BLEAdvertising *pAdvertising = NULL;
uint32_t message;

void IRAM_ATTR onTimer() {
  portENTER_CRITICAL_ISR(&timerMux);
  //Serial.println("Pog");
  if (simul[0] != 255) {
    for (int i = 0; i < sizeof(outputs)/sizeof(outputs[0]); i++){
      if (extension[i] == 1) { //If output i needs an extension at alarm 1
        (al_list[i].time_hit_1 += al_list[i].repeat_period); //Extend by the period
        if (al_list[i].time_hit_1 >= 1440) { //Change mods if needed
          mods[2*i]++;
          al_list[i].time_hit_1 %= 1440;
        }
      }
      else if (extension[i] == 2) { //Same logic as above applied to alarm 2
        (al_list[i].time_hit_2 += al_list[i].repeat_period);
        if (al_list[i].time_hit_2 >= 1440) {
          mods[2 * i + 1]++;
          al_list[i].time_hit_2 %= 1440;
        }
      }
    }
    mod = mods[0];
    for (int i = 0; i < 2*sizeof(outputs)/sizeof(outputs[0]); i++){
      mod = min(mods[i], mod); //Finds smallest mod 
    }
    for (int i = 0; i < max_index; i++){
      al_list[simul[i]].state = !al_list[simul[i]].state; //Toggles all simultaneous alarms
    }
    for (int i = 0; i < sizeof(outputs) / sizeof(outputs[0]); i++) {
      if (al_list[i].permanence) {
        digitalWrite(outputs[i], !al_list[i].permanent);
      }
      else {
        digitalWrite(outputs[i], !al_list[i].state);
      }
    }
  }/*
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
  for (int i = 0; i < 2*sizeof(outputs)/sizeof(outputs[0]); i++){
    Serial.print(mods[i]);
    Serial.print(" ");
  }
  Serial.println();
  Serial.print("Permanence: ");
  for (int i = 0; i < sizeof(outputs)/sizeof(outputs[0]); i++){
    Serial.print(al_list[i].permanence);
    Serial.print(" ");
  }*/
  max_index = find_closest_timer() + 1;
  /*
    Serial.println();
    Serial.print("Day Time: ");
    Serial.print(day_time());
    Serial.println();
    Serial.print("Next Time: ");
    Serial.print(next_time);
    Serial.println();
    Serial.print("Mod: ");
    Serial.print(mod);
    Serial.println();
  */
  portEXIT_CRITICAL_ISR(&timerMux);
  timerAlarmWrite(timer, ((mod * 1440) + next_time - day_offset) * SCALE, false);
  timerAlarmEnable(timer);
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
        //Documentation for his found on drive (bluetooth protocol)
        uint16_t blue_part = (message >> 2) & 0xFF; 
        uint16_t red_part = (message >> 10) & 0x7FF;
        uint16_t brown_part = (message >> 21) & 0x7FF;

        Serial.println(message, BIN);
        Serial.print("Outlet: ");
        Serial.println(blue_part);
        Serial.print("Red: ");
        Serial.println(red_part);
        Serial.print("Brown: ");
        Serial.println(brown_part);
        Serial.println("*********");

        if ((message & 3) == 0) {
          if (blue_part == 0) {
            Serial.println("Start Message Sent!");
            full_reset();
            day_offset = red_part;
            timerAlarmDisable(timer);
            timerRestart(timer);
            timerStop(timer);
          }
          if (blue_part == 1) {
            full_recombobulate();
            max_index = find_closest_timer() + 1;
            timerRestart(timer);
            timerAlarmWrite(timer, (next_time - day_offset) * SCALE, false);
            timerAlarmEnable(timer);
            Serial.println("Restarted!");
            Serial.println("Next time: ");
            Serial.print(next_time);
            Serial.println();
          }
        } else if ((message & 3) == 1) {
          timerAlarmDisable(timer);
          timerStop(timer);
          al_list[blue_part].time_hit_1 = (day_time() + 1) % 1440;
          al_list[blue_part].time_hit_2 = (red_part + day_time() + 1) % 1440;
          al_list[blue_part].repeat_period = red_part * 2;
          max_index = find_closest_timer() + 1;
          timerAlarmWrite(timer, (next_time - day_offset) * SCALE, false);
          timerAlarmEnable(timer);
          timerStart(timer);
        } else if ((message & 3) == 2) {
          timerAlarmDisable(timer);
          timerStop(timer);
          al_list[blue_part].time_hit_1 = red_part;
          Serial.print("Huh?");
          Serial.print(al_list[blue_part].time_hit_1);
          Serial.println();
          al_list[blue_part].time_hit_2 = (red_part + brown_part) % 1440;
          al_list[blue_part].repeat_period = 1440;
          recombobulate(blue_part);
          max_index = find_closest_timer() + 1;
          timerAlarmWrite(timer, (next_time - day_offset) * SCALE, false);
          timerAlarmEnable(timer);
          timerStart(timer);
        } else if ((message & 3) == 3) {
          al_list[blue_part].permanent = brown_part;
          al_list[blue_part].permanence = red_part;
          if (al_list[blue_part].permanence) {
            digitalWrite(outputs[blue_part], !al_list[blue_part].permanent);
          }
          Serial.print("Permanence: ");
          Serial.println(al_list[blue_part].permanence);
        }
      }
    }
};

uint32_t day_time() {
  uint32_t d_time = ((timerReadMicros(timer) / 1000) * 2 / SCALE) + day_offset; //Used as the relative counter based off day_offset's 0 time
  return d_time;
}

void reset_extension() {
  for (int i = 0; i < sizeof(outputs) / sizeof(outputs[0]); i++) {
    extension[i] = 0;
  }
}

uint8_t find_closest_timer() {
  uint16_t running_min = 1500; //Minutes in a day is 1440
  uint8_t index = 0;
  uint8_t max_index = 0;
  uint8_t alarm_index = sizeof(outputs) / sizeof(outputs[0]) + 1;
  simul[0] = 255;
  
  for (int i = 0; i < sizeof(outputs)/sizeof(outputs[0]); i++) {
    if (day_time() < al_list[i].time_hit_1 + 1440 * mods[2*i]) {
      if ((al_list[i].time_hit_1 + 1440 * mods[2*i] - day_time()) < running_min) { //If the turn on timer for this index comes sooner than the current next timer,
        index = 0;
        max_index = 0;
        reset_extension();
        alarm_index = i;
        next_time = al_list[i].time_hit_1;
        simul[index] = i; //Base of one "simultaneous" alarm being hit
        extension[i] = 1; //extend the activation timer
        running_min = al_list[i].time_hit_1 + 1440 * mods[2*i] - day_time(); //Shifts the time hit to be relative to our time system
      }
      else if ((al_list[i].time_hit_1 + 1440 * mods[2*i] - day_time()) == running_min) { //If the turn on timer for this index comes at the same time as the next timer
        index++;
        simul[index] = i; //Add the timer to the simul array
        extension[i] = 1; //Add the on timer to the list of timers that needs to be extended
      }
    }
    if (day_time() < al_list[i].time_hit_2 + 1440 * mods[2*i + 1]) {
      if ((al_list[i].time_hit_2 + 1440 * mods[2*i + 1] - day_time()) < running_min) { //Same logic as above, but for the turn off timer
        index = 0;
        max_index = 0;
        reset_extension();
        alarm_index = i;
        next_time = al_list[i].time_hit_2;
        simul[index] = i;
        extension[i] = 2;
        running_min = al_list[i].time_hit_2 + 1440 * mods[2 * i + 1] - day_time();
      }
      else if ((al_list[i].time_hit_2 + 1440 * mods[2 * i + 1] - day_time()) == running_min) {
        index++;
        simul[index] = i;
        extension[i] = 2;
      }
    }
    max_index = max(max_index, index); //max_index determines how many simultaneous timers are hit
  }
  return max_index;
}

void full_reset() {
  reset_extension();
  for (int i = 0; i < sizeof(outputs) / sizeof(outputs[0]); i++) {
    al_list[i].state = 0;
    digitalWrite(i, HIGH);
  }
  for (int i = 0; i < 2 * sizeof(outputs) / sizeof(outputs[0]); i++) {
    mods[i] = 0;
  }
  mod = 0;
}
//Nah this won't work
void recombobulate(uint8_t outlet){
  int32_t day_t = day_time();
  mods[2 * outlet + 1] = mod;
  mods[2 * outlet] = mod;
  if (day_t - al_list[outlet].time_hit_1 >= 0) {
    if (((day_t - al_list[outlet].time_hit_1) % al_list[outlet].repeat_period) < ((1440 + al_list[outlet].time_hit_2 - al_list[outlet].time_hit_1) % 1440) % al_list[outlet].repeat_period) {
      al_list[outlet].state = true;
      digitalWrite(outputs[outlet], !al_list[outlet].state);
    }
  }
  if ((day_t - al_list[outlet].time_hit_1) >= 0) {
    Serial.print(al_list[outlet].time_hit_1);
    Serial.println();
    al_list[outlet].time_hit_1 = (((day_t - al_list[outlet].time_hit_1) / al_list[outlet].repeat_period + 1) * al_list[outlet].repeat_period + al_list[outlet].time_hit_1);
    if (al_list[outlet].time_hit_1 >= 1440) {
      mods[2 * outlet]++;
    }
    al_list[outlet].time_hit_1 %= 1440;
  }
  if (al_list[outlet].time_hit_2 + 1440 * mods[2 * outlet + 1] <= al_list[outlet].time_hit_1 + 1440 * mods[2 * outlet]) {
    if (al_list[outlet].state) {
      while (al_list[outlet].time_hit_2 + al_list[outlet].repeat_period < al_list[outlet].time_hit_1 + 1440 * mods[2 * outlet]) {
        al_list[outlet].time_hit_2 += al_list[outlet].repeat_period;
      }
    } else {
      while (al_list[outlet].time_hit_2 < al_list[outlet].time_hit_1 + 1440 * mods[2 * outlet]) {
        al_list[outlet].time_hit_2 += al_list[outlet].repeat_period;
      }
    }
    mods[2 * outlet + 1] = al_list[outlet].time_hit_2 / 1440;
    al_list[outlet].time_hit_2 %= 1440;
  }
}

void full_recombobulate() {
  for (int i = 0; i < sizeof(outputs) / sizeof(outputs[0]); i++) {
    if (day_offset - al_list[i].time_hit_1 >= 0) {
      if (((day_offset - al_list[i].time_hit_1) % al_list[i].repeat_period) < ((1440 + al_list[i].time_hit_2 - al_list[i].time_hit_1) % 1440) % al_list[i].repeat_period) {
        al_list[i].state = true;
        digitalWrite(outputs[i], !al_list[i].state);
      }
    }
    if ((day_offset - al_list[i].time_hit_1) >= 0) {
      al_list[i].time_hit_1 = (((day_offset - al_list[i].time_hit_1) / al_list[i].repeat_period + 1) * al_list[i].repeat_period + al_list[i].time_hit_1);
      if (al_list[i].time_hit_1 >= 1440) {
        mods[2 * i]++;
      }
      al_list[i].time_hit_1 %= 1440;
    }
    if (al_list[i].time_hit_2 + 1440 * mods[2 * i + 1] <= al_list[i].time_hit_1 + 1440 * mods[2 * i]) {
      if (al_list[i].state) {
        while (al_list[i].time_hit_2 + al_list[i].repeat_period < al_list[i].time_hit_1 + 1440 * mods[2 * i]) {
          al_list[i].time_hit_2 += al_list[i].repeat_period;
        }
      } else {
        while (al_list[i].time_hit_2 < al_list[i].time_hit_1 + 1440 * mods[2 * i]) {
          al_list[i].time_hit_2 += al_list[i].repeat_period;
        }
      }
      mods[2 * i + 1] = al_list[i].time_hit_2 / 1440;
      al_list[i].time_hit_2 %= 1440;
    }
  }
  mod = mods[0];
  for (int i = 0; i < 2 * sizeof(outputs) / sizeof(outputs[0]); i++) {
    mod = min(mods[i], mod);
  }
}

void setup() {
  Serial.begin(115200);
  Serial.println("Beginning!");

  for (int i = 0; i < sizeof(outputs) / sizeof(outputs[0]); i++) {
    pinMode(outputs[i], OUTPUT);
    digitalWrite(outputs[i], HIGH);
  }

  timerSemaphore = xSemaphoreCreateBinary();

  timer = timerBegin(0, TIMER_SCALAR, true);

  timerAttachInterrupt(timer, &onTimer, true);

  al_list[0] = virt_alarm{(int32_t)0, (int32_t)10, (int32_t)50, false, false, false};
  al_list[1] = virt_alarm{(int32_t)0, (int32_t)20, (int32_t)50, false, false, false};
  al_list[2] = virt_alarm{(int32_t)0, (int32_t)30, (int32_t)50, false, false, false};
  al_list[3] = virt_alarm{(int32_t)30, (int32_t)40, (int32_t)50, false, false, false};
  al_list[4] = virt_alarm{(int32_t)40, (int32_t)50, (int32_t)50, false, false, false};
  al_list[5] = virt_alarm{(int32_t)10, (int32_t)20, (int32_t)50, false, false, false};
  al_list[6] = virt_alarm{(int32_t)10, (int32_t)30, (int32_t)50, false, false, false};
  al_list[7] = virt_alarm{(int32_t)10, (int32_t)40, (int32_t)50, false, false, false};
  al_list[8] = virt_alarm{(int32_t)10, (int32_t)45, (int32_t)50, false, false, false};
  al_list[9] = virt_alarm{(int32_t)10, (int32_t)50, (int32_t)50, false, false, false};
  al_list[10] = virt_alarm{(int32_t)20, (int32_t)25, (int32_t)50, false, false, false};
  al_list[11] = virt_alarm{(int32_t)20, (int32_t)30, (int32_t)50, false, false, false};
  al_list[12] = virt_alarm{(int32_t)20, (int32_t)35, (int32_t)50, false, false, false};
  al_list[13] = virt_alarm{(int32_t)20, (int32_t)40, (int32_t)50, false, false, false};
  al_list[14] = virt_alarm{(int32_t)20, (int32_t)45, (int32_t)50, false, false, false};
  al_list[15] = virt_alarm{(int32_t)30, (int32_t)50, (int32_t)50, false, false, false};

  day_offset = 30;
  full_recombobulate();

  max_index = find_closest_timer() + 1;

  Serial.print("next time: ");
  Serial.println(next_time);

  Serial.print("day time: ");
  Serial.println(day_time() % 1440);

  timerAlarmWrite(timer, ((mod * 1440) + next_time - day_offset) * SCALE, false);

  // Start an alarm
  timerAlarmEnable(timer);
  Serial.println(timerReadSeconds(timer));

  BLEDevice::init("AutoAquaponicsOutleBox");
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
    timerAlarmWrite(timer, (next_time - day_offset) * SCALE, false);
    timerAlarmEnable(timer);
    timerStart(timer);
    Serial.print("Next time: ");
    Serial.print(mod * 1440);
    Serial.print('+');
    Serial.println(next_time);
    Serial.println(timerReadSeconds(timer));*/
}
