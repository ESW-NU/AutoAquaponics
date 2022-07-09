#include "interrupt.h"

void setup() {
  //initialize interrupt
  init_interrupt();
  // put your setup code here, to run once:
  pinMode(VALVE_1, OUTPUT); //screw terminal 1
  pinMode(VALVE_2, OUTPUT); //screw terminal 2
  pinMode(UPPER_GLIGHT, OUTPUT); //output 1
  pinMode(LOWER_GLIGHT, OUTPUT); //output 2
  pinMode(FISH_LIGHT, OUTPUT); //output 3
  pinMode(PUMP, OUTPUT);//pump
  digitalWrite(PUMP, LOW); //always keep pump on
  digitalWrite(VALVE_1, HIGH);
  digitalWrite(VALVE_2, LOW);
}

void loop() {
  // turn on all lights
  digitalWrite(UPPER_GLIGHT, LOW);
  digitalWrite(LOWER_GLIGHT, LOW);
  digitalWrite(FISH_LIGHT, LOW);
  delay(fish_light_dur * 60 * 60 * 1000);

  //turn off fish light
  digitalWrite(FISH_LIGHT, HIGH);
  delay((upper_glight_dur-fish_light_dur) * 60* 60* 1000);
  //turn off plant lights 
  digitalWrite(UPPER_GLIGHT, HIGH);
  digitalWrite(LOWER_GLIGHT, HIGH);
  delay((24-upper_glight_dur) * 60 * 60 * 1000);
}
