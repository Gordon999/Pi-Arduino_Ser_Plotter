 
int Pin1 = A0;
int Pin2 = A1;
int Pin3 = A2;
int Pin4 = A3;
int Pin5 = A4;

float Value1 = 0.0;
float Value2 = 0.0;
float Value3 = 0.0;
float Value4 = 0.0;
float Value5 = 0.0;
 
void setup() {
  Serial.begin(9600);
}
 
void loop() {
  Value1 = analogRead(Pin1);
  Value2 = analogRead(Pin2);
  Value3 = analogRead(Pin3);
  Value4 = analogRead(Pin4);
  Value5 = analogRead(Pin5);
  Serial.print(Value1);
  Serial.print(" ");
  Serial.print(Value2);
  Serial.print(" ");
  Serial.print(Value3);
  Serial.print(" ");
  Serial.print(Value4);
  Serial.print(" ");
  Serial.print(Value5);
  Serial.write("\n");
 
  delay(1000);
}
