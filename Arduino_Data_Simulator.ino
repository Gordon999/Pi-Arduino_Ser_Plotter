//============Variables Measures ============

unsigned int A0Raw;      //Raw ADC Averaged -> 50mS
unsigned int A1Raw;      //Raw ADC Averaged -> 50 mS
byte nRaw;                       //Count of 25 samples
unsigned int A0Max;      //Raw Avg 1S Max
unsigned int A1Max;      //Raw Avg 1S Max
unsigned int A0Min;       //Raw Avg 1S Min
unsigned int A1Min;       //Raw Avg 1S Min
int A0Smp;       //Raw 1S Strobe
int A1Smp;       //Raw 1S Strobe
int A0Sum1S;     //Raw Sum 1S
int A1Sum1S;     //Raw Sum 1S
int n1S;         //Count of samples in 1S
int n10;         //n for 10s average
int Test;
int A0Avg1S;     //Raw ADC Averaged 1S
int A1Avg1S;     //Raw ADC Averaged 1S
float A0dB;        //A0 in dB
float A0dBslow;
float A0dB10;      //A0 avg 10sec.
float A1dB;        //A1 in dB
float A0dBRaw;     //A0 in dB
float A0dBMax;     //A0 in dB
float A0dBMin;     //A0 in dB
float A0dBAvg24;    //A0 in dB

//************Variables Simulation ***************

byte val; //used for counters
int x1;            //Simulation Sinus1
int y1;            //Simulation Sinus2
int x2;            //Simulation Cosinus2
int y2;            //Simulation Cosinus2
int x3;            //Simulation Cosinus3
int y3;            //Simulation Cosinus3
long z;            //Simulation Mixed
long m;            //Simulation Mixed
int n;             //Simulation Mixed
int l;             //Simulation Mixed
int p;             //Simulation Mixed

//************Variables Timers ***************
unsigned int   amount2mS = 0;
boolean        callMenu;
byte           counter50mS = 0;
unsigned int   amount50mS = 0;
boolean        timer1S;
byte           counter1S = 0;
boolean        timer1M;
byte           counter1M = 0;


void setup() {
  A0Max = 0;
  A0Min = 1024;
  A0dBAvg24 = 50;
  Serial.begin(9600); //UART in 9600 Baud;
  y1 = y2 = y3 = 1000;
  x1 = x2 = x3 = 0;
//  adc94u = 940;
//  adc47u = 470;
//  RatioADC = 1;
//  OffsetADC = 0;

  //set timer1 interrupt at 1Hz
  TCCR1A = 0; // set entire TCCR1A register to 0
  TCCR1B = 0; // same for TCCR1B
  TCNT1 = 0; //initialize counter value to 0
  // set compare match register for 1hz increments
#if F_CPU==16000000
  OCR1A = 15624; //=(16*10^6)/(1*1024) - 1 (must be <65536)
#elif F_CPU==8000000
  OCR1A = 7811; //=(8*10^6)/(1*1024) - 1 (must be <65536)
#endif
  // turn on CTC mode
  TCCR1B |= (1 << WGM12);
  // Set CS12 and CS10 bits for 1024 prescaler
  TCCR1B |= (1 << CS12) | (1 << CS10);
  // enable timer compare interrupt
  TIMSK1 |= (1 << OCIE1A);

#ifndef __AVR_ATmega32U4__
  //set timer2 interrupt at 500Hz
  TCCR2A = 0; // set entire TCCR2A register to 0
  TCCR2B = 0; // same for TCCR2B
  TCNT2 = 0; //initialize counter value to 0
  // set compare match register for 2khz increments
#if F_CPU==16000000
  OCR2A = 249; //=(16*10^6)/(1*1024) - 1 (must be <512)
#elif F_CPU==8000000
  OCR2A = 124; //=(8*10^6)/(1*1024) - 1 (must be <512)
#endif

  // turn on CTC mode
  TCCR2A |= (1 << WGM21);
  // Set CS20 , CS 21 and CS22 bit for 128 prescaler
  TCCR2B |= (1 << CS22) | (0 << CS21) | (1 << CS20);
  // enable timer compare interrupt
  TIMSK2 |= (1 << OCIE2A);
#endif

  sei();//allow interrupts
}

void loop() {

  if (nRaw >= 25) //running every 50mS (nRaw is ++ every 2mS)
  {
    //====(Running simulation)======
    n = random(0 , 80) + l;                  //Create 1% fast Noise+5% random variation at 1 sec pace
    m = max (x1, 0) + y2 / 6 + y3 / 8 + 120; //Half the first wave, mix with the second and third to create a pulsed, rectified AM wave type
    z = (m * m) / 2200 + n + 800;      // Square the result, add noise, add bias.
    A0Raw = z / 2;
    n = random(0 , 230);                        //Create 6% Noise
    m = max (x1, 0) - y2 / 8 + y3 / 6 + 120; //Half the first wave, mix with the second and third to create a pulsed, rectified AM wave type
    z = (m * m) / 2200 + n + 780;      // Square the result, add noise, add bias.
    A1Raw = z / 2;
    nRaw = 0; 
    //====(Building 1S Averages, Max, Mins)======
    A0Sum1S += A0Raw; A1Sum1S += A1Raw; ++n1S;                          //Sum for Averaging
    A0Max = max(A0Max, A0Raw); A0Min = min(A0Min, A0Raw); //computing max,min, storing the last sample
    ++amount50mS;
  }
  //end if (nRaw >=25)

  if (timer1S)
  {
    //====(Running simulation)======
    y1 = y1 - x1 / 20;            //Compute a Cosinus
    x1 = x1 + y1 / 20;            //Compute a Sinus
    y2 = y2 - x2 / 31;            //Compute a somewhat slower Cosinus
    x2 = x2 + y2 / 31;            //Compute a somewhat slower Sinus
    y3 = y3 - x3 / 13;            //Compute a slower Cosinus
    x3 = x3 + y3 / 13;            //Compute a slower Sinus
    l = random(0 , 100);          //Create 5% random variation
    p = random(0 , 2000);         //Create Pulse Disturbances
    if (p % 128 >= 125)           // Approx every 2 Minute
    {
      A0Sum1S += p; A0Max += p / 8 ; // Issue a pulse of variable amplitude
    }

    // Final forming the displayed variables
    A0Sum1S = A0Sum1S / n1S;   
    A1Sum1S = A1Sum1S / n1S;
    A0dB = float(A0Sum1S)  / 10;
    A0dBslow = A0dBslow + (A0dB - A0dBslow) / 2;
    A1dB = float(A1Sum1S)  / 10;
    A0dBMax = float(A0Max) / 10;
    A0dBMin = float(A0Min) / 10;
    A0dBRaw = float(A0Smp) / 10;
    n1S = 0;   A0Sum1S = 0;   A1Sum1S = 0; A0Max = 0;    A0Min = 2000;

   // Compute A0 smoothed with a 24H time constant
    if ( millis() < 1000000)
  {
    //the first 20 Minutes ~Avg24 with a 10 minute time constant
    A0dBAvg24 = A0dBAvg24 + (A0dB - A0dBAvg24) / 600;
    }
    else
    {
      //after the first 20 Minutes ~Avg24 with a 24h time constant
      A0dBAvg24 = A0dBAvg24 + (A0dB - A0dBAvg24) / 87000;
    }

//====(Reporting )======
    Serial.print(A0dBAvg24); prSp();  Serial.print(A0dB); prSp(); Serial.print(A0dBslow); prSp(); Serial.print(A0dBMin); prSp(); Serial.println(A0dBMax);
//    Serial.print("2mS=");     Serial.print(amount2mS);    prTab();  Serial.print("50mS=");    Serial.print(amount50mS);    prTab();   Serial.print("ADC=");  Serial.println(A0Raw);
    amount2mS = 0;
    amount50mS = 0;
    timer1S = false;

  } //end (timer1S) 

}  //end void(loop) 


//============Timer relays============

ISR(TIMER1_COMPA_vect) //timer1 interrupt 1Hz
{
  //every second
  timer1S = true;
  counter50mS = 0;
  if (millis() / 1000 % 60 == 20) //every minute delayed by 20s
  {
    timer1M = true;
  }
}
//end ISR(TIMER1_COMPA_vect)

ISR(TIMER2_COMPA_vect) //timer1 interrupt 500Hz
{
 ++nRaw;  ++amount2mS; 
}
//end ISR(TIMER2_COMPA_vect)


//************Functions modules*****************

void prDot()    // Print "." on Serial
{
  Serial.print('.');
}
void prTab()  // Print a " | " on Serial
{
  Serial.print(" | ");
}

void prSp()
{
  Serial.print(' '); //Print a " " on Serial
}

void prLe()
{
  Serial.print('<'); //Print a "<" on Serial
}
