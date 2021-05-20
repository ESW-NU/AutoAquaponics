/*
 Repeat timer example

 This example shows how to use hardware timer in ESP32. The timer calls onTimer
 function every second. The timer can be stopped with button attached to PIN 0
 (IO0).

 This example code is in the public domain.
 */

// Stop button is attached to PIN 0 (IO0)
#define BTN_STOP_ALARM    0
#define MAX_ALARMS 500

typedef struct virt_alarm {
  uint32_t time_hit;
  uint16_t state;
} virt_alarm;

hw_timer_t * timer = NULL;
volatile SemaphoreHandle_t timerSemaphore;
portMUX_TYPE timerMux = portMUX_INITIALIZER_UNLOCKED;
virt_alarm al_list[500];
uint32_t current_list = 0;

volatile uint32_t isrCounter = 0;
volatile uint32_t lastIsrAt = 0;

void IRAM_ATTR onTimer(){
  // Increment the counter and set the time of ISR
  portENTER_CRITICAL_ISR(&timerMux);
  Serial.print(millis());
  Serial.println(" ms");
  al_pop();
  portEXIT_CRITICAL_ISR(&timerMux);
  // Give a semaphore that we can check in the loop
  //xSemaphoreGiveFromISR(timerSemaphore, NULL);
  if (current_list > 0) {
    timerAlarmWrite(timer, al_list[0].time_hit, false);
    timerAlarmEnable(timer);
  }
  // It is safe to use digitalRead/Write here if you want to toggle an output
}

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

void al_pop(void) {
  for (size_t i = 0; i < current_list; i++) {
    al_list[i] = al_list[i + 1];
  }
  current_list --;
}

void setup() {
  Serial.begin(115200);
  al_insert(15000, 10);
  al_insert(50000, 10);
  al_insert(100000, 10);
  al_insert(40000, 10);
  al_insert(30000, 10);
  al_insert(20000, 10);
  al_insert(10000, 10);
  
  // Create semaphore to inform us when the timer has fired
  timerSemaphore = xSemaphoreCreateBinary();

  // Use 1st timer of 4 (counted from zero).
  // Set 80 divider for prescaler (see ESP32 Technical Reference Manual for more
  // info).
  timer = timerBegin(0, 8000, true);

  // Attach onTimer function to our timer.
  timerAttachInterrupt(timer, &onTimer, true);
  Serial.println("huh?");

  // Set alarm to call onTimer function every second (value in microseconds).
  // Repeat the alarm (third parameter)
  timerAlarmWrite(timer, al_list[0].time_hit, false);

  // Start an alarm
  timerAlarmEnable(timer);
}

void loop() {
  // If Timer has fired
//  if (xSemaphoreTake(timerSemaphore, 0) == pdTRUE){
//    uint32_t isrCount = 0, isrTime = 0;
//    // Read the interrupt count and time
//    portENTER_CRITICAL(&timerMux);
//    isrCount = isrCounter;
//    isrTime = lastIsrAt;
//    portEXIT_CRITICAL(&timerMux);
//    // Print it
//    Serial.print("onTimer no. ");
//    Serial.print(current_list);
//    Serial.print(" at ");
//    Serial.print(isrTime);
//    Serial.println(" ms");
//  }
}
