 
int Pin1 = A0;

float Avg = 0.0;
float A0 = 0.0;
float A0Slow = 0.0;
float Min = 0.0;
float Max = 0.0;

 
void setup() {
  Serial.begin(9600);
}
 
void loop() {
  A0 = analogRead(Pin1);
  if (A0 >= Max){ Max = A0}
  if (A0 <= Min){Min = A0}
  A0Slow = A0
  Avg = A0

  Serial.print(Avg);
  Serial.print(" ");
  Serial.print(A0);
  Serial.print(" ");
  Serial.print(A0Slow);
  Serial.print(" ");
  Serial.print(Min);
  Serial.print(" ");
  Serial.print(Max);
  Serial.write("\n");
 
  delay(1000);
}
