#include <SoftwareSerial.h>
#include <SPI.h>
#include "Mirf.h"
#include "nRF24L01.h"
#include "MirfHardwareSpiDriver.h"
#include "RDM6300.h"
// RFID  | Nano
// Pin 1 | D2
// Pin 2 | D3
SoftwareSerial rfid = SoftwareSerial(2, 3);
uint16_t sensorReading;
int LEDBlue = 4;
int LEDYellow = 5;
bool unlock = false;

// int passwordOne[] = {2, 49, 53, 48, 48, 50, 55, 56, 52, 52, 54, 70, 48, 3};
//int passwordTwo[] = {2, 49, 53, 48, 48, 50, 55, 48, 56, 53, 48, 54, 65, 3};

String allowedTags[] = {"1500278446F0"};// "15002708506A"};

String readRFID() {
  // Clear the RFID buffer before starting a new read
  while (rfid.available()) {
    rfid.read();  // Discard any leftover data
  }

  String tag = "";
  unsigned long startTime = millis();  // Record the start time

  while (millis() - startTime < 100) { // Timeout after 100ms (adjust as needed)
    if (rfid.available()) {
      char c = (char)rfid.read();
      if (c == '\r' || c == '\n') break;  // Stop at line-ending character
      tag += c;                           // Append to tag
      if (tag.length() >= 14) break;      // Stop reading after 14 characters
    }
  }
  return tag;
}

bool isTagAllowed(String tagID) {
  for (int i = 0; i < sizeof(allowedTags) / sizeof(allowedTags[0]); i++) {
    if (tagID.equals(allowedTags[i])) {
      return true;
    }
  }
  return false;
}

void setup() {
  // Start serial communication for debugging
  Serial.begin(9600);
  
  // Start SoftwareSerial communication for RFID
  rfid.begin(9600);
  
  // Optional: Set up feedback components (e.g., LEDs, buzzer)
  pinMode(LED_BUILTIN, OUTPUT);  // Use built-in LED for indication

   Mirf.spi = &MirfHardwareSpi;
  Mirf.init();
  Mirf.setRADDR((byte *)"BOOPI");
  Mirf.payload = sizeof(sensorReading);
  Mirf.channel = 90;
  Mirf.config();
}

void loop() {
  if (rfid.available()) {
    // Read the RFID tag
    String tagID = readRFID();
    
    // Debug: Print tag ID
    Serial.println("Scanned Tag ID: " + tagID);
    
    // Check if the tag is valid
    if (isTagAllowed(tagID)) {
      Serial.println("Access Granted!");
      sensorReading = 1;
      digitalWrite(LEDBlue, HIGH);  // Turn on LED
    } else {
      Serial.println("Access Denied!");
      digitalWrite(LEDYellow, HIGH);
      digitalWrite(LEDBlue, LOW);
      sensorReading = 0;
      // Optional: Provide other feedback for denied access
    }
  } 
  Serial.println(sensorReading);                     // Keep it on for 2 seconds; // Turn off LED
  Mirf.setTADDR((byte *)"BOOOO");
  Mirf.send((byte *) &sensorReading);
  delay(2000);
  digitalWrite(LEDBlue, LOW);
  while(Mirf.isSending()){}
  sensorReading = 0;
  delay(50);
}