#ifndef INTERRUPT_H
#define INTERRUPT_H
#include <Arduino.h>

#define BTN_STOP_ALARM    0

#define VALVE_1 15
#define VALVE_2 33
#define PUMP 22 //outlet 1
#define UPPER_GLIGHT 23 //outlet 2
#define LOWER_GLIGHT 25 //outlet 3
#define FISH_LIGHT 26 //outlet 4
#define gb1_duration 5 //minutes
#define gb2_duration 5 //minutes
#define upper_glight_dur 10 //hours
#define lower_glight_dur 10 //hours
#define fish_light_dur 8 //hours

void ARDUINO_ISR_ATTR onTimer();
void init_interrupt();

#endif
