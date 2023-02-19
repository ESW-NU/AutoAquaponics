// Stop button is attached to PIN 0 (IO0)
#define BTN_STOP_ALARM    0
#define Outlet_1          22
#define Outlet_2          23
#define Outlet_3          25
#define Outlet_4          7
#define Outlet_5          26
#define Outlet_6          13
#define Outlet_7          12
#define Outlet_8          14
#define Outlet_9          27
#define Outlet_10         19
#define Terminal_1        15  
#define Terminal_2        33
#define Terminal_3        4
#define Terminal_4        5
#define Terminal_5        32
#define Terminal_6        21

hw_timer_t * timer = NULL;
volatile SemaphoreHandle_t timerSemaphore;
portMUX_TYPE timerMux = portMUX_INITIALIZER_UNLOCKED;

volatile uint32_t tens_counter = 0;           //Counts total 10 second increments since start of minute
volatile uint32_t mins_counter = 0;           //Counts total number of minutes passed
gpio_num_t ledPin =  GPIO_NUM_27;

void IRAM_ATTR onten(){
  // Increment the counter every ten seconds 
  portENTER_CRITICAL_ISR(&timerMux);
  tens_counter++;
  if (tens_counter == 6){
    mins_counter++;
    tens_counter = 0;
  }
  portEXIT_CRITICAL_ISR(&timerMux);
  // Give a semaphore that we can check in the loop
  xSemaphoreGiveFromISR(timerSemaphore, NULL);
  // It is safe to use digitalRead/Write here if you want to toggle an output  
}

void setup() {
  Serial.begin(115200);

  // Set BTN_STOP_ALARM to input mode
  pinMode(BTN_STOP_ALARM, INPUT);

  // Create semaphore to inform us when the timer has fired
  timerSemaphore = xSemaphoreCreateBinary();

  // Use 1st timer of 4 (counted from zero).
  // Set 80 divider for prescaler (see ESP32 Technical Reference Manual for more
  // info).
  timer = timerBegin(0, 80, true);

  // Attach onTimer function to our timer.
  timerAttachInterrupt(timer, &onten, true);

  // Set alarm to call onten every ten seconds
  timerAlarmWrite(timer, 10000000, true);

  // Start an alarm
  timerAlarmEnable(timer);

  //Enable pin to test out code on LED
  pinMode(ledPin, OUTPUT);
}

void loop() {
  // If Timer has fired
  if (xSemaphoreTake(timerSemaphore, 0) == pdTRUE){
    uint32_t ten_inc = 0;
    uint32_t min_inc = 0;
    // Read the interrupt count and time
    portENTER_CRITICAL(&timerMux);
    ten_inc = tens_counter;
    min_inc = mins_counter;
    portEXIT_CRITICAL(&timerMux);
    // Print it
    Serial.println("Minutes Passed: ");
    Serial.print(min_inc);
    Serial.println(" Ten Second Increments in new minute: ");
    Serial.print(ten_inc);
    Serial.println("");
  }
  // If button is pressed
  if (digitalRead(BTN_STOP_ALARM) == LOW) {
    // If timer is still running
    if (timer) {
      // Stop and free timer
      timerEnd(timer);
      timer = NULL;
    }
  }
}
