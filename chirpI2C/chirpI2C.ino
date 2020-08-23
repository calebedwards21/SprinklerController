#include <I2CSoilMoistureSensor.h>
#include <Wire.h>
#include <WiFi.h>
#include <PubSubClient.h>

//WIFI
const char* wifiName = "INSTER_WIFI_NAME";
const char* wifiPass = "INSERT_WIFI_PASS";

//MQTT
const char* mqtt_server = "INSERT_RASPBERRY_PI_IPADDRESS";  // IP of the MQTT broker
const int mqtt_port = 1883;
const char* moisture_topic = "chirp/moisture";
const char* temperature_topic = "chirp/temperature";
const char* mqtt_username = "INSERT_MQTT_USERNAME"; // MQTT username
const char* mqtt_password = "INSERT_MQTT_PASSWORD"; // MQTT password
const char* clientID = "ESP32_Chirp"; // MQTT client ID

WiFiClient wifi;
I2CSoilMoistureSensor sensor;

PubSubClient client(wifi);



void setupWifi(){
  Serial.print("Connecting to ");
  Serial.println(wifiName);
  //Connect to WIFI
  WiFi.begin(wifiName, wifiPass);
  while( WiFi.status() != WL_CONNECTED ) {
        Serial.print(".");
        delay(1000);
    }
  Serial.println("WiFi connected");
}

void setup() {
  Wire.begin();
  Serial.begin(115200);
  
  sensor.begin(); // reset sensor
  delay(1000); // give some time to boot up

  Serial.print("I2C Soil Moisture Sensor Address: ");
  Serial.println(sensor.getAddress(),HEX);
  Serial.print("Sensor Firmware version: ");
  Serial.println(sensor.getVersion(),HEX);
  Serial.println();

  setupWifi();
  client.setServer(mqtt_server,mqtt_port);
}

float getTemp(){
  while (sensor.isBusy()) delay(50); // available since FW 2.3
  Serial.print(", Temperature: ");
  sensor.getTemperature();
  while (sensor.isBusy()) delay(50);
  return sensor.getTemperature()/(float)10;
}
unsigned int getMoisture(){
  while (sensor.isBusy()) delay(50); // available since FW 2.3
  Serial.print("Soil Moisture Capacitance: ");
  sensor.getCapacitance();
  while (sensor.isBusy()) delay(50);
  return sensor.getCapacitance();
}

void loop() {
  //Connect to MQTT Broker
  while(!client.connect(clientID, mqtt_username, mqtt_password)){
    if(client.state() > 0){
      Serial.print("CONNECTED, rc= ");
      Serial.println(client.state());
    }
    else {
      Serial.print("FAILED, rc= ");
      Serial.println(client.state());
    }
  }
  unsigned int moisture;
  float temp;
  moisture = getMoisture();
  Serial.print(moisture);
  temp = getTemp();
  Serial.println(temp);

  // MQTT can only transmit strings
  String moistureOut = String(moisture,DEC);
  Serial.print(moistureOut);
  Serial.print(" , ");
  String tempOut = String(temp,2);
  Serial.println(tempOut);

  //Publish to MQTT Broker (temperature_topic)
  if(client.publish(temperature_topic, tempOut.c_str())){
    Serial.println("TEMP SENT!");
  }
  else{
    Serial.println("FAILED TO SEND TEMP!");
    client.connect(clientID,mqtt_username,mqtt_password);
    delay(10);
    client.publish(temperature_topic,tempOut.c_str());
  }

  //Publish to MQTT Broker (moisture_topic)
  if(client.publish(moisture_topic, moistureOut.c_str())){
    Serial.println("MOISTURE SENT!");
  }
  else{
    Serial.println("FAILED TO SEND MOISTURE!");
    client.connect(clientID,mqtt_username,mqtt_password);
    delay(10);
    client.publish(moisture_topic,moistureOut.c_str());
  }

  client.disconnect(); //disconnet from MQTT Broker
  delay(10);
  
  sensor.sleep();
  //delay(1800000UL);
  delay(300000UL);
}
