/*
 * Program to operate ESP32 in client mode and use fitness band as proximity switch
 * Program by: Aswinth Raj B
 * Dated: 31-10-2018
 * Website: www.circuitdigest.com 
 * Reference: https://github.com/nkolban/esp32-snippets 
 * //NOTE: The My_BLE_Address, serviceUUID and charUUID should be changed based on the BLe server you are using 
 */

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

/* This class will receive the address of a server (Raspberry Pi)
   and turn it into a string so that it can be compared and verified
   with the right address*/
class MyAdvertisedDeviceCallbacks: public BLEAdvertisedDeviceCallbacks 
{
    void onResult(BLEAdvertisedDevice advertisedDevice) {
      Serial.printf("Scan Result: %s \n", advertisedDevice.toString().c_str());
      Server_BLE_Address = new BLEAddress(advertisedDevice.getAddress());
      Scaned_BLE_Address = Server_BLE_Address->toString().c_str();
      
    }
};

void setup() {
    Serial.begin(115200); //Start serial monitor 
    Serial.println("ESP32 BLE Server program"); //Intro message 

    /*BLEDevice::init("MyESP32");
    BLEServer *pServer = BLEDevice::createServer(); */
    connectToserver(*Server_BLE_Address); 
    
    pBLEScan = BLEDevice::getScan(); //create new scan
    pBLEScan->setAdvertisedDeviceCallbacks(new MyAdvertisedDeviceCallbacks()); //Call the class that is defined above 
    pBLEScan->setActiveScan(true); //active scan uses more power, but get results faster

    pinMode (13,OUTPUT); //Declare the in-built LED pin as output 
}

void loop() {

  foundDevices = pBLEScan->start(3); //Scan for 3 seconds to find the Raspberry Pi 

  while (foundDevices.getCount() >= 1)
  {
    if (Scaned_BLE_Address == My_BLE_Address && paired == false)
    {
      Serial.println("Found Device :-)... connecting to Server as client");
       if (connectToserver(*Server_BLE_Address))   //Uses UUID of Raspberry Pi
      {
      paired = true;
      break;
      }
      else
      {
      Serial.println("Pairing failed");
      break;
      }
    }
    
    if (Scaned_BLE_Address == My_BLE_Address && paired == true)
    {
      Serial.println("Our device went out of range");
      paired = false;
      Serial.println("********************LED OOOFFFFF************************");
      digitalWrite (13,LOW);
      ESP.restart();
      break;
    }
    else
    {
    Serial.println("We have some other BLe device in range");
    break;
    }
  } 
}
