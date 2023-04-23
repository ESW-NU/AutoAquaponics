int VALVE_1 = 15;
int VALVE_2 = 33;
int gb1_duration = 5;
int gb2_duration = 5;

void setup() {
  // put your setup code here, to run once:
  pinMode(VALVE_1, OUTPUT); //screw terminal 1
  pinMode(VALVE_2, OUTPUT); //screw terminal 2
}

void loop() {
  // flood grow bed 1
  digitalWrite(VALVE_1, HIGH);
  digitalWrite(VALVE_2, LOW);
  delay(gb1_duration * 60 * 1000);

  // flood grow bed 2
  digitalWrite(VALVE_1, LOW);
  digitalWrite(VALVE_2, HIGH);
  delay(gb2_duration * 60 * 1000);
}