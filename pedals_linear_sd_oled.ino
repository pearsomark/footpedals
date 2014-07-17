/* Footpedals using encoder and SD library
 * 
 *
 * This example code is in the public domain.
 */

#include <Encoder.h>
#include <SD.h>
#include <Bounce.h>
#include <MP_SSD1306.h>

boolean enableKbd = true;
boolean enableTrnk = true;
boolean timingPulsetrain = true;

#define VERSION                 "FPL V0.66"
#define BLOCK_COUNT             1500U
#define BLOCKSIZE               512UL
#define TIMING_PULSE_INTERVAL   5000UL
#define TIMING_PULSE_WIDTH      5UL
#define KBD_PULSE_WIDTH         30UL
#define FUDGE_FACTOR            3

uint16_t blockCount = 1;
uint16_t seconds = 0;

// pins
const int enc_left_a     = 0;
const int enc_left_b     = 1;
const int enc_right_a    = 2;
const int enc_right_b    = 3;
const int sw_left        = 4;
const int sw_right       = 5;
const int enablePin      = 6;
const int pulsePin       = 7;
const int chipSelect     = 10;
const int oledReset      = 14;
const uint8_t kkey_space = 15;
const uint8_t kkey_t     = 16;
const uint8_t kkey_x     = 17;

Encoder footLeft(enc_left_a, enc_left_b);
Encoder footRight(enc_right_a, enc_right_b);

volatile uint32_t timeref = 0;
volatile uint32_t timepulseref = 0;
volatile uint32_t kbdtimeref = 0;

boolean sdstatus;
boolean recordFlag = false;
boolean pulseOn = false;
uint8_t kbd_down = 0;
String filename;
//File dataFile;
int bytecount = 0;
int calibrated = 0;
volatile boolean ldown = false;
volatile boolean rdown = false;
volatile boolean key_test_mode = false;
//   avoid using pins with LEDs attached
Bounce recordButton = Bounce(enablePin, 15); 
MP_SSD1306 display(oledReset);

Sd2Card card;
SdVolume volume;
SdFile root;
SdFile file;

uint8_t* pCache;
uint32_t* iCache;
uint32_t bgnBlock, endBlock;

// store error strings in flash to save RAM
#define error(s) error_P(PSTR(s))

void error_P(const char* str) {
  PgmPrint("error: ");
  SerialPrintln_P(str);
  if (card.errorCode()) {
    PgmPrint("SD error: ");
    Serial.print(card.errorCode(), HEX);
    Serial.print(',');
    Serial.println(card.errorData(), HEX);
  }
  while(1);
}

void setup() {
  display.begin(SSD1306_SWITCHCAPVCC);
  display.clearDisplay();   // clears the screen and buffer
  pinMode(sw_left, INPUT_PULLUP);
  pinMode(sw_right, INPUT_PULLUP);
  pinMode(enablePin, INPUT_PULLUP);
  pinMode(chipSelect, OUTPUT);
  pinMode(pulsePin, OUTPUT);
  pinMode(kkey_space, OUTPUT);
  pinMode(kkey_x, OUTPUT);
  pinMode(kkey_t, OUTPUT);
  digitalWrite(pulsePin, LOW);
  digitalWrite(kkey_space, LOW);
  digitalWrite(kkey_x, LOW);
  digitalWrite(kkey_t, LOW);
  Serial.begin(115200);
  oledDisplay(VERSION, false);
  if (digitalRead(enablePin) == LOW)
      key_test_mode = true;
  delay(3000);
  sdstatus = sdInit();
  resetAll();
}

long positionLeft  = -999;
long positionRight = -999;
int maxleft = 100;
int maxright = 100;

void loop() {
    long left, right, newLeft, newRight, inByte;
    uint32_t ts, rts;
    int lstate, rstate;
    boolean bstate = false;

    if (key_test_mode)
        sendTestKeys();
    recordButton.update();
    newLeft = footLeft.read();
    newRight = footRight.read();

    ts = millis();
    
    // end keyboard pulse
    if (kbd_down) { 
        if ((ts - kbdtimeref) > KBD_PULSE_WIDTH) {
            digitalWrite(kbd_down, LOW);
            kbd_down = 0;
        }
    }
    
    // output timing pulse while recording
    if (timingPulsetrain && recordFlag) {
        if ((ts - timepulseref) > TIMING_PULSE_INTERVAL)
            sendTimingPulse();
        if (pulseOn) {
            if ((ts - timepulseref) > TIMING_PULSE_WIDTH) {
                digitalWrite(pulsePin, LOW);
                pulseOn = false;
            }
        }
    }

    // new datapoint if something has moved
    if (newLeft != positionLeft || newRight != positionRight) {
        rts = millis()-timeref;
//         uint32_t ms = 0;
//         uint32_t sec = 0;
//         if (rts < 1000) {
//             ms = rts;
//     } else {
//         ms = rts % 1000;
//         sec = (rts / 1000) - seconds;
//         seconds = rts / 1000;
//     }
//     uint32_t tp = ms | (sec << 10);
    
    
    // get foot position
    //left = int(newLeft*(100.0/(float)maxleft));
    //right = int(newRight*(100.0/(float)maxright));
    left = newLeft;
    right = newRight;
    if (enableTrnk) {
      if (left < FUDGE_FACTOR)
        left = 0;
      if (right < FUDGE_FACTOR)
        right = 0;
    }   
    //String dataString = "";
    //if (recordFlag)
      //dataString += String(rts) + ", ";
    //dataString += String(left) + ", ";
    //dataString += String(right);
    
    lstate = digitalRead(sw_left);
    rstate = digitalRead(sw_right);
    if (lstate == LOW) {
      //dataString += ", 1";
      if (ldown == false) {
        ldown = true;
        if (rdown == false && enableKbd)
            sendKey(kkey_x);
//  	  Keyboard.print("x");
      }
    }
    if (lstate == HIGH) {
      //dataString += ", 0";
      ldown = false;
    }
  
    if (rstate == LOW) {
      //dataString += ", 1";
      if (rdown == false) {
        rdown = true;
        if (ldown == false && enableKbd)
            sendKey(kkey_t);
//	  Keyboard.print("t");
      }
    }
    if (rstate == HIGH) {
      //dataString += ", 0";
      rdown = false;
    }

     
    if (recordFlag) {
      if (sdstatus) {
	iCache[bytecount++] = (left << 16) | right;
	iCache[bytecount++] = rts |  (rdown << 31) | (ldown << 30);
	//iCache[bytecount++] = rts;
//        iCache[bytecount++] = tp | (left << 24) | (0xDE << 16);
         
        if (bytecount > 127) {
          if (sdstatus) {
            blockCount++;
            if (!card.writeData(pCache)) error("writeData failed");
          }
          bytecount = 0;
          memset(pCache, 0, BLOCKSIZE);
        }
//        dataFile.println(dataString);
//        Serial.println(dataString);
      }
      oledDisplaybits(TimeToString(rts), String(left), String(right), false, ldown, rdown);
    } else {
      oledDisplaybits("", String(left), String(right), true, ldown, rdown);
    }
    positionLeft = newLeft;
    positionRight = newRight;
  }
  
  // if a character is sent from the serial monitor,
  // reset both back to zero.
  if (Serial.available()) {
    inByte = Serial.read();
    if (inByte == 114) {  // r
      resetAll();
    }
    if (inByte == 115) {  // s
        if (! recordFlag)
            recordFlag = true;
        else
            recordFlag = false;
    }
    if (inByte == 99) {  // c
      // end multiple block write mode
      if (!card.writeData(pCache)) error("writeData failed");
      if (!card.writeStop()) error("writeStop failed");
      uint32_t filesize = blockCount * BLOCKSIZE;
      if (!file.truncate(filesize)) error("Could not truncate");
    }
    if (inByte == 97) {
        Serial.println("Press left pedal and enter '1'\nPress right pedal and enter '2'");
    }
    if (inByte == 49) {  // 1
        maxleft = footLeft.read();
        Serial.print("Left max ");
        Serial.println(maxleft);
    }
    if (inByte == 50) {  // 2
      maxright = footRight.read();
      Serial.print("Right max ");
      Serial.println(maxright);
      calibrated = 1;
    }
  }
  // start recording
  if (recordButton.fallingEdge() && recordFlag == false) {
    if (sdstatus) {
      delay(20);
//      oledDisplay("Start recording", false);
      recordFlag = true;
      bstate = true;
    } else {
      oledDisplay("SD error", false);
    }
    oledDisplaybits("00:00.000", "0", "0", false, false, false);
    timeref = millis();
    sendKey(kkey_space);
    sendTimingPulse();
  }
  // stop recording
  if (recordButton.fallingEdge() && recordFlag == true && bstate == false) {
    if ((millis() - timeref) > 2000) {
      oledDisplay("Stop recording", false);
      recordFlag = false;
      // end multiple block write mode
      if (!card.writeData(pCache)) error("writeData failed");
      if (!card.writeStop()) error("writeStop failed");
      uint32_t filesize = blockCount * BLOCKSIZE;
      if (!file.truncate(filesize)) error("Could not truncate");
      delay(500);
    }
  }
}

void resetAll() {
  char fname[15];
  footLeft.write(0);
  footRight.write(0);
  timeref = millis();
  blockCount = 1;
  if (sdstatus) {
    filename.toCharArray(fname, sizeof(fname));
    if (!file.createContiguous(&root, fname, BLOCKSIZE*BLOCK_COUNT)) {
      error("createContiguous failed");
    }
    // get the location of the file's blocks
    if (!file.contiguousRange(&bgnBlock, &endBlock)) {
      error("contiguousRange failed");
    }
    // clear the cache and use it as a 512 byte buffer
    pCache = volume.cacheClear();
    iCache = (uint32_t *)pCache;
    // tell card to setup for multiple block write with pre-erase
    if (!card.erase(bgnBlock, endBlock)) error("card.erase failed");
    if (!card.writeStart(bgnBlock, BLOCK_COUNT)) {
      error("writeStart failed");
    }
  } else {
    oledDisplay("No SD card", false);
  }
  delay(2000);
}

String getNextFilename() {
  String ss, logfile = "LOG001.BIN";
  char fname[15];
  int fnum, top = 0;
  File root;
  root = SD.open("/");
  while(true) { 
     File entry =  root.openNextFile();
     if (! entry) {
       break;
     }
    ss = entry.name();
    if (ss.startsWith("LOG0")) {
       fnum = ss.substring(3,7).toInt();
       if (fnum > top && entry.size() > 0) {
           if (entry.size() == 768000) {
               ss.toCharArray(fname, sizeof(fname));
               SD.remove(fname);
           }
               top = fnum;
       }
    }
   }
   if (top < 9)
     logfile = "LOG00" + String(top+1) + ".BIN";
   else
     logfile = "LOG0" + String(top+1) + ".BIN";
   return logfile;
}

boolean sdInit() {
  oledDisplay("Initializing SD card...", false);
  // make sure that the default chip select pin is set to
  // output, even if you don't use it:
  if (!SD.begin(chipSelect)) {
    oledDisplay("Card failed, or missing", false);
    // don't do anything more:
    return 0;
  }
  // initialize the SD card at SPI_FULL_SPEED for best performance.
  // try SPI_HALF_SPEED if bus errors occur.
  if (!card.init(SPI_FULL_SPEED)) error("card.init failed");
  // initialize a FAT volume
  if (!volume.init(&card)) error("volume.init failed"); 
  // open the root directory
  if (!root.openRoot(&volume)) error("openRoot failed");

  oledDisplay("card initialized.", false);
  filename = getNextFilename();
//  Serial.print("Save to ");
  oledDisplayStr(filename, false);
  return 1;
}

void oledDisplay(char *str, boolean invert) {
  display.clearDisplay();   // clears the screen and buffer
  display.setTextSize(1);
  display.setTextColor(WHITE);
  display.setCursor(0,0);
  display.println(str);
  display.display();
}
void oledDisplayScroll(char *str, boolean invert) {
  display.clearDisplay();   // clears the screen and buffer
  display.setTextSize(2);
  display.setTextColor(WHITE);
  display.setCursor(20,0);
  display.println(str);
  display.display();
  delay(1000);
  display.startscrollleft(0x00, 0x0F);
  delay(3000);
  display.stopscroll();
  display.clearDisplay();
}

void oledDisplayStr(String str, boolean invert) {
  display.clearDisplay();   // clears the screen and buffer
  display.setTextSize(1);
  display.setTextColor(WHITE);
  if (invert)
    display.setTextColor(BLACK, WHITE); // 'inverted' text
  display.setCursor(0,0);
  display.println(str);
  display.display();
}

void oledDisplaybits(String s1, String s2, String s3, boolean i1, boolean i2, boolean i3) {
  display.clearDisplay();   // clears the screen and buffer
  display.setTextSize(1);
  display.setTextColor(WHITE);
  if (i1)
    display.setTextColor(BLACK, WHITE); // 'inverted' text
  display.setCursor(0,0);
  display.print(s1);
  display.setTextColor(WHITE);
  if (i2)
    display.setTextColor(BLACK, WHITE);
  display.setCursor(55,8);
  display.print(s2);
  display.setTextColor(WHITE);
  if (i3)
    display.setTextColor(BLACK, WHITE);
  display.setCursor(77,8);
  display.print(s3);
  display.display();
}

String TimeToString(uint32_t t)
{
  if (t < 1000)
    return String(t);
  static char str[12];
//  long h = t / 3600;
  int ms = t % 1000;
  t = t / 1000;
  t = t % 3600;
  int m = t / 60;
  int s = t % 60;
  sprintf(str, "%02d:%02d:%03d", m, s, ms);
  return String(str);
}

/*
 * Start pulse for key. Check pulse end in loop()
 */
void sendKey(uint8_t k) {
    digitalWrite(k, HIGH);
    kbd_down = k;
    kbdtimeref = millis();
}

void sendTimingPulse() {
// change this if pulse width > 5ms
    digitalWrite(pulsePin, HIGH);
    pulseOn = true;
    timepulseref = millis();
}

void sendTestKeys() {
    unsigned long short_delay = 30;
    unsigned long long_delay = 500;
    digitalWrite(kkey_x, HIGH);   // turn the LED on (HIGH is the voltage level)
    delay(short_delay);               // wait for a second
    digitalWrite(kkey_x, LOW);
    delay(long_delay);
    digitalWrite(kkey_t, HIGH);
    delay(short_delay);
    digitalWrite(kkey_t, LOW);
    delay(long_delay);
    
}