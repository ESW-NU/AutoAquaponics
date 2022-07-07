//Stepping motor from scratch
#include <Arduino.h>
#include "stepper_motor.h"

int wait = 10; //changes the speed of the auger motor in step()
int wait2 = 2; //speed of door, can be much faster
Steppers stepper1, stepper2; //define the steppers locally here

void init_steppers(){ //called in setup() to initialize all GPIO pins used for both motors
  //define pins for gate motor
  stepper1.INT1 = 27;
  stepper1.INT2 = 14;
  stepper1.INT3 = 12;
  stepper1.INT4 = 13;
  
  //define pins for auger motor
  stepper2.INT1 = 5;
  stepper2.INT2 = 18;
  stepper2.INT3 = 19;
  stepper2.INT4 = 21;

  //initialize each stepper motor
  init_stepper(stepper1);
  init_stepper(stepper2);
}

void init_stepper(Steppers motor){ //initializes GPIO pins of one motor to output
  pinMode(motor.INT1, OUTPUT);
  pinMode(motor.INT2, OUTPUT);
  pinMode(motor.INT3, OUTPUT);
  pinMode(motor.INT4, OUTPUT);
}

// Make one motor take a certain number of steps
// num is how many steps it takes, + num will make motor turn in CW direction, - will go CCW
// motor is the stepper motor we want to move
void step(int num, Steppers motor, int t) { 
  int cur_num = 0; //current number of steps
  if (num > 0){ //procedure for positive num
    while (cur_num < num){
      digitalWrite(motor.INT1, HIGH);
      digitalWrite(motor.INT3, LOW);
      digitalWrite(motor.INT2, LOW);
      digitalWrite(motor.INT4, LOW);
      delay(t);
      digitalWrite(motor.INT1, LOW);
      digitalWrite(motor.INT3, LOW);
      digitalWrite(motor.INT2, HIGH);
      digitalWrite(motor.INT4, LOW);
      delay(t);
      digitalWrite(motor.INT1, LOW);
      digitalWrite(motor.INT3, HIGH);
      digitalWrite(motor.INT2, LOW);
      digitalWrite(motor.INT4, LOW);
      delay(t);
      digitalWrite(motor.INT1, LOW);
      digitalWrite(motor.INT3, LOW);
      digitalWrite(motor.INT2, LOW);
      digitalWrite(motor.INT4, HIGH);
      cur_num = cur_num + 1;
      delay(t);
    }
  }
   else if (num < 0){ //procedure for negative num
    while (cur_num > num){
      digitalWrite(motor.INT1, LOW);
      digitalWrite(motor.INT3, LOW);
      digitalWrite(motor.INT2, LOW);
      digitalWrite(motor.INT4, HIGH);
      delay(t);
      digitalWrite(motor.INT1, LOW);
      digitalWrite(motor.INT3, HIGH);
      digitalWrite(motor.INT2, LOW);
      digitalWrite(motor.INT4, LOW);
      delay(t);
      digitalWrite(motor.INT1, LOW);
      digitalWrite(motor.INT3, LOW);
      digitalWrite(motor.INT2, HIGH);
      digitalWrite(motor.INT4, LOW);
      delay(t);
      digitalWrite(motor.INT1, HIGH);
      digitalWrite(motor.INT3, LOW);
      digitalWrite(motor.INT2, LOW);
      digitalWrite(motor.INT4, LOW);
      cur_num = cur_num - 1;
      delay(t);
   }
  }
  //turn off all pins after stepping
  digitalWrite(motor.INT1, LOW);
  digitalWrite(motor.INT3, LOW);
  digitalWrite(motor.INT2, LOW);
  digitalWrite(motor.INT4, LOW);
}

// Move feeder cover in and out to dispense food
void dispense_food(){
  step(-180, stepper1, wait2); //experimentally figured out 180 steps is optimal to open gate
  step(180, stepper1, wait2);
}

// dir is either 1 or -1, 1 makes auger turn in a way that dispenses food
void turn_auger(int dir){
  step(dir*10, stepper2, wait); //turn auger a single step
}
