#include <Wire.h>
#include <SendOnlySoftwareSerial.h>
#include <Kalman.h> // Source: https://github.com/TKJElectronics/KalmanFilter

//#define RESTRICT_PITCH // Comment out to restrict roll to ±90deg instead - please read: http://www.freescale.com/files/sensors/doc/app_note/AN3461.pdf
#define CALIBRATE_ACC

SendOnlySoftwareSerial mySerial (1);  // Tx pin

Kalman kalmanX; // Create the Kalman instances
Kalman kalmanY;
Kalman kalmanZ;

//===============================================


// Arduino Wire library is required if I2Cdev I2CDEV_ARDUINO_WIRE implementation
// is used in I2Cdev.h
#include "Wire.h"

// I2Cdev and MPU6050 must be installed as libraries, or else the .cpp/.h files
// for both classes must be in the include path of your project
#include "I2Cdev.h"

#include "MPU6050_6Axis_MotionApps20.h"
//#include "MPU6050.h" // not necessary if using MotionApps include file

// class default I2C address is 0x68
// specific I2C addresses may be passed as a parameter here
// AD0 low = 0x68 (default for SparkFun breakout and InvenSense evaluation board)
// AD0 high = 0x69
MPU6050 mpu;

/* =========================================================================
/* IMU Data */
int CALIBRATE_GYRO = 1;
bool dmpReady = false;  // set true if DMP init was successful
uint8_t devStatus;      // return status after each device operation (0 = success, !0 = error)
uint16_t packetSize;    // expected DMP packet size (default is 42 bytes)
float ypr[3];
Quaternion q;
VectorFloat gravity;
uint8_t fifoBuffer[64]; // FIFO storage buffer
uint8_t mpuIntStatus;   // holds actual interrupt status byte from MPU
uint16_t fifoCount;     // count of all bytes currently in FIFO

double accX, accY, accZ;
double gyroX, gyroY, gyroZ;
int16_t tempRaw;

double gyroXangle, gyroYangle; // Angle calculate using the gyro only
double compAngleX, compAngleY; // Calculated angle using a complementary filter
double kalAngleX, kalAngleY; // Calculated angle using a Kalman filter

uint32_t timer;
uint8_t i2cData[14]; // Buffer for I2C data
int state;

//  Use the following global variables 
//  to calibrate the gyroscope sensor and accelerometer readings
float    base_x_gyro = 0;
float    base_y_gyro = 0;
float    base_z_gyro = 0;
float    base_x_accel = 0;
float    base_y_accel = 0;
float    base_z_accel = 0;


// ================================================================
// ===                CALIBRATION_ROUTINES                       ===
// ================================================================
// Simple calibration - just average first few readings to subtract
// from the later data
void calibrate_gyro() {
  float num_readings = 10;

  // Discard the first reading (don't know if this is needed or
  // not, however, it won't hurt.)
  while (i2cRead(0x3B, i2cData, 14));
  accX = (int16_t)((i2cData[0] << 8) | i2cData[1]);
  accY = (int16_t)((i2cData[2] << 8) | i2cData[3]);
  accZ = (int16_t)((i2cData[4] << 8) | i2cData[5]);
  tempRaw = (int16_t)((i2cData[6] << 8) | i2cData[7]);
  gyroX = (int16_t)((i2cData[8] << 8) | i2cData[9]);
  gyroY = (int16_t)((i2cData[10] << 8) | i2cData[11]);
  gyroZ = (int16_t)((i2cData[12] << 8) | i2cData[13]);
  // Read and average the raw values
  for (int i = 0; i < num_readings; i++) {
    gyroX = (int16_t)((i2cData[8] << 8) | i2cData[9]);
    gyroY = (int16_t)((i2cData[10] << 8) | i2cData[11]);
    gyroZ = (int16_t)((i2cData[12] << 8) | i2cData[13]);;
    base_x_gyro += gyroX;
    base_y_gyro += gyroY;
    base_z_gyro += gyroZ;
  }
  
  base_x_gyro /= num_readings;
  base_y_gyro /= num_readings;
  base_z_gyro /= num_readings;
}

// ================================================================
// ===               INTERRUPT DETECTION ROUTINE                ===
// ================================================================

volatile bool mpuInterrupt = false;     // indicates whether MPU interrupt pin has gone high
void dmpDataReady() {
    mpuInterrupt = true;
}

void setup(){  
   mySerial.begin(9600);
   Wire.begin();
#if ARDUINO >= 157
  Wire.setClock(400000UL); // Set I2C frequency to 400kHz
#else
  TWBR = ((F_CPU / 400000UL) - 16) / 2; // Set I2C frequency to 400kHz
#endif

/*
// ================================================================
// ===                DMP                     ===
// ================================================================
  
  mySerial.println(F("Initializing DMP..."));
  devStatus = mpu.dmpInitialize();
  
  // make sure it worked (returns 0 if so)
  if (devStatus == 0) {
      // turn on the DMP, now that it's ready
      mySerial.println(F("Enabling DMP..."));
      mpu.setDMPEnabled(true);

      // set our DMP Ready flag so the main loop() function knows it's okay to use it
      mySerial.println(F("DMP ready! Waiting for first interrupt..."));
      dmpReady = true;
      
      // Set the full scale range of the accelerometer
      //uint8_t AFS_SEL = 0;
      //mpu.setFullScaleAccelRange(AFS_SEL);

      // get expected DMP packet size for later comparison
      packetSize = mpu.dmpGetFIFOPacketSize();
  } else {
      // ERROR!
      // 1 = initial memory load failed
      // 2 = DMP configuration updates failed
      // (if it's going to break, usually the code will be 1)
      mySerial.print(F("DMP Initialization failed (code "));
      mySerial.print(devStatus);
      mySerial.println(F(")"));
  }//*/

  i2cData[0] = 7; // Set the sample rate to 1000Hz - 8kHz/(7+1) = 1000Hz
  i2cData[1] = 0x00; // Disable FSYNC and set 260 Hz Acc filtering, 256 Hz Gyro filtering, 8 KHz sampling
  i2cData[2] = 0x00; // Set Gyro Full Scale Range to ±250deg/s
  i2cData[3] = 0x00; // Set Accelerometer Full Scale Range to ±2g
  while (i2cWrite(0x19, i2cData, 4, false));; // Write to all four registers at once
  while (i2cWrite(0x6B, 0x01, true));; // PLL with X axis gyroscope reference and disable sleep mode

  while (i2cRead(0x75, i2cData, 1));

  if (i2cData[0] != 0x68) { // Read "WHO_AM_I" register
    mySerial.print(F("Error reading sensor"));
    while (1);
  }

  delay(100); // Wait for sensor to stabilize
  
  /* Set kalman and gyro starting angle */
  while (i2cRead(0x3B, i2cData, 6));
  accX = (int16_t)((i2cData[0] << 8) | i2cData[1]);
  accY = (int16_t)((i2cData[2] << 8) | i2cData[3]);
  accZ = (int16_t)((i2cData[4] << 8) | i2cData[5]);

  // Source: http://www.freescale.com/files/sensors/doc/app_note/AN3461.pdf eq. 25 and eq. 26
  // atan2 outputs the value of -π to π (radians) - see http://en.wikipedia.org/wiki/Atan2
  // It is then converted from radians to degrees
#ifdef RESTRICT_PITCH // Eq. 25 and 26
  double roll  = atan2(accY, accZ) * RAD_TO_DEG;
  double pitch = atan(-accX / sqrt(accY * accY + accZ * accZ)) * RAD_TO_DEG;
#else // Eq. 28 and 29
  double roll  = atan(accX / sqrt(accX * accX + accZ * accZ)) * RAD_TO_DEG;
  double pitch = atan2(accY, accZ) * RAD_TO_DEG;
#endif

  kalmanX.setAngle(roll); // Set starting angle
  kalmanY.setAngle(pitch);
  gyroXangle = roll;
  gyroYangle = pitch;
  compAngleX = roll;
  compAngleY = pitch;
  timer = micros();
  if (CALIBRATE_GYRO){
    calibrate_gyro();
  }

}
void loop(){
  /* Update all the values */
  
  while (i2cRead(0x3B, i2cData, 14));
  accX = (int16_t)((i2cData[0] << 8) | i2cData[1]);
  accY = (int16_t)((i2cData[2] << 8) | i2cData[3]);
  accZ = (int16_t)((i2cData[4] << 8) | i2cData[5]);
  tempRaw = (int16_t)((i2cData[6] << 8) | i2cData[7]);
  gyroX = (int16_t)((i2cData[8] << 8) | i2cData[9]);
  gyroY = (int16_t)((i2cData[10] << 8) | i2cData[11]);
  gyroZ = (int16_t)((i2cData[12] << 8) | i2cData[13]);

  double dt = (double)(micros() - timer) / 1000000; // Calculate delta time
  timer = micros();

  // Source: http://www.freescale.com/files/sensors/doc/app_note/AN3461.pdf eq. 25 and eq. 26
  // atan2 outputs the value of -π to π (radians) - see http://en.wikipedia.org/wiki/Atan2
  // It is then converted from radians to degrees
#ifdef RESTRICT_PITCH // Eq. 25 and 26
  double roll  = atan2(accY, accZ) * RAD_TO_DEG;
  double pitch = atan(-accX / sqrt(accY * accY + accZ * accZ)) * RAD_TO_DEG;
#else // Eq. 28 and 29
  double roll  = atan(accX / sqrt(accX * accX + accZ * accZ)) * RAD_TO_DEG;
  double pitch = atan2(accY, accZ) * RAD_TO_DEG;
#endif

  double gyroXrate = (gyroX - base_x_gyro) / 131.0; // Convert to deg/s
  double gyroYrate = (gyroY - base_y_gyro) / 131.0; // Convert to deg/s
  double gyroZrate = (gyroZ - base_z_gyro)/ 131.0; // Convert to deg/s

#ifdef RESTRICT_PITCH
  // This fixes the transition problem when the accelerometer angle jumps between -180 and 180 degrees
  if ((roll < -90 && kalAngleX > 90) || (roll > 90 && kalAngleX < -90)) {
    kalmanX.setAngle(roll);
    compAngleX = roll;
    kalAngleX = roll;
    gyroXangle = roll;
  } 
  else
    kalAngleX = kalmanX.getAngle(roll, gyroXrate, dt); // Calculate the angle using a Kalman filter

  if (abs(kalAngleX) > 90)
    gyroYrate = -gyroYrate; // Invert rate, so it fits the restriced accelerometer reading
  kalAngleY = kalmanY.getAngle(pitch, gyroYrate, dt);
  
#else
  if (pitch < -90 && kalAngleY > 90) {
    kalmanY.setAngle(kalmanY.getCurrentAngle()-360);
    compAngleY = kalmanY.getCurrentAngle();
    //gyroXangle = kalmanY.getCurrentAngle();
    kalAngleY = kalmanY.getAngle(pitch, gyroXrate, dt);
  }  
  else if (pitch > 90 && kalAngleY < -90) {
    kalmanY.setAngle(kalmanY.getCurrentAngle()+360);
    compAngleY = kalmanY.getCurrentAngle();
    //gyroXangle = kalmanY.getCurrentAngle();
    kalAngleY = kalmanY.getAngle(pitch, gyroXrate, dt);
  }
  
  else
    kalAngleY = kalmanY.getAngle(pitch, gyroXrate, dt); // Calculate the angle using a Kalman filter

  //if (abs(kalAngleY) > 90)
    //gyroXrate = -gyroXrate; // Invert rate, so it fits the restriced accelerometer reading
  kalAngleX = kalmanX.getAngle(roll, gyroXrate, dt); // Calculate the angle using a Kalman filter
#endif
  
  gyroXangle += gyroXrate * dt; // Calculate gyro angle without any filter
  gyroYangle += gyroYrate * dt;
  //gyroXangle += kalmanX.getRate() * dt; // Calculate gyro angle using the unbiased rate
  //gyroYangle += kalmanY.getRate() * dt;

  compAngleX = 0.93 * (compAngleX + gyroXrate * dt) + 0.07 * roll; // Calculate the angle using a Complimentary filter
  compAngleY = 0.93 * (compAngleY + gyroYrate * dt) + 0.07 * pitch;

  // Reset the gyro angle when it has drifted too much
  
  if (gyroXangle < -180)
    gyroXangle += 360;
  else if (gyroXangle > 180)
    gyroXangle -= 360;
    
  if (gyroYangle < -180 || gyroYangle > 180)
    gyroYangle = kalAngleY;

     // reset interrupt flag and get INT_STATUS byte
    mpuInterrupt = false;
    mpuIntStatus = mpu.getIntStatus();

    // get current FIFO count
    fifoCount = mpu.getFIFOCount();

    // check for overflow (this should never happen unless our code is too inefficient)
    /*if ((mpuIntStatus & 0x10) || fifoCount == 1024) {
        // reset so we can continue cleanly
        mpu.resetFIFO();
        Serial.println(F("FIFO overflow!"));

    // otherwise, check for DMP data ready interrupt (this should happen frequently)
    } else if (mpuIntStatus & 0x02) {
        // wait for correct available data length, should be a VERY short wait            
    }
  
         /* Print Data */
  double seconds = timer/1000000.0;
  //if (1) //(state == LOW) 
        //SoftSerial.begin(9600); // begin communication
        //mySerial.print("a/g:\t");
      
        mySerial.print(seconds); mySerial.print("\t");  
        //mySerial.print(accX); mySerial.print("\t");
        //mySerial.print(accY); mySerial.print("\t");
        //mySerial.print(accZ); mySerial.print("\t");
        
        mySerial.print(gyroXrate); mySerial.print("\t");
        mySerial.print(gyroYrate); mySerial.print("\t");
        mySerial.print(gyroZrate); mySerial.print("\t");
        
        //double temperature = (double)tempRaw / 340.0 + 36.53;
        //Serial.print(temperature); Serial.print("\t");

        //mySerial.print(kalmanX.getRate()); mySerial.print("\t");
        mySerial.print(kalmanY.getRate()); mySerial.print("\t");

        mySerial.print(gyroXangle); mySerial.print("\t");
        mySerial.print(gyroYangle); mySerial.print("\t");

        mySerial.print(pitch); mySerial.print("\t");
        mySerial.print(roll); mySerial.print("\t");

        //mySerial.print(kalAngleX); mySerial.print("\t");
        mySerial.print(kalAngleY); mySerial.print("\t");
        
        //Serial.print(compAngleX); Serial.print("\t");

       //mySerial.print(ypr[0]* RAD_TO_DEG, 2); mySerial.print("\t");
       //mySerial.print(-ypr[1]* RAD_TO_DEG, 2); mySerial.print("\t");
       //mySerial.print(ypr[2]* RAD_TO_DEG, 2); mySerial.print("\t");

       //mySerial.print(base_z_gyro); mySerial.print("\t");
       
       mySerial.print("\n"); 
          
}


