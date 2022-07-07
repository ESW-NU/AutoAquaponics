#include "interrupt.h"

void setup() {
  // put your setup code here, to run once:
  pinMode(UPPER_GLIGHT, OUTPUT); //output 1
  pinMode(LOWER_GLIGHT, OUTPUT); //output 2
  pinMode(FISH_LIGHT, OUTPUT); //output 3
}

void loop() {
  // turn on all lights
  digitalWrite(UPPER_GLIGHT, HIGH);
  digitalWrite(LOWER_GLIGHT, HIGH);
  digitalWrite(FISH_LIGHT, HIGH);
  delay(fish_light_dur * 1000);

  //turn off fish light
  digitalWrite(FISH_LIGHT, LOW);
  delay((upper_glight_dur-fish_light_dur) * 1000);
  //turn off plant lights 
  digitalWrite(UPPER_GLIGHT, LOW);
  digitalWrite(LOWER_GLIGHT, LOW);
  delay((24-upper_glight_dur) * 1000);
}
