#include <Arduino.h>
#include <TMC5160.h>

const uint8_t SPI_CS = 25; // CS pin in SPI mode
const uint8_t SPI_DRV_ENN = 24;  // DRV_ENN pin in SPI mode

TMC5160_SPI *motor = new TMC5160_SPI(SPI_CS); //Use default SPI peripheral and SPI settings.

void setup()
{
  // USB/debug serial coms
  Serial.begin(9600);
  Serial.ignoreFlowControl();

  SPI.begin();
  pinMode(SPI_DRV_ENN, OUTPUT); 
  digitalWrite(SPI_DRV_ENN, LOW); // Active low

  // This sets the motor & driver parameters /!\ run the configWizard for your driver and motor for fine tuning !
  TMC5160::PowerStageParameters powerStageParams; // defaults.
  TMC5160::MotorParameters motorParams;
  motorParams.globalScaler = 87; // 87/256*3.1 A rms = 1.1 amp
  motorParams.irun = 31; // full current
  motorParams.ihold = 15;

    // Wait for the TMC5160 to answer back
    TMC5160_Reg::IOIN_Register ioin = { 0 };

    while (ioin.version != motor->IC_VERSION)
    {
      ioin.value = motor->readRegister(TMC5160_Reg::IO_INPUT_OUTPUT);

      if (ioin.value == 0 || ioin.value == 0xFFFFFFFF) 
      {
//DEBUG        Serial.println("No TMC5160 found.");
        delay(2000);
      }
      else
      {
/*DEBUG        Serial.println("Found a TMC device.");
        Serial.print("IC version: 0x");
        Serial.print(ioin.version, HEX);
        Serial.print(" (");
        if (ioin.version == motor->IC_VERSION)
          Serial.println("TMC5160).");
        else
          Serial.println("unknown IC !)"); */
      }
    }
  
  motor->begin(powerStageParams, motorParams, TMC5160::NORMAL_MOTOR_DIRECTION);

  // ramp definition
  motor->setRampMode(TMC5160::POSITIONING_MODE);
  motor->setMaxSpeed(400); // max steps per second (=120 rpm * 200 steps/rev / 60 sec/min)
  motor->setAcceleration(500); // steps per second squared

//DEBUG  Serial.println("starting up");

  delay(1000); // Standstill for automatic tuning
}

void loop()
{
  static bool dir = false;
  static bool mov = false;
  static char cmd[255] = { 0 };
  static uint8_t bpos = 0;

  if (mov) {
    if ( motor->isTargetPositionReached() )
    {
      delayMicroseconds(20000); // wait 2 ms between direction changes

      // reverse direction
      dir = !dir;

      motor->setTargetPosition(dir ? 200 : 0);  // 1 full rotation = 200steps, so go twice around
/*DEBUG      float xactual = motor->getCurrentPosition();
      float vactual = motor->getCurrentSpeed();
    Serial.print("target : ");
    Serial.print(dir ? 400 : 0);
    Serial.print("current position : ");
    Serial.print(xactual);
    Serial.print("\tcurrent speed : ");
    Serial.println(vactual); */
    } 
  } else {
    while ( ! motor->isTargetPositionReached() ) delayMicroseconds(100);
    delayMicroseconds(2000);
    if ((int)(motor->getCurrentPosition()*10) != 0) {
      // If no motion is desired, make sure we are stopped at 0
      dir = false;
      motor->setTargetPosition(0);
    }
  }

  while (Serial.available() && (cmd[bpos++] = Serial.read()) != '\r');  
  if (bpos > 0 && cmd[bpos-1] == '\r') {
    if (bpos == 1)
      goto empty; // empty command
    // process command
    int pos;
    switch (cmd[0]) {
      case 'X':
        pos = motor->getCurrentPosition()*10;
        if (mov)
          Serial.print("+");
        else
          Serial.print("X+");
        if (pos < 1000000)
          Serial.print('0');
        if (pos < 100000)
          Serial.print('0');
        if (pos < 10000)
          Serial.print('0');
        if (pos < 1000)
          Serial.print('0');
        if (pos < 100)
          Serial.print('0');
        if (pos < 10)
          Serial.print('0');
        Serial.print(pos);
        if (mov)
          Serial.print('\r');
        else
          Serial.print("\r\r");
        break;
      case 'D':
        mov = false;
        break;
      case 'E':
        if (bpos >= 18) {
          int i = 7;
          for (int j = 7; j < bpos; j++)
              if (cmd[j] == '-')
                i = bpos-1;
          if (i < bpos-1) {
              Serial.print("M");
              for (int j = 7; j < bpos-1; j++)
                Serial.print(cmd[j]);
        pos = motor->getCurrentPosition()*10;
          Serial.print("+");
        if (pos < 1000000)
          Serial.print('0');
        if (pos < 100000)
          Serial.print('0');
        if (pos < 10000)
          Serial.print('0');
        if (pos < 1000)
          Serial.print('0');
        if (pos < 100)
          Serial.print('0');
        if (pos < 10)
          Serial.print('0');
        Serial.print(pos);
              Serial.print('\r');
              mov = true;
            }
/*
          if (cmd[2] == 'C' && cmd[4] == 'S' && cmd[5] == '1' && cmd[6] == 'M') {
            int i = 7;
            while (cmd[i] != ',' && i < bpos)
              i++;
            for (int j = 7; j < bpos; j++)
              if (cmd[j] == '-')
                i = bpos; // these are initialize, not move commands
            if (i < bpos-1) {
              Serial.print("M");
              for (int j = 7; j < bpos-1; j++)
                Serial.print(cmd[j]);
//              Serial.print(",IA1M0, R");
        pos = motor->getCurrentPosition()*10;
          Serial.print("+");
        if (pos < 1000000)
          Serial.print('0');
        if (pos < 100000)
          Serial.print('0');
        if (pos < 10000)
          Serial.print('0');
        if (pos < 1000)
          Serial.print('0');
        if (pos < 100)
          Serial.print('0');
        if (pos < 10)
          Serial.print('0');
        Serial.print(pos);
              Serial.print('\r');
              mov = true;
            }
          }
*/
        }
        break;
      default:
        break;
    }
empty:
    bpos = 0;
  }
}
