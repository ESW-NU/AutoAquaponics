/*
 Repeat timer example

 This example shows how to use hardware timer in ESP32. The timer calls onTimer
 function every second. The timer can be stopped with button attached to PIN 0
 (IO0).

 This example code is in the public domain.
 */


#define O_1               22            // O define's show pin numbers for Outlets 1-10
#define O_2               23
#define O_3               25
#define O_4               7
#define O_5               26
#define O_6               13
#define O_7               12
#define O_8               14
#define O_9               27
#define O_10              19
#define T_1               15            // T define's show Screw Terminals 1-6 (will be regarded as outlets 11-16 in arrays below)   
#define T_2               33 
#define T_3               4
#define T_4               5
#define T_5               32
#define T_6               21
#include <string> 
#include <iostream> 
#include <stdint.h>
const outlet_pins[16] = {O_1, O_2, O_3, O_4, O_5, O_6, O_7, O_8, O_9, O_10, T_1, T_2, T_3, T_4, T_5, T_6}; 

hw_timer_t * timer = NULL;
volatile SemaphoreHandle_t timerSemaphore;
portMUX_TYPE timerMux = portMUX_INITIALIZER_UNLOCKED;

volatile uint32_t mins_counter = 0;    // counts the number of minutes that have passed in ten minute interval
volatile uint32_t tens_counter = 0;    // counts the number of ten-minute increments that have passed in current hour
volatile uint32_t hour_counter = 0;    // counts the number of hours that have passed in current day
volatile uint32_t day_counter = 0;     // counts the number of days that have passed in current week

uint32_t outlet_mode[15];              // array holding values for the mode an outlet is set to
uint32_t on_time[15];                  // array holding times at which outlets will turn on in ten-minute intervals from the start of the day
uint32_t on_or_off[15];                // array holding values for whether outlet is on or off 
uint32_t duration[15];                 // array holding the durations an outlet will be on in daily-repeat and time cycle modes
uint32_t cyc_cnts[15];                 // array that specifies how much time is left for on/off mode on outlets in time-cycle mode

// Interrupt that is called every minute and increments the time counters accordingly
void IRAM_ATTR on_min(){
  // Increments counters based on values of smaller value counters 
  portENTER_CRITICAL_ISR(&timerMux);
  mins_counter++;
  if (mins_counter == 10){
    tens_counter++;
    mins_counter = 0;
  }
  if (tens_counter == 6){
    hour_counter++;
    tens_counter = 0;
  }
  if (hour_counter == 24){
    day_counter++;
    hour_counter = 0;
  }
  if (day_counter == 7){
    mins_counter = 0;
    tens_counter = 0;
    hour_counter = 0;
    day_counter = 0;
  }

  // for loop for checking counters against arrays and changing values
  // will check the mode for all outlets and change on/off and duration values accordingly
  // Needs to be in on_min interrupt because time_cycle values will change too quickly otherwise
  for (int i = 0; i < 16; i++) {
      mode = outlet_mode[i];
      swtich(mode){
        case 0:
        break;

        case 1:                                   // Time Cycle Mode (01) (mode 1)
        if (outlet_mode[i] == 1){
          if (cyc_cnts[i] == 0){                  // Check to see if the time_cycle has ended for given outlet
            cyc_cnts[i] = duration[i];            // Assign time cycle duration that is permanently stored in duration array
            if (on_or_off[i] == 0){               // When cyc_cnts[i] == 0, that means the current time cycle has ended,
              on_or_off[i] == 1;                  // so the outlet will be turned on or off at this time and a new cycle starts
            }                                     // using the number in the duration array.
            if (on_or_off[i] == 0){
              on_or_off[i] == 0;
            }
          }
          else{
            cyc_cnts[i] --;                       // Decreases current time cycle by 1 every minute (ISR called every minute)
          }
        }

        break;
        case 2:                                   // Daily Repeat Mode (10) (mode 2)
        break;

        case 3:                                   // Permanent State Mode (11) (mode 3)  
        break;
      }

  }

  portEXIT_CRITICAL_ISR(&timerMux);
  // Give a semaphore that we can check in the loop
  xSemaphoreGiveFromISR(timerSemaphore, NULL);
  // It is safe to use digitalRead/Write here if you want to toggle an output  
}

void setup() {
  Serial.begin(115200);

  // for loop that will set ESP32 pins correlating to outlets as OUTPUT
  for (int i = 0; i < 16; i++){
    pinMode(outlet_pins[i], OUTPUT);
  }

  // Create semaphore to inform us when the timer has fired
  timerSemaphore = xSemaphoreCreateBinary();

  // Use 1st timer of 4 (counted from zero).
  // Set 80 divider for prescaler (see ESP32 Technical Reference Manual for more
  // info).
  timer = timerBegin(0, 80, true);

  // Attach onTimer function to our timer.
 timerAttachInterrupt(timer, &on_min, true);

  // Set alarm to call onmin function every minute (value in microseconds).
  // Repeat the alarm (third parameter)
  timerAlarmWrite(timer, 60000000, true);

  // Start an alarm
  timerAlarmEnable(timer);
}

void loop() {
  
  // The message that has been received will be broken down into segments specified by
  // the AutoOutlet C++ Code Documentation on Google Drive: 
  // https://docs.google.com/document/d/17H-WvJsHd-YGuLblgH95uoM-LP0ZRlJ7i7fLkkYbfUw/edit
  
  uint32_t message;                             // needs to be assigned to BLE message from RPi, then if statement if message has been changed. If it has, run switch cases below.
  uint32_t req_mode = (message & 0x3);
  uint32_t blue_bits = (message >> 2) & 0xFF;
  uint32_t red_bits = (message >> 10) & 0x7FF;
  uint32_t green_bits = (message >> 21) & 0x7FF;


  // switch cases need to be placed in interrupt for receiving messages
  // will alwaye
  switch (req_mode) {
    case 0:                                   // Initialization Mode (00)
      time = red_bits;                        // Message from RPi showing number of ten-minute intervals from start of day
      int hrs = time/60;                      // Number of hours from start of the day
      int tens = (time % 60) / 10;            // Number of ten minute intervals that have passed in given hour
      portENTER_CRITICAL(&timerMux);
      tens_counter = tens;
      hour_counter = hrs;                     // Counter values will be reset here based on time from RPi
      portEXIT_CRITICAL(&timerMux);
      break;

    case 1:                                   // Time Cycle Mode (01) (mode 1)
      uint32_t outlet_num = blue_bits;
      outlet_mode[outlet_num] = req_mode;
      duration[outlet_num] = red_bits;
      break;

    case 2:                                   // Daily Repeat Mode (10) (mode 2)
      uint32_t outlet_num = blue_bits;
      outlet_mode[outlet_num] = req_mode;
      uint32_t time_to_turn_on = red_bits;
      on_time[outlet_num] = time_to_turn_on;
      uint32_t duration_10 = green_bits;      // Gets duration in increments of 10 (i.e. value of 4 = 40 minutes)
      duration[outlet_num] = duration_10;
      break;

    case 3:                                   // Permanent State Mode (11) (mode 3)      
      uint32_t outlet_num = blue_bits;
      outlet_mode[outlet_num] = req_mode;
      uint32_t state = green_bits;
      on_or_off[outlet_num] = state;
      uint32_t permenant_or_not = red_bits;
      //duration[outlet_num] = INT_FAST#@_MAX; //use infinity to show we are in permanant mode
      break;      
  }

  // for loop for turning outlets on/off based on on_or_off array
  for (int i = 0; i < 16; i ++){
      switch (on_or_off[i]){
        case 0:
          digitalWrite(on_or_off[i], LOW);          // Turns pin off if on_or_off[i] value is 0
          break;
        case 1:
          digitalWrite(on_or_off[i], HIGH)          // Turns pin on if on_or_off[i] value is 1
          break;          
      }
  }
}
