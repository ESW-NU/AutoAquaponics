/*
 Repeat timer example

 This example shows how to use hardware timer in ESP32. The timer calls onTimer
 function every second. The timer can be stopped with button attached to PIN 0
 (IO0).

 This example code is in the public domain.
 */

int VALVE_1 = 15;
int VALVE_2 = 33;
int PUMP = 22;
int UPPER_GLIGHT = 23;
int LOWER_GLIGHT = 25;
int FISH_LIGHT = 18;
int gb1_duration = 5; //minutes
int gb2_duration = 5; //minutes
int upper_glight_dur = 10; //hours
int lower_glight_dur = 10; //hours
int fish_light_dur = 8; //hours
volatile int ON = 1;

hw_timer_t * timer = NULL;
volatile SemaphoreHandle_t timerSemaphore;
portMUX_TYPE timerMux = portMUX_INITIALIZER_UNLOCKED;

volatile uint32_t isrCounter = 0;
volatile uint32_t lastIsrAt = 0;

void ARDUINO_ISR_ATTR onTimer(){
  // Increment the counter and set the time of ISR
  portENTER_CRITICAL_ISR(&timerMux);
  isrCounter++;
  lastIsrAt = millis();
  portEXIT_CRITICAL_ISR(&timerMux);
  // Give a semaphore that we can check in the loop
  xSemaphoreGiveFromISR(timerSemaphore, NULL);
  // It is safe to use digitalRead/Write here if you want to toggle an output
  if (ON == 1){
    digitalWrite(VALVE_1, HIGH);
    digitalWrite(VALVE_2, LOW);
    ON = 0;
  }
  else{
    digitalWrite(VALVE_1, LOW);
    digitalWrite(VALVE_2, HIGH);
    ON = 1;
  }
}

void setup() {
  Serial.begin(115200);

  // Create semaphore to inform us when the timer has fired
  timerSemaphore = xSemaphoreCreateBinary();

  // Use 1st timer of 4 (counted from zero).
  // Set 80 divider for prescaler (see ESP32 Technical Reference Manual for more
  // info).
  timer = timerBegin(0, 80, true);

  // Attach onTimer function to our timer.
  timerAttachInterrupt(timer, &onTimer, true);

  // Set alarm to call onTimer function every second (value in microseconds).
  // Repeat the alarm (third parameter)
  timerAlarmWrite(timer, gb1_duration*60*1000000, true);

  // Start an alarm
  timerAlarmEnable(timer);

  //set output stuff here
  pinMode(VALVE_1, OUTPUT); //screw terminal 1
  pinMode(VALVE_2, OUTPUT); //screw terminal 2
  pinMode(UPPER_GLIGHT, OUTPUT); //screw terminal 1
  pinMode(LOWER_GLIGHT, OUTPUT); //screw terminal 2
  pinMode(FISH_LIGHT, OUTPUT); //screw terminal 1
  pinMode(PUMP, OUTPUT); //pump
  digitalWrite(PUMP, HIGH); //always keep pump on
}

void loop() {
  // If Timer has fired
  if (xSemaphoreTake(timerSemaphore, 0) == pdTRUE){
    uint32_t isrCount = 0, isrTime = 0;
    // Read the interrupt count and time
    portENTER_CRITICAL(&timerMux);
    isrCount = isrCounter;
    isrTime = lastIsrAt;
    portEXIT_CRITICAL(&timerMux);
    // Print it
    Serial.print("onTimer no. ");
    Serial.print(isrCount);
    Serial.print(" at ");
    Serial.print(isrTime);
    Serial.println(" ms");
  }
  // toggle lights
  digitalWrite(UPPER_GLIGHT, HIGH);
  digitalWrite(LOWER_GLIGHT, HIGH);
  digitalWrite(FISH_LIGHT, HIGH);
  Serial.println("All lights on");
  delay(fish_light_dur * 60 * 60 * 1000);

  //turn off fish light
  digitalWrite(FISH_LIGHT, LOW);
  Serial.println("Fish light off");
  delay((upper_glight_dur-fish_light_dur)* 60 * 60 * 1000);
  //turn off plant lights 
  digitalWrite(UPPER_GLIGHT, LOW);
  digitalWrite(LOWER_GLIGHT, LOW);
  Serial.println("Plant lights off");
  delay((24-upper_glight_dur) * 60 * 60 * 1000);
}
