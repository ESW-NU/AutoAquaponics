/**
 * @file AddressConfig.ino
 * @author John Madden (jtmadden@ucsc.edu)
 * @brief Utility to configure the address of TEROS-12 sensors.
 * @version 0.1
 * @date 2022-06-24
 * 
 * Allows the addresses on TEROS-12 sensors to be configured. Used when setting
 * up multiple sensors connected to a single arduino that use the same data
 * line. The address of each sensor needs to be unique or else there is bus
 * contention.
 * 
 * To use this utility
 * 1. Connect a SINGLE sensor to the arduino
 * 2. Configure @p DATA_PIN and @p new_addr
 * 3. Flash firmware
 * 4. Check serial output. If the current address shows unexpected characters
 * there is bus contention. Double check that a single sensor is connected.
 */

#include "SDISerial.h"

/** Max Delay between the measure and data commands */
#define SENSOR_DELAY 1000

/** Pin used for line. Must be interrupt pin. */
#define DATA_PIN 13

SDISerial conn(DATA_PIN);

/** New address of TEROS-12 */
const char new_addr = '1';

void setup()
{
	Serial.begin(9600);
	Serial.println("TEROS-12 Address configurator, compiled on " __DATE__ " " __TIME__);

	conn.begin();
	delay(3000);	

	// Query for sensors	
	char * sens_info = conn.sdi_query("?!", 1000);

	Serial.print("Sensor active at ");
	Serial.print(sens_info);

	Serial.print("Changing to ");
	Serial.println(new_addr);

	// Update address
	char a_query[5];
	sprintf(a_query, "%cA%c!", sens_info[0], new_addr);
	char * resp_addr = conn.sdi_query(a_query, 1000);

	Serial.print("Responded ");
	Serial.print(resp_addr);
}

void loop() {}
