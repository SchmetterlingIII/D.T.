// This interprets the data from the ArduinoUno and send its via the serial to Thonny (the Python interpreter).

// Given that I was new to both consumer electronics and C++, I used `gemini-2.5-pro` as the foundation of this prompt, specifying the need for the multiplexer to interpret the channels of IMU data and send them off.

// Include the standard library for I2C communication.
#include <Wire.h>

// --- I2C Addresses ---
#define MPU6050_ADDR      0x68 // I2C address of the MPU6050
#define TCA_ADDRESS       0x70 // I2C address of the TCA9548A multiplexer

// --- MPU6050 Register Addresses ---
#define MPU6050_PWR_MGMT_1   0x6B
#define MPU6050_WHO_AM_I     0x75
#define MPU6050_ACCEL_XOUT_H 0x3B
#define MPU6050_GYRO_CONFIG  0x1B
#define MPU6050_ACCEL_CONFIG 0x1C

// --- Adjustable Delay ---
// The delay in milliseconds after each full cycle of sensor readings.
#define LOOP_DELAY_MS 150

// This array will keep track of which channels have a successfully connected MPU6050.
bool mpu_found[8] = {false, false, false, false, false, false, false, false};
bool any_sensor_found = false;

// Conversion factors for raw data to real-world units.
const float ACCEL_SCALE_FACTOR = 16384.0; // For ±2g range
const float GYRO_SCALE_FACTOR = 131.0;   // For ±250°/s range

void tca_select(uint8_t channel) {
  if (channel > 7) return;
  Wire.beginTransmission(TCA_ADDRESS);
  Wire.write(1 << channel);
  Wire.endTransmission();
}

void initializeMPU6050() {
  Wire.beginTransmission(MPU6050_ADDR);
  Wire.write(MPU6050_PWR_MGMT_1);
  Wire.write(0);
  Wire.endTransmission(true);

  Wire.beginTransmission(MPU6050_ADDR);
  Wire.write(MPU6050_ACCEL_CONFIG);
  Wire.write(0x00);
  Wire.endTransmission(true);
  
  Wire.beginTransmission(MPU6050_ADDR);
  Wire.write(MPU6050_GYRO_CONFIG);
  Wire.write(0x00);
  Wire.endTransmission(true);
}

bool testMPU6050Connection() {
  Wire.beginTransmission(MPU6050_ADDR);
  Wire.write(MPU6050_WHO_AM_I);
  Wire.endTransmission(false);
  Wire.requestFrom(MPU6050_ADDR, 1);
  return (Wire.read() == 0x68);
}

void readRawData(int16_t* ax, int16_t* ay, int16_t* az, int16_t* gx, int16_t* gy, int16_t* gz) {
  Wire.beginTransmission(MPU6050_ADDR);
  Wire.write(MPU6050_ACCEL_XOUT_H);
  Wire.endTransmission(false);
  Wire.requestFrom(MPU6050_ADDR, 14, true);

  *ax = (Wire.read() << 8 | Wire.read());
  *ay = (Wire.read() << 8 | Wire.read());
  *az = (Wire.read() << 8 | Wire.read());
  Wire.read(); Wire.read(); // Skip temperature data
  *gx = (Wire.read() << 8 | Wire.read());
  *gy = (Wire.read() << 8 | Wire.read());
  *gz = (Wire.read() << 8 | Wire.read());
}

void setup() {
  Serial.begin(115200);
  while (!Serial) { delay(10); }

  Wire.begin();
  Serial.println("Scanning for MPU6050 sensors...");

  for (uint8_t i = 0; i < 8; i++) {
    tca_select(i);
    if (testMPU6050Connection()) {
      Serial.print("MPU6050 found on channel: ");
      Serial.println(i);
      initializeMPU6050();
      mpu_found[i] = true;
      any_sensor_found = true;
    }
  }
  
  Serial.print("Available channels: "); // This outputs which channels are available into a list that can later be interpreted in Python
  bool first = true;
  for (uint8_t i = 0; i < 8; i++) {
    if (mpu_found[i]) {
      if (!first) {
        Serial.print(", ");
      }
      Serial.print(i);
      first = false;
    }
  }
  Serial.println();
  
  Serial.println("Scan complete.");

  if (!any_sensor_found) {
    Serial.println("No sensors found. Halting.");
    while (1) { delay(100); }
  }

  // Count the number of sensors that were actually found
  uint8_t found_sensor_count = 0;
  for (uint8_t i = 0; i < 8; i++) {
    if (mpu_found[i]) {
      found_sensor_count++;
    }
  }
  
  // Wait for the start command
  Serial.print("Number of sensors: ");
  Serial.println(found_sensor_count);
  Serial.println("Waiting for 'begin program' command from Python...");
  String command = "";
  while (command != "begin program") {
    if (Serial.available() > 0) {
      command = Serial.readStringUntil('\n');
      command.trim(); // Remove any whitespace or newline characters
    }
  }
  // Serial.println("Begin command received. Starting data stream...");
}

void loop() {
  int16_t accX_raw, accY_raw, accZ_raw;
  int16_t gyroX_raw, gyroY_raw, gyroZ_raw;

  for (uint8_t i = 0; i < 8; i++) {
    if (mpu_found[i]) {
      tca_select(i);
      readRawData(&accX_raw, &accY_raw, &accZ_raw, &gyroX_raw, &gyroY_raw, &gyroZ_raw);

      Serial.print(accX_raw / ACCEL_SCALE_FACTOR, 4);
      Serial.print(",");
      Serial.print(accY_raw / ACCEL_SCALE_FACTOR, 4);
      Serial.print(",");
      Serial.print(accZ_raw / ACCEL_SCALE_FACTOR, 4);
      Serial.print(",");
      Serial.print(gyroX_raw / GYRO_SCALE_FACTOR, 4);
      Serial.print(",");
      Serial.print(gyroY_raw / GYRO_SCALE_FACTOR, 4);
      Serial.print(",");
      Serial.print(gyroZ_raw / GYRO_SCALE_FACTOR, 4);
      Serial.print(",");
      Serial.println(i);
    }
  }
  
  delay(LOOP_DELAY_MS);
}