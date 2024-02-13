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

void setup() {
    USE_SERIAL.begin(115200);
    USE_SERIAL.println("Starting...");
    USE_SERIAL.flush();

    WiFi.mode(WIFI_STA);
    WiFi.disconnect();
    int n = WiFi.scanNetworks();
    USE_SERIAL.print(n);
    USE_SERIAL.println(" network(s) found:");
    for (int i = 0; i < n; i++)
    {
      USE_SERIAL.print(WiFi.SSID(i) + ", ");
    }
    USE_SERIAL.println();

    char* APNAME = waitForInput("APNAME", 100);
    char* APAUTH = waitForInput("APAUTH", 100);
    WiFiMulti.addAP(APNAME, APAUTH);
    

    freeInputBuffer(APNAME);
    freeInputBuffer(APAUTH);

    API_HOME = waitForInput("API", 100);
}

void loop() {
    if (WiFiMulti.run() == WL_CONNECTED) { 
        // Read data from UART
        char* uartData = waitForInput("MESSAGE", 2048); // You need to implement this function to read UART data
        HTTPClient http;
        USE_SERIAL.println("Sending...");
        http.begin(API_HOME); // Change the URL to your server

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
        delay(100);
    }
}
