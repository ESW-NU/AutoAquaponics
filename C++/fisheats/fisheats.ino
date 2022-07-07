#include "stepper_motor.h"
#include "HX711.h"

//initialize load cell
#define calibration_factor 16880.0 //This value is obtained using the SparkFun_HX711_Calibration sketch
#define DOUT  23
#define CLK  22
HX711 scale;

float desired_weight = 0.1;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  init_steppers();
  pinMode(4, INPUT);

  scale.begin(DOUT, CLK);
  scale.set_scale(calibration_factor); //This value is obtained by using the SparkFun_HX711_Calibration sketch
  scale.tare(); //Assuming there is no weight on the scale at start up, reset the scale to 0
}

void loop() {
  /*for (int i = 0; i < 10; i++) {
    turn_auger(-1);
  }
  for (int i = 0; i < 20; i++) {
    turn_auger(1);
  }*/
  Serial.print(scale.get_units(), 3); //scale.get_units() returns a float
  Serial.print(" g"); //You can change this to kg but you'll need to refactor the calibration_factor
  Serial.println();
  if (digitalRead(4) == 1){
    Serial.println("Reset scale");
    scale.tare(); //reset scale
    float last_weight = abs(scale.get_units());
    while (last_weight < desired_weight){
      turn_auger(10);
      turn_auger(-5);
      last_weight = abs(scale.get_units());
    }
    Serial.println("Opening door");
    Serial.print(scale.get_units(), 3); //scale.get_units() returns a float
    Serial.print(" g"); //You can change this to kg but you'll need to refactor the calibration_factor
    Serial.println();
    dispense_food();
  }
  
}
