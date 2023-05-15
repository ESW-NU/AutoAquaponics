/**
 * @file SDISerial.ino
 * @author John Madden (jtmadden@ucsc.edu)
 * @brief Serial logger for TEROS-12 soil moisture sensor
 * @version 0.1
 * @date 2022-06-23
 * 
 * The firmware reads data using SDI from any number of TEROS-12 soil moisture sensors
 * and outputs it over serial. Sensor addresses are configured with @p addrs.
 * The logging interval can be changed with the define @p MEAS_INT.
 * 
 * There is no checking done if the connected sensors do not match what is
 * currently connected. If a address is defined but not connected no data will
 * be output.
 * 
 * If the data appears weird, then there is most likely bus contention between two
 * sensors. Every sensor connected must have a different address.
 */

#include "SDISerial.h"

/** Max Delay between the measure and data commands */
#define SENSOR_DELAY 1000

/** Period between measurements in ms */
#define MEAS_INT 10

/** Pin used for line. Must be interrupt pin. */
#define DATA_PIN 13

/** Array of address characters */
const char addrs[] = {'0', '1'};
/** Length of @p addrs */
const unsigned int addrs_len = 2;

SDISerial sdi_serial_connection(DATA_PIN);

String nom = "Arduino";
String msg;

void setup()
{
  Serial.begin(1200);

  // Debug string to break up the data stream when testing
  //Serial.println("SDISerial, compiled on " __DATE__ " " __TIME__);

  sdi_serial_connection.begin();
  delay(3000);
}

void loop()
{

  //readSerialPort();
  if (Serial.available() > 0) {
    String data = Serial.readStringUntil('\n');
    if (data == "data"){
      // Serial.print("samples(ADDR/RAW/TMP/EC): ");
      for (int i = 0; i < addrs_len; i++) {
        char * samples = get_measurement(addrs[i]);
        Serial.write(samples);
      }
    }
  }
  delay(MEAS_INT);
}

/**
 * @brief Get measurement from sensor at address
 * 
 * @param _addr Address of sensor
 *
 * @see https://github.com/joranbeasley/SDISerial/blob/master/examples/SDISerialExample/SDISerialExample.ino
 * @return Single measurement
 */
char * get_measurement(char _addr)
{
  // Measure query
  char m_query[4];
  // Data query
  char d_query[5];

  // Format query strings
  sprintf(m_query, "%cM!", _addr);
  sprintf(d_query, "%cD0!", _addr);

  // Query sensor 0
  sdi_serial_connection.sdi_query(m_query, SENSOR_DELAY);
  // you can use the time returned above to wait for the service_request_complete
  sdi_serial_connection.wait_for_response(SENSOR_DELAY);
  // Get data from sensor
  return (sdi_serial_connection.sdi_query(d_query, SENSOR_DELAY));
}


void readSerialPort() {
  msg = "";
  if (Serial.available()) {
    delay(10);
    while (Serial.available() > 0) {
      msg += (char)Serial.read();
    }
    Serial.flush();
  }
}
