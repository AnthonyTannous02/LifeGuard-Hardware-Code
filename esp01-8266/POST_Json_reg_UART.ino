#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <ESP8266WiFiMulti.h>
#include <ESP8266HTTPClient.h>

#define USE_SERIAL Serial

ESP8266WiFiMulti WiFiMulti;


char* waitForInput(const char* prompt, int maxSize, int timeoutMillis = 5000) {
    USE_SERIAL.println(prompt);
    USE_SERIAL.flush();
    char* inputBuffer = new char[maxSize];

    size_t index = 0;
    unsigned long startMillis = millis();  // Record the start time

    while (true) {
        while (USE_SERIAL.available() > 0) {
            char c = USE_SERIAL.read();
            inputBuffer[index++] = c;
            if (c == '\n' || c == '\r') {
                while (index > 0 && (inputBuffer[index - 1] == '\n' || inputBuffer[index - 1] == '\r' || inputBuffer[index - 1] == ' ')) {
                    index--;
                }
                inputBuffer[index] = '\0';
                return inputBuffer;
            }
        }
        // if(index > 0) break;
        delay(10);
    }

    // Timeout reached, return what's collected so far
    inputBuffer[index] = '\0';  // Null-terminate the buffer
    return inputBuffer;
}


void freeInputBuffer(char* buffer) {
    delete[] buffer;
}


char* API_HOME;


void postRequest(char* dataType, char* uartData) {
  HTTPClient http;
  int type = dataType[0] - 48;
  char* endPoint;
  switch(type){
    case 1:
      endPoint = "/acc";
      break;
    case 2:
      endPoint = "/gps";
      break;
    case 3:
      endPoint = "/oxi";
      break;
    case 4:
      endPoint = "/prs";
      break;
    default:
      endPoint = "";
      break;
  }
  freeInputBuffer(dataType);

  USE_SERIAL.println("Sending...");
  
  char* API = new char[strlen(API_HOME) + strlen(endPoint) + 1];
  API[0] = '\0';
  strcat(API, API_HOME);
  strcat(API, endPoint);
  http.begin(API);
  freeInputBuffer(API);
  http.addHeader("Content-Type", "application/json");
  int httpResponseCode = http.POST(uartData);
  USE_SERIAL.println(uartData);
  freeInputBuffer(uartData);
  if (httpResponseCode > 0) {
      USE_SERIAL.printf("[HTTP] POST... code: %d\n", httpResponseCode);

      if (httpResponseCode == HTTP_CODE_OK) {
          USE_SERIAL.println(http.getString());
      }
  } else {
      USE_SERIAL.printf("[HTTP] POST... failed, error: %s\n", http.errorToString(httpResponseCode).c_str());
  }
  USE_SERIAL.flush();
  http.end();
}


void setup() {
    USE_SERIAL.begin(115200);
    USE_SERIAL.println("Starting...");
    USE_SERIAL.flush();

    WiFi.mode(WIFI_STA); // Config to Allow it to connect to WIFI APs
    WiFi.disconnect(); // Disconnect Previously Connected Wifi in case of Change
    int n = WiFi.scanNetworks(); // Debugging purpose Scan Networks
    USE_SERIAL.print(n);
    USE_SERIAL.println(" network(s) found:");
    for (int i = 0; i < n; i++)
    {
      USE_SERIAL.print(WiFi.SSID(i) + ", ");
    }
    USE_SERIAL.println();
    char* APNAME;
    char* APAUTH;
    do{
      APNAME = waitForInput("APNAME", 100); // Wait for Rpi to Send the APNAME
      APAUTH = waitForInput("APAUTH", 100); // Wait for Rpi to Send the APAUTH
      WiFiMulti.addAP(APNAME, APAUTH);
    }while(WiFiMulti.run() != WL_CONNECTED);

    freeInputBuffer(APNAME); // Delete Unused Data
    freeInputBuffer(APAUTH); // Delete Unused Data

    API_HOME = waitForInput("API", 100); // Wait for Rpi to send the API URL
}


void loop() {
    if (WiFiMulti.run() == WL_CONNECTED) { 
        char* dataType = waitForInput("TYPE", 2); // Get the Data Type to be Sent
        /*
          dataType can be:
          1 -> Accelerometer Data
          2 -> GPS Data
          3 -> Oximeter Data 
        */
        char* uartData = waitForInput("MESSAGE", 2048); // Send Confirmation that ESP is ready to receive Data
        postRequest(dataType, uartData); // Send the request to the Server based on the Data Type
        
        delay(100); // To avoid Tight Looping
    }
}
