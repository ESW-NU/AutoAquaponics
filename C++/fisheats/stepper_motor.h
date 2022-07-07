#ifndef STEPPER_MOTOR_H
#define STEPPER_MOTOR_H
#include <Arduino.h>

struct Steppers { //define new data type for stepper motor
  int INT1;
  int INT2;
  int INT3;
  int INT4;
};


void init_stepper(Steppers motor);
void init_steppers();
void step(int num, Steppers motor);
void dispense_food();
void turn_auger();

#endif
