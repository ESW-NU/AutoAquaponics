import processing.serial.*;
Serial myPort;  // Create object from Serial class
int red;     // red  data received from the serial port
int green;     // green  data received from the serial port
int blue;     // blue  data received from the serial port
int lf = 10;  // The number 10 is the ASCII code for linefeed (end of serial.println), later we will look for this to break up individual messages.
String receivedStr;


void setup()
{
  // Open whatever port is the one you're using.
  String portName = Serial.list()[3]; //change the 0 to a 1 or 2 etc. to match your port
  myPort = new Serial(this, portName, 9600);
  myPort.clear();  // function from serial library that throws out the first reading, in case we started reading in the middle of a string from Arduino
  receivedStr = myPort.readStringUntil(lf); //reads the string from serial port until a println occurs and assigns to receivedStr
  receivedStr = null;  //initialize receivedStr to be empty

  size(400, 400);  //size of canvas
}

void draw()
{
  while (myPort.available() > 0) { //as long as there is data coming from serial port, read it and store it
    receivedStr = myPort.readStringUntil(lf);
  }

  if (receivedStr != null) {
    String[] a = split(receivedStr, ',');  // a new array (called 'a') that stores values into separate cells (separated by commas specified in your Arduino program)
    println(a[0]); //print the first string value of the array
    println(a[1]); //print to the console the second string value
    println(a[2]);  //print to the console the third string value
    int red = Integer.parseInt(a[0].trim()); // This is probably the scariest line of code here. For now, you...
    int green = Integer.parseInt(a[1].trim()); // ...just need to know that it converts the string into an integer.
    int blue = Integer.parseInt(a[2].trim());
    
    fill(red, green, blue);  //use values sent from arduino to set color of square 
    noStroke();
    rect(0, 0, 400, 400);

  }
}
