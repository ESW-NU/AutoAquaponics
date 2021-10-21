#include "BluetoothSerial.h" //Header File for Serial Bluetooth, will be added by default into Arduino
#include <BLEDevice.h> //Header file for BLE 

static BLEUUID serviceUUID("4fafc201-1fb5-459e-8fcc-c5c9c331914b"); //Service UUID of RaspberryPi
static BLEUUID charUUID("beb5483e-36e1-4688-b7f5-ea07361b26a8"); //Characteristic  UUID of RaspberryPi
String My_BLE_Address = "AC:67:B2:36:AF:A2"; //Hardware Bluetooth MAC of RaspberryPi
static BLERemoteCharacteristic* pRemoteCharacteristic;

BLEScan* pBLEScan; //Name the scanning device as pBLEScan
BLEScanResults foundDevices;

static BLEAddress *Server_BLE_Address;
String Scaned_BLE_Address;

boolean paired = false; //boolean variable to togge light

bool connectToserver (BLEAddress pAddress){
    
    BLEClient*  pClient  = BLEDevice::createClient(); //Makes ESP32 a client
    Serial.println(" - Created client");

    // Connect to the BLE Server.
    pClient->connect(pAddress);
    Serial.println(" - Connected to Pi");

    // Obtain a reference to the service we are after in the remote BLE server.
    BLERemoteService* pRemoteService = pClient->getService(serviceUUID);  //Gets service from Pi
    if (pRemoteService != nullptr)
    {
      Serial.println(" - Found our service");
      return true;
    }
    else
    return false;

  /* DO NOT NEED TO OBTAIN A REFERENCE TO BOTH CHARACTERISTIC AND SERVICE.
   * ONLY INCLUDED FOR FUTURE USE AND UNDERSTANDING
   */
   
  /*  // Obtain a reference to the characteristic in the service of the remote BLE server.
    pRemoteCharacteristic = pRemoteService->getCharacteristic(charUUID);
    if (pRemoteCharacteristic != nullptr)
      Serial.println(" - Found our characteristic");

      return true; */
}













BluetoothSerial ESP_BT; //Object for Bluetooth

int incoming;

void setup() {
  Serial.begin(115200); //Start Serial monitor in 9600
  ESP_BT.begin("Power Relay ESP32"); //Name of your Bluetooth Signal
  Serial.println("Bluetooth Device is Ready to Pair");

  BLEDevice::init("");
  pBLEScan = BLEDevice::getScan(); //create new scan
  pBLEScan->setAdvertisedDeviceCallbacks(new MyAdvertisedDeviceCallbacks()); //Call the class that is defined above 
  pBLEScan->setActiveScan(true); //active scan uses more power, but get results faster
}

void loop() {
  
  if (ESP_BT.available()) //Check if we receive anything from Bluetooth
  {
    incoming = ESP_BT.read(); //Read what we recevive 
    Serial.print("Received:"); Serial.println(incoming);

    if (incoming == 49)       // 49 is ASCII for 1. Bluetooth sends digits as chars.
        {
        digitalWrite(23, HIGH);
        ESP_BT.println("LED turned ON");
        }
        
    if (incoming == 48)       // 48 is ASCII for 0
        {
        digitalWrite(23, LOW);
        ESP_BT.println("LED turned OFF");
        }     
  }
  delay(20);
}
