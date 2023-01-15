/*********************************************************************
This is an example for our Monochrome OLEDs based on SSD1306 drivers
 
  Pick one up today in the adafruit shop!
  ------> http://www.adafruit.com/category/63_98
 
This example is for a 128x64 size display using I2C to communicate
3 pins are required to interface (2 I2C and one reset)
 
Adafruit invests time and resources providing this open source code, 
please support Adafruit and open-source hardware by purchasing 
products from Adafruit!
 
Written by Limor Fried/Ladyada  for Adafruit Industries.  
BSD license, check license.txt for more information
All text above, and the splash screen must be included in any redistribution
*********************************************************************/



#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <ESP8266WiFi.h>
#include <ESP8266WiFiMulti.h>
#include <ESP8266HTTPClient.h>


 
Adafruit_SSD1306 display(128,32,&Wire);
ESP8266WiFiMulti WiFiMulti;


 
#define LOGO16_GLCD_HEIGHT 16 
#define LOGO16_GLCD_WIDTH  16 
static const unsigned char PROGMEM logo16_glcd_bmp[] =
{ B00000000, B11000000,
  B00000001, B11000000,
  B00000001, B11000000,
  B00000011, B11100000,
  B11110011, B11100000,
  B11111110, B11111000,
  B01111110, B11111111,
  B00110011, B10011111,
  B00011111, B11111100,
  B00001101, B01110000,
  B00011011, B10100000,
  B00111111, B11100000,
  B00111111, B11110000,
  B01111100, B11110000,
  B01110000, B01110000,
  B00000000, B00110000 };
 


 const char *SSID         = "--SSID--";
 const char *PASSWORD     = "--PASSWORD--";
 const char *SERVER_ADDR  = "--SERVER_ADDRESS--"

void setup()   {                
  Serial.begin(9600);

  Wire.begin(2, 0);       

  display.begin(SSD1306_SWITCHCAPVCC, 0x3C);
 
  display.display();
  delay(1000);
  display.clearDisplay();


  WiFi.mode(WIFI_OFF);        
  delay(1000); 

  WiFi.mode(WIFI_STA);
  WiFiMulti.addAP(SSID, PASSWORD);
}
 

String fetch_price()
{
  String payload;
  if ((WiFiMulti.run() == WL_CONNECTED))
   {    
     long rssi = WiFi.RSSI();
     Serial.print("Signal strength (RSSI): ");
     Serial.println(rssi);
    }

    WiFiClient client;
    HTTPClient http;

    Serial.print("[HTTP] begin...\n");
    http.begin(client, SERVER_ADDR);       
    http.addHeader("Content-Type", "text/plain");             

    int httpCode = http.GET();
    Serial.print(httpCode);
    // httpCode will be negative on error
    if (httpCode > 0)
    {
      // file found at server
      if (httpCode == HTTP_CODE_OK)
       {
        payload = http.getString();
      }
    }
    else
    {
      Serial.printf("[HTTP] GET... failed, error: %s\n", http.errorToString(httpCode).c_str());
    }

  http.end();
  return payload;
}

void loop() {

  String data = fetch_price();

  // data is in the format "price; out; in)"
  int first_comma = data.indexOf(';');
  int second_comma = data.indexOf(';', first_comma + 1);

  String price = data.substring(0, first_comma);
  String out = data.substring(first_comma + 1, second_comma);
  String in = data.substring(second_comma + 1);

  int counter = 0;
  while (counter <= 10)
  {
    char display_buf [10];
    display.clearDisplay();
    display.setTextSize(2);
    display.setTextColor(WHITE);
    display.setCursor(0,0);

    display.print("Out ");
    display.print(out);
    display.print("C");
    display.println();
  
    display.print("In  ");
    display.print(in);
    display.print("C");
    display.display();

    delay(5000);
    
    display.clearDisplay();
    display.setCursor(0,0);
    display.println("Price");
    display.print(price);
    display.print(" cnt");
    display.display();
    delay(5000);
    counter ++;
  }  

}
