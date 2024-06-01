#include <PWM.h>
#define pwmPin 9  
int frequency = 12500;  
int dutyCycle = 90; 
int waktu = 30;


void setup() {
  Serial.begin(9600); 
  InitTimersSafe(); 
  pinMode(pwmPin, OUTPUT);
}

void loop() {
  if (Serial.available() > 0) {
    int receivedFrequency = Serial.parseInt(); 
    int receivedDutyCycle = Serial.parseInt();  
    int receivedTime = Serial.parseInt();  

    if (receivedFrequency  >= 1 && receivedFrequency  <= 25000) {

      frequency = receivedFrequency;  
      waktu = receivedTime; 

      SetPinFrequencySafe(pwmPin, frequency);
      analogWrite(pwmPin, map(dutyCycle, 0, 100, 0, 255)); 

      pwmWrite(pwmPin, dutyCycle);  
      delay(waktu * 1000);
    }

    else if (receivedFrequency  >= 1 && receivedFrequency  <= 25000 &&
             receivedDutyCycle >= 1 && receivedDutyCycle <= 100) {

      frequency = receivedFrequency; 
      dutyCycle = receivedDutyCycle;  
      waktu = receivedTime; 

      SetPinFrequencySafe(pwmPin, frequency); 
      analogWrite(pwmPin, map(dutyCycle, 0, 100, 0, 255));  

      pwmWrite(pwmPin, dutyCycle);  
      delay(waktu * 1000);
    }
    
    else {
      Serial.write("Frekuensi tidak valid. Gunakan frekuensi 1-25000 Hz.");

      SetPinFrequencySafe(pwmPin, 0); 
      analogWrite(pwmPin, map(dutyCycle, 0, 100, 0, 255));  

      pwmWrite(pwmPin, 0);  
    }
  }
}
