// Very simple code which interfaces a DHT11 sensor on pin 14 and spits out
// humidity and temperature readings over the USB serial output in ASCII. 

#include "DHT.h"
#define DHTPIN 14     // what digital pin we're connected to
#define DHTTYPE DHT11

DHT dht(DHTPIN, DHTTYPE);

void setup() 
{
  Serial.begin(115200);
  dht.begin();
}

void loop() 
{
  // Wait a few seconds between measurements.
  delay(2000);

  // Reading temperature or humidity takes about 250 milliseconds!
  // Sensor readings may also be up to 2 seconds 'old' (its a very slow sensor)
  float h = dht.readHumidity();
  // Read temperature as Celsius (the default)
  float t = dht.readTemperature();
  // Read temperature as Fahrenheit (isFahrenheit = true)
  float f = dht.readTemperature(true);

  // Check if any reads failed and exit early (to try again).
  if (isnan(h) || isnan(t) || isnan(f)) 
  {
    Serial.println("Error: Failed to read from DHT sensor!");
    return;
  }

  Serial.print("Humidity=");
  Serial.print((int)h);
  Serial.print("%, ");
  
  Serial.print("Temperature=");
  Serial.print((int)t);
  Serial.println("C");
}
