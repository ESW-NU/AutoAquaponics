// Include the AccelStepper Library
#include <AccelStepper.h>
// Include the load cell library
#include "HX711.h"
// Define step constant

#define FULLSTEP 4
#define calibration_factor 4170//3480.0 //This value is obtained using the SparkFun_HX711_Calibration sketch
#define DOUT  23
#define CLK  22
#define POWER 4
HX711 scale;

// Creates an instance
// Pins entered in sequence IN1-IN3-IN2-IN4 for proper step sequence
AccelStepper stepper1(FULLSTEP, 1, 21, 3, 19);
AccelStepper stepper2(FULLSTEP, 18, 17, 5, 16);
int count=0;
int count2=0;
int movetodistance=4038;

void setup() {
  pinMode(POWER, OUTPUT);    // sets the digital pin 13 as output
  
  stepper1.setMaxSpeed(1000);
  stepper1.setSpeed(300);
  //stepper1.setAcceleration(1000);
  
  stepper2.setMaxSpeed(1000);
  stepper2.setAcceleration(1000);
  
  //Serial.begin(9600);
  //Serial.println("FishEats Demo");
/*
  scale.begin(DOUT, CLK);
  scale.set_scale(calibration_factor); //This value is obtained by using the SparkFun_HX711_Calibration sketch
  scale.tare(); //Assuming there is no weight on the scale at start up, reset the scale to 0

  Serial.println("Starting....");
*/
}

void loop() {
  // Run motor
  //digitalWrite(POWER, HIGH); //set POWER pin to high    
  stepper1.runSpeed(); 
  /*while (count < 1) {
    //stepper1.moveTo(movetodistance);
    
    scale.tare(); //Assuming there is no weight on the scale at start up, reset the scale to 0
    while (abs(scale.get_units()) < 10) {
      //for (int i = 0; i <= 1000; i++) {
      stepper1.runSpeed();
      //delay(1);
      //}
      //Serial.print("Reading: ");
      //Serial.print(scale.get_units(), 2); //scale.get_units() returns a float
      //Serial.print(" grams"); //You can change this to kg but you'll need to refactor the calibration_factor
      //Serial.println();
    }
    stepper1.stop();
    
    count++;   
  }  
  stepper1.stop();  
  while (count2 < 1) {
    stepper2.moveTo(-640);
    stepper2.setSpeed(-300);
    while (stepper2.currentPosition() != -645)
      stepper2.runSpeed();
    stepper2.stop();
    stepper2.runToPosition();
    
    stepper2.moveTo(0);
    stepper2.setSpeed(300);
    while (stepper2.currentPosition() != 0)
      stepper2.runSpeed();
    stepper2.stop();
    count2++;
  }*/
}
