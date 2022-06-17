#include "stepper_motor.h"

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  init_steppers();
  pinMode(4, INPUT);
}

void loop() {
  // put your main code here, to run repeatedly:
  turn_auger();
  if (digitalRead(4) == 1){
    Serial.println("Opening door");
    dispense_food();
  }
}
