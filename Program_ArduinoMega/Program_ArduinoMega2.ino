#include <PZEM004Tv30.h>

// PZEM pada masing-masing port serial Mega
PZEM004Tv30 pzemR(&Serial1, 0x03);
PZEM004Tv30 pzemS(&Serial2);
PZEM004Tv30 pzemT(&Serial3, 0x01);

// Pin Relay
const int relayPin = 22; 
const int BuzzerPin = 23;

// Variabel Data
float teganganR, teganganS, teganganT;
float arusR, arusS, arusT;

// KOEFISIEN KALIBRASI
// Fase R
const float CAL_V_R = 0.9966;
const float CAL_I_R = 0.9179;

// Fase S
const float CAL_V_S = 1.0025;
const float CAL_I_S = 0.9204;

// Fase T
const float CAL_V_T = 0.9962;
const float CAL_I_T = 0.9725;
// 

void setup() {
  Serial.begin(9600);
  Serial1.begin(9600);
  Serial2.begin(9600);
  Serial3.begin(9600);

  // Setup Relay
  pinMode(relayPin, OUTPUT);
  pinMode(BuzzerPin, OUTPUT);
  digitalWrite(relayPin, HIGH); // Relay OFF awal
  digitalWrite(BuzzerPin, HIGH);

  delay(1000);
}

void bacaPZEM() {
  //Nilai Mentah (Raw)
  float raw_vR = pzemR.voltage();
  float raw_vS = pzemS.voltage();
  float raw_vT = pzemT.voltage();

  float raw_iR = pzemR.current();
  float raw_iS = pzemS.current();
  float raw_iT = pzemT.current();

  //Kalibrasi (Raw * Faktor)
  if (!isnan(raw_vR)) teganganR = raw_vR * CAL_V_R;
  else teganganR = 0;
  if (!isnan(raw_vS)) teganganS = raw_vS * CAL_V_S;
  else teganganS = 0;
  if (!isnan(raw_vT)) teganganT = raw_vT * CAL_V_T;
  else teganganT = 0;
  if (!isnan(raw_iR)) arusR = raw_iR * CAL_I_R;
  else arusR = 0;
  if (!isnan(raw_iS)) arusS = raw_iS * CAL_I_S;
  else arusS = 0;
  if (!isnan(raw_iT)) arusT = raw_iT * CAL_I_T;
  else arusT = 0;
}

void loop() {
  bacaPZEM();

  // Kirim data ke main.py
  Serial.print(teganganR, 2); Serial.print(",");
  Serial.print(teganganS, 2); Serial.print(",");
  Serial.print(teganganT, 2); Serial.print(",");
  Serial.print(arusR, 3); Serial.print(",");
  Serial.print(arusS, 3); Serial.print(",");
  Serial.println(arusT, 3);

  //terima perintah dari main.py
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();

    if (command == "UNBALANCE") {
      digitalWrite(relayPin, LOW); // Relay ON
      digitalWrite(BuzzerPin, LOW); // Buzzer ON
    } 
    else if (command == "BALANCE") {
      digitalWrite(relayPin, HIGH); // Relay OFF
      digitalWrite(BuzzerPin, HIGH); // Buzzer OFF
    }
  }

  delay(1000);
}