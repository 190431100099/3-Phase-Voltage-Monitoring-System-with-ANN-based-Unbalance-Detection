void setup() {
  Serial.begin(9600);
  randomSeed(analogRead(A0)); // Inisialisasi seed random
}

void loop() {
  // Hasilkan data tegangan (210-230 V) dan arus (4-6 A) secara acak
  float VR = random(21000, 23000) / 100.0;
  float VS = random(21000, 23000) / 100.0;
  float VT = random(21000, 23000) / 100.0;
  float AR = random(400, 600) / 100.0;
  float AS = random(400, 600) / 100.0;
  float AT = random(400, 600) / 100.0;

  // Format string data
  String data = String(VR, 2) + "," + String(AR, 2) + 
                "," + String(VS, 2) + "," + String(AS, 2) + 
                "," + String(VT, 2) + "," + String(AT, 2);

  // Kirim data ke serial
  Serial.println(data);

  delay(1000); // Jeda 1 detik
}
