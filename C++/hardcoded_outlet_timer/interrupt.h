#ifndef INTERRUPT_H
#define INTERRUPT_H
#include <Arduino.h>

#define BTN_STOP_ALARM    0

#define VALVE_1 15
#define VALVE_2 33
#define UPPER_GLIGHT 32
#define LOWER_GLIGHT 25
#define FISH_LIGHT 18
#define gb1_duration 5 //minutes
#define gb2_duration 5 //minutes
#define upper_glight_dur 6 //hours
#define lower_glight_dur 10 //hours
#define fish_light_dur 8 //hours

void ARDUINO_ISR_ATTR onTimer();
void init_interrupt();

#endif
