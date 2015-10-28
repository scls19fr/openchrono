/*
An Arduino code to acquire data from ADC
and send to serial
*/


/*
Read data with terminal
minicom -H -D /dev/ttyUSB0 -b 57600
kermit (ckermit or gkermit)
gtkterm
cutecom
*/

/*
ToDo
measure time ellapsed with millis()

*/

void setup() {
  Serial.begin(57600); // 9600 14400 19200 28800 38400 57600 115200
  //Serial.print("setup\n");

  delay(50);
  while (!Serial.available()) {
    Serial.write(0x07);
    delay(300);
  }
  // read the byte that Python will send over
  Serial.read();
}

void loop() {
  int sensor0;
  int sensor1;
  
  //sensor0 = 128;
  sensor0 = analogRead(A0);
  sensor1 = analogRead(A1);
  
  //Serial.println(sensor0);
  
  /*
  Serial.print(sensor0);
  Serial.print(";");
  Serial.print(sensor1);
  Serial.print("\n");
  */
  
  Serial.write(0x07);
  Serial.write(0x00); // sensors board id
  
  Serial.write(highByte(sensor0));
  Serial.write(lowByte(sensor0));

  Serial.write(highByte(sensor1));
  Serial.write(lowByte(sensor1));
  //Serial.write(0x99);
  
  Serial.write(0x0d); // \r
  Serial.write(0x0a); // \n
  
  Serial.flush();
  
  //delay(100);
}

