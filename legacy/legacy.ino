#include <ESP8266WiFi.h>
#include <ESP8266WiFiMulti.h>
#include <WiFiClientSecure.h>
#include <TimeLib.h>
#include <EEPROM.h>

WiFiClient client;                //(client) tablet/phone/etc <---> uBot (ESP8266 server)
WiFiServer server(80);            //(client) tablet/phone/etc <---> uBot (ESP8266 server)
WiFiClientSecure client_sec;      //uBot <---> WEB (through GET queries)
ESP8266WiFiMulti wifiMulti;       //uBot <---> AP

boolean conn;                     //connection to host status
const char* host = "reped.hu";    //db's host
const int port = 443;             //host's https port
const char* fingerprint = "FA 22 47 40 8F 75 3D 07 CB 94 6D FE 7E 4D D7 70 86 41 25 73";  //host's fingerprint,
String URL0 = "/assets/ESP/multiAP.php?OP=0&ID=1&CHK=wkWEBkUBWf7ps9qvXnPBMNxX&AP=";       //URL for mySQL pseudodelete
String URL1 = "/assets/ESP/multiAP.php?OP=1&ID=1&CHK=wkWEBkUBWf7ps9qvXnPBMNxX&AP=";       //URL for mySQL select
String URL = URL1;              //URL slot for GET
String line;                    //for received data after GET

char* ssid = "uBot";            //fallback SSID
char* password = "robotika";    //fallback PWD
String issid;                   //string for GET the SSID
String ipassword;               //and pwd from internet
String APs;                     //list of added APs (to multiWifi)

const int eeprom_ssid = 400;    //reserved bytes for APs
byte earray[eeprom_ssid];       //APs EEPROM in an array
int origo[3];                   //AP record boundaries... START RECORD/SSID: 20/17 (last/others), END SSID, START PWD: 18, END RECORD/PWD: 19
int gmt_poz;                    //for received time stamp
byte TZ = 1;                    //time zone: GMT+1
byte sl = 11;                   //multiAP slots for APs: 10 user defined + 1 fallback
unsigned long pM = 0;           //past millis() for timer
long interval = 60000;          //timer interval
bool s_on = false;              //uBot's server status
String request;                 //request to uBot's server
byte q = 0;                     //(semi)autocounter for for-loop


const byte in1 = 12;            //GPIO pin. Used to Charlieplexing on turtle HAT.
const byte in2 = 13;            //GPIO pin. Used to Charlieplexing on turtle HAT.
const byte in3 = 14;            //GPIO pin. Used to Charlieplexing on turtle HAT.
const byte in4 = 16;            //GPIO pin. Used to Charlieplexing on turtle HAT.

const byte mot1 = 1;            //Connected to the  2nd pin of the motor driver (SN754410). Left motor.
const byte mot2 = 3;            //Connected to the  7th pin of the motor driver (SN754410). Left motor.
const byte mot3 = 4;            //Connected to the 10th pin of the motor driver (SN754410). Right motor.
const byte mot4 = 5;            //Connected to the 15th pin of the motor driver (SN754410). Right motor.

const byte msg = 15;            //Connected to GND by a 10kOhm resistor. (It's needed by startup process.) This pin is connected to a LED and a buzzer on the turtle HAT. 
byte BEEPon = 4;                //Switch turtle HAT's beeps and stops. 4 = Normal mode: beeps and stops after executed every command. 3 = Flow mode: only beeps.
                                //2 = Quiet mode: only stops. 1 = Silent mode: no beeps, no stops. 0 = Silent mode + GPIO 15 switch the (UV) LED. (Instead of GPIO 2.)
bool LEDon = false;             //Switch the painting (UV) LED off/on.

byte pwmA = 39;                 //PWM duty % for motorA
byte pwmB = 34;                 //PWM duty % for motorB
byte pwmT = 45;                 //PWM duty % for motorA and motorB at turns
byte pwmCY = 20;                //PWM cycle length in ms
int pwmAB_lng = 45;             //command length for straight (forward and backward) moves in ms (multiplied by pwmCY)
int pwmT_lng = 24;              //command length for turns in ms (multiplied by pwmCY)
char pwmPRIM;                   //
char pwmSEC;                    //
int pwmON;                      //calculated microseconds for PWM cycles (straight)
int pwmGAP;                     //calculated microseconds for PWM cycles (straight)
int pwmOFF;                     //calculated microseconds for PWM cycles (straight)
int pwmONt;                     //calculated microseconds for PWM cycles (turns)
int pwmOFFt;                    //calculated microseconds for PWM cycles (turns)

byte cmd[1000];                 //command list
int ptr = 0;                    //pointer for command list's stack operations
int oldptr = 0;                 //if we accidentally reset the command list... it helps.
byte exe[1000];                 //executed command list position for undos
int ptre = 1;                   //pointer for exe[]'s stack operations
int oldptre = 0;                //if we accidentally reset the milestones list... it helps.

bool CHARLIEen = true;          //switch Charlieplexing on/off -> prevent duplicated input (during beeps, etc.)
byte input_btn = 0;             //make possible to distinguish short and long button press + prevent duplicated input, ghost effects...
byte input_lng = 0;             //make possible to distinguish short and long button press + prevent duplicated input, ghost effects...

byte LOOPon = 0;                //input modes for for-loop making with turtle HAT
byte LOOPcount = 0;             //loop count for for-loop making with turtle HAT
int LOOPstart = 0;              //milestone for for-loop execution on the fly
int LOOPremain = -1;            //iteration count  for for-loop execution on the fly

#define NOTE_C4  262
#define NOTE_CS4 277
#define NOTE_D4  294
#define NOTE_DS4 311
#define NOTE_E4  330
#define NOTE_F4  349
#define NOTE_FS4 370
#define NOTE_G4  392
#define NOTE_GS4 415
#define NOTE_A4  440
#define NOTE_AS4 466
#define NOTE_B4  494
#define NOTE_C5  523


void lAPs () {                                          //Read APs from the EEPROM and add to wifiMulti. Finally add the fallback AP too.
  if ((earray[origo[0]] == 17) || (earray[origo[0]] == 20)) {
    if ((sl == 0 ? 0 : --sl) > 0) {
      char essid[100] = ""; char epassword[100] = "";
      q = 0;
      for (int i = origo[0] + 1; true; i++) {           //Read the SSID from origo[0]
        if (i == origo[1]) break;                       //to origo[1]
        if (i > eeprom_ssid - 1) i = 0;                 //After max addr, continue from addr 0
        essid[q++] = char(earray[i]);
      }
      q = 0;
      for (int i = origo[1] + 1; true; i++) {           //Read the password from origo[1]
        if (i == origo[2]) break;                       //to origo[2]
        if (i > eeprom_ssid - 1) i = 0;                 //After max addr, continue from addr 0
        epassword[q++] = char(earray[i]);
      }
      REOR1();
      REOR2();
      if (APs.indexOf(essid) == -1) {
        //                                              Serial.println(); Serial.print("Adding "); Serial.println(essid);
        wifiMulti.addAP(essid, epassword);              //Add read AP to wifiMulti.
        APs.concat(essid);                              //Add AP to list to prevent redundant adding.
        APs.concat(" ");
        lAPs();                                         //Continue the recursion if the last found AP is added. If not (because of redundancy) only shift boundaries (origo[]).
      } else {
        sl++;                                           //If it don't add AP, keep the "slot kredit".
      }
    }
  }
}

void REOR1() {                                          //Find next origo[0], backward: eeprom_ssid -> 0
  for (int i = (origo[0] == 0 ? eeprom_ssid - 1 : origo[0] - 1); true; i--) {
    if (i < 0) i = eeprom_ssid - 1;
    if ((earray[i] == 17) || (earray[i] == 20)) {
      origo[0] = i;
      break;
    }
  }
}

void REOR2() {                                            //Find next origo[1] and origo[2], forward: 0 -> eeprom_ssid
  for (int i = origo[0]; true; i++) {                     //origo[1]
    if (i > eeprom_ssid - 1) i = 0;
    if (earray[i] == 18) {
      origo[1] = i;
      break;
    }
  }

  for (int i = origo[1]; true; i++) {                     //origo[2]
    if (i > eeprom_ssid - 1) i = 0;
    if (earray[i] == 19) {
      origo[2] = i;
      break;
    }
  }
}


void BEEP(byte note=0, byte dur=3, byte pause=0, byte rep=1) { //KI KÉNE DOLGOZNI A FLOW MODE DOLGAIT...... SŐT...... MINDENT....

  if (BEEPon > 1){
    for (byte i = 0; i < rep; i++){
    
      digitalWrite(msg, LOW);
      delay(100);
    
      if (BEEPon==4) {    

      int tgap;
      int beepCY;
      
      switch (note) {
        case 0:
          tgap = round(500000 / NOTE_C4);
          beepCY = round(NOTE_C4 / 10 * dur);
          break;
        case 1:
          tgap = round(500000 / NOTE_FS4);
          beepCY = round(NOTE_FS4 / 10 * dur);
          break;
        case 2:
          tgap = round(500000 / NOTE_C5);
          beepCY = round(NOTE_C5 / 10 * dur);
          break;
        }
        
        for (byte j = 0; j < beepCY; j++){
          digitalWrite(msg, HIGH);
          delayMicroseconds(tgap);
          digitalWrite(msg, LOW);
          delayMicroseconds(tgap);
        }
      
    } else {
      
      digitalWrite(msg, HIGH);
      delay(dur * 100);
      digitalWrite(msg, LOW);
      
    }   

       if (pause == 0) {
        delay(200);
        CHARLIEen = true;
      } else {
        delay((pause - 1) * 100);
      }
  }
  if (LOOPon) digitalWrite(msg, HIGH);
  }
}


void MOT_init() {
  if (pwmA < pwmB) {
    pwmPRIM = 'B';
    pwmSEC = 'A';
    pwmON = round(pwmCY * pwmA / 100);
    pwmGAP = round(pwmCY * (pwmB-pwmA) / 100);
    pwmOFF = round(pwmCY * (100-pwmB) / 100);  
  } else {
    pwmPRIM = 'A';
    pwmSEC = 'B';
    pwmON = round(pwmCY * pwmB / 100);
    pwmGAP = round(pwmCY * (pwmA-pwmB) / 100);
    pwmOFF = round(pwmCY * (100-pwmA) / 100);  
  } 
  pwmONt = round(pwmCY * pwmT / 100);
  pwmOFFt = round(pwmCY * (100-pwmT) / 100);  
}


void MOT(char motor='U', byte motormode=0) {

  switch (motor) {
    case 'A':
      switch (motormode) {
      case 0:
        digitalWrite(mot1, LOW);
        digitalWrite(mot2, LOW);
        break;
      case 1:
        digitalWrite(mot1, HIGH);
        digitalWrite(mot2, LOW);
        break;
      case 2:
        digitalWrite(mot1, LOW);
        digitalWrite(mot2, HIGH);
        break;
      default:
        digitalWrite(mot1, LOW);
        digitalWrite(mot2, LOW);
        digitalWrite(mot3, LOW);
        digitalWrite(mot4, LOW);
        break;
      }
    break;

    case 'B':
      switch (motormode) {
      case 0:
        digitalWrite(mot3, LOW);
        digitalWrite(mot4, LOW);
        break;
      case 1:
        digitalWrite(mot3, HIGH);
        digitalWrite(mot4, LOW);
        break;
      case 2:
        digitalWrite(mot3, LOW);
        digitalWrite(mot4, HIGH);
        break;
      default:
        digitalWrite(mot1, LOW);
        digitalWrite(mot2, LOW);
        digitalWrite(mot3, LOW);
        digitalWrite(mot4, LOW);
        break;
      }   
    break;
    
    case 'U':
      switch (motormode) {
      case 0:
        digitalWrite(mot1, LOW);
        digitalWrite(mot2, LOW);
        digitalWrite(mot3, LOW);
        digitalWrite(mot4, LOW);
        break;
      case 1:
        digitalWrite(mot1, HIGH);
        digitalWrite(mot2, LOW);
        digitalWrite(mot3, HIGH);
        digitalWrite(mot4, LOW);
        break;
      case 2:
        digitalWrite(mot1, LOW);
        digitalWrite(mot2, HIGH);
        digitalWrite(mot3, LOW);
        digitalWrite(mot4, HIGH);
        break;
      default:
        digitalWrite(mot1, LOW);
        digitalWrite(mot2, LOW);
        digitalWrite(mot3, LOW);
        digitalWrite(mot4, LOW);
        break;
      }   
    break;

    default:
      digitalWrite(mot1, LOW);
      digitalWrite(mot2, LOW);
      digitalWrite(mot3, LOW);
      digitalWrite(mot4, LOW);
      break;
  }
}


void CMD(byte modeA=0, byte modeB=0) {
  byte modePRIM;
  byte modeSEC;

  if (pwmPRIM == 'A') {
    modePRIM = modeA;
    modeSEC = modeB;
  } else {
    modePRIM = modeB;
    modeSEC = modeA;
  }
    
  if (modePRIM == modeSEC) {
    for (int i = 0; i < pwmAB_lng; i++) {
      MOT(pwmPRIM, modePRIM);
      MOT(pwmSEC, modeSEC);
      delay(pwmON);
      MOT(pwmSEC, 0);
      delay(pwmGAP);
      MOT();
      delay(pwmOFF);
    }
  } else {
    for (int i = 0; i < pwmT_lng; i++) {
      MOT(pwmPRIM, modePRIM);
      MOT(pwmSEC, modeSEC);
      delay(pwmONt);
      MOT();
      delay(pwmOFFt);
    }
  }
}


void PRESS(byte btn) {
  if (input_btn == btn){
    input_lng++;  
  } else {
    input_btn = btn;
    input_lng = 1;
  }  
}


void CHARLIE(){
  pinMode(in1, OUTPUT);
  pinMode(in2, INPUT_PULLUP);
  pinMode(in3, INPUT_PULLUP);
  digitalWrite(in1, LOW);  
  digitalWrite(in4, HIGH);
  delay(1);
  
  if (digitalRead(in2)==0){                                     //LEFT BUTTON
    PRESS(2);
  } else if (digitalRead(in3)==0){                              //FORWARD BUTTON
    PRESS(1);
  }

  pinMode(in1, INPUT_PULLUP);
  pinMode(in2, OUTPUT);
  pinMode(in3, INPUT_PULLUP);
  digitalWrite(in2, LOW);  
  digitalWrite(in4, HIGH);
  delay(1);
  
  if (digitalRead(in1)==0){                                     //BACKWARD BUTTON
    PRESS(4);
  } else if (digitalRead(in3)==0){                              //RIGHT BUTTON
    PRESS(3);
  }

  pinMode(in1, INPUT_PULLUP);
  pinMode(in2, INPUT_PULLUP);
  pinMode(in3, OUTPUT);
  digitalWrite(in3, LOW);  
  digitalWrite(in4, HIGH);
  delay(1);
  
  if (digitalRead(in1)==0){                                     //REPEAT BUTTON
    PRESS(6);
  } else if (digitalRead(in2)==0){                              //START BUTTON
    PRESS(5);
  }

  pinMode(in1, INPUT_PULLUP);
  pinMode(in2, INPUT_PULLUP);
  pinMode(in3, INPUT_PULLUP);
  digitalWrite(in4, LOW);
  delay(1);
  
  if (digitalRead(in1)==0){                                     //PAUSE BUTTON
    PRESS(9);
  } else if (digitalRead(in2)==0){                              //CLEAR BUTTON
    PRESS(8);
  } else if (digitalRead(in3)==0){                              //UNDO BUTTON
    PRESS(7);
  }
}


void LCOUNT(char sign, byte num=1) {
  if (sign == '+') {
    if ((LOOPcount + num) > 255) {
      LOOPcount = 255;
      BEEP(2,1); 
      BEEP(0,4,2,3);
    } else {
      LOOPcount += num;
      BEEP(2,1); 
    } 
  } else if (sign == '-') {
    if ((LOOPcount - num) < 1){
      LOOPcount = 1;
      BEEP(2,1); 
      BEEP(0,4,2,3);
    } else {
      LOOPcount -= num;   
      BEEP(2,1); 
    }
  } else if (sign == 'X') {
    LOOPcount = 1;
    BEEP(2,1); 
    BEEP(2,1,1,3);
    BEEP(1,1);   
  } else if (sign == 'B') {
    byte LOOPbeep = LOOPcount;
    BEEP(2,1);
    delay(300);
    BEEP(2,3,1); 
    BEEP(1,3,1); 
    BEEP(0,3,1); 
    delay(1000);
    
    do {
      if (LOOPbeep > 99) {
        BEEP(2,3,7);
        LOOPbeep -= 100;
      } else if (LOOPbeep > 9) {
        BEEP(1,3,7);
        LOOPbeep -= 10;
      } else {
        BEEP(0,3,7);
        LOOPbeep--;
      }
    } while (LOOPbeep > 0);
    

  }
}



void setup() {
                                                                                    //Serial.begin(115200);
                                                                                    //Serial.setDebugOutput(true);
  EEPROM.begin(eeprom_ssid);

  pinMode(mot1, OUTPUT);
  pinMode(mot2, OUTPUT);
  pinMode(mot3, OUTPUT);
  pinMode(mot4, OUTPUT);

  pinMode(in1, INPUT);                                                               //For Charlieplexing.
  pinMode(in2, INPUT);                                                               //For Charlieplexing.
  pinMode(in3, INPUT);                                                               //For Charlieplexing.
  pinMode(in4, OUTPUT);                                                              //For Charlieplexing.

  pinMode(msg, OUTPUT);                                                              //For LED and buzzer. GPIO 15.
  pinMode(2, OUTPUT);
  
  MOT_init();                                                                        //Motor PWM settings initialization.
  MOT();                                                                             //Set motor A and B -> OFF.
  exe[0] = 0;                                                                        //set the first milestone at 0, to 0 

  for (int i = 0; i < eeprom_ssid; i++) earray[i] = EEPROM.read(i);                  //Read and "copy" EEPROM.
  wifiMulti.addAP(ssid, password);                                                   //Add fallback AP to wifiMulti.

  for (int i = 0; i < eeprom_ssid; i++) if (earray[i] == 20) {
      origo[0] = i;                                                                  //Search the last AP record, its boundaries.
      REOR2();
      break;
    }   
  digitalWrite(2,LOW);
}

void loop() {

  if (CHARLIEen) CHARLIE();
  
  if (input_lng > 4) {
    CHARLIEen = false;
    switch (input_btn) {
      case 1:                                                     //FORWARD
        if (LOOPon == 2){
          LCOUNT('+',1); 
        } else {
          cmd[ptr++] = 1;
          BEEP(); 
        }
        break;
        
      case 2:                                                     //LEFT
        if (LOOPon == 2){
          LCOUNT('-',10);
        } else {
          cmd[ptr++] = 2;
          BEEP();
        } 
        break;
        
      case 3:                                                     //RIGHT
        if (LOOPon == 2){
          LCOUNT('+',10);
        } else {
          cmd[ptr++] = 3;
          BEEP(); 
        }
        break;
        
      case 4:                                                     //BACKWARD
        if (LOOPon == 2){
          LCOUNT('-',1);
        } else {
          cmd[ptr++] = 4;
          BEEP(); 
        }
        break;
            
      case 5:                                                     //START
        if (LOOPon == 2){
          LCOUNT('B');
        } else {
          BEEP(); 
          if (ptr != exe[ptre-1]) exe[ptre++] = ptr;              //Save the execuion as milestone in exe[]. + avoid duplicate entries.
          delay(1000);
          for (int j=0; j < ptr; j++){
            if (cmd[j] == 6) {
              LOOPstart = j;                                      //Only j, not j+1. After it jumps back, the loop makes an increment.
            } else if (cmd[j] == 7){
              if (LOOPremain == -1) LOOPremain = cmd[j+1];
              if (--LOOPremain > 0) {
                j = LOOPstart;                                    //Jumps back...
              } else {
                j++;                                              //Only ++, not += 2! (The loop makes the secound increment.)
                LOOPremain = -1;
              } 
            } else {
              switch (cmd[j]) {
                case 1:
                  CMD(1,1);
                  break;
        
                case 2:
                  CMD(2,1);
                  break;
        
                case 3:
                  CMD(1,2);
                  break;
              
                case 4:
                  CMD(2,2);
                  break;
        
                case 9:
                  //MOT();
                  //delay(pwmCY * pwmAB_lng);
                    if (LEDon){
                      digitalWrite(2,LOW);
                      LEDon = false;                      
                    } else {
                      digitalWrite(2,HIGH);
                      LEDon = true;
                    }   
                default:
                  MOT();
                  break;
              }
              BEEP(2,2,7);
            }
          }
          BEEP(1,3,1,2);
        }
        break;
          
      case 6:                                                     //REPEAT
        if (LOOPon == 0){
          cmd[ptr++] = 6;                                         //save the REPEAT action in command list and increase the pointer
          LOOPon = 1;
        } else if (LOOPon == 1) {  
          cmd[ptr++] = 7;
          LOOPon = 2;
        } else {
          cmd[ptr++] = LOOPcount;
          LOOPcount = 0;
          LOOPon = 0;
          BEEP(0,1,1,2);
        }
        BEEP(); 
        break;

      case 7:                                                     //UNDO
        if (LOOPon == 2){
          LCOUNT('X');
        } else { 
          BEEP();  
          if (ptr == 0){                                          //If the pointer is 0, it undoes the assumed clear. If didn't a clear changed the pointer to 0 (at startup), it doesn't change anything.
            ptr = oldptr;
            ptre = oldptre;
          } else if (ptr == exe[ptre-1]){                         //If the pointer is same with the last milestone (=there aren't any new command after last execution), it undoes to the previous (last-1) milestone.
            ptr = exe[--ptre-1];
          } else {                                                //If there are new commands after last execution (=the pointer isn't same with last milestone), it undoes to the last milestone.
            ptr = exe[ptre-1];
          }
        
          BEEP(0,1,1);
          BEEP(1,1,1);
          BEEP(2,1,1);
        
          if (ptr == 0) {
            delay(500);
            ptr = 0;                                              //Reset the pointer.      -> (Pseudo)clear the whole command list.
            ptre = 1;                                             //Reset the pointer.      -> (Pseudo)clear the whole milestone list.
            oldptr = 0;                                           //Avoid undoing the undo. -> (Pseudo)clear the whole command list "permanently".
            oldptre = 0;                                          //Avoid undoing the undo. -> (Pseudo)clear the milestone list "permanently" .
            exe[0] = 0;                                           //Set the first milestone at 0, to 0
            BEEP(2,1,1,3);
            BEEP(1,1);
          }
        }
        break;

      case 8:                                                     //CLEAR
        if (LOOPon == 2){
          LCOUNT('X');  
        } else {  
          BEEP();           
          oldptr = ptr;                                           //Save the command list's pointer for undo.
          oldptre = ptre;                                         //Save the milestone list's pointer for undo.
          ptr = 0;                                                //Reset the pointer. -> (pseudo)clear the whole command list.
          ptre = 1;                                               //Reset the pointer. -> (pseudo)clear the whole milestone list.
          exe[0] = 0;                                             //Set the first milestone at 0, to 0.
          BEEP(2,1,1,3);
          BEEP(1,1);
        }
        break;

      case 9:                                                     //PAUSE
        if (LOOPon == 2){
          LCOUNT('B');
        } else { 
          cmd[ptr++] = 9;
          BEEP();
        } 
        break;    
      }
  input_btn = 0;
  input_lng = 0;
  }

  
  if (millis() >= pM + interval) {
    pM = millis();
    lAPs();                                                       //Add APs from EEPROM.
    //                                                            Serial.println("Connecting Wifi...");
    if (wifiMulti.run() != WL_CONNECTED) return;                  //If connection lost, return.
    //                                                            Serial.println(); Serial.println("WiFi connected."); Serial.println("IP address: "); Serial.println(WiFi.localIP());
    conn = client_sec.connect(host, port);
    //                                                            Serial.print("Connecting to "); Serial.println(host);
    if (!conn) {
      //                                                          Serial.println("Connection failed.");
      return;
    }
    if (client_sec.verify(fingerprint, host)) {
      //                                                          Serial.println("Certificate matches.");
    } else {
      //                                                          Serial.println("Certificate doesn't match.");
    }
    //                                                            Serial.print("Requesting URL: "); Serial.println(URL+WiFi.SSID());
    client_sec.print(String("GET ") + URL + WiFi.SSID() + " HTTP/1.1\r\n" +
                     "Host: " + host + "\r\n" +
                     "User-Agent: BuildFailureDetectorESP8266\r\n" +
                     "Connection: close\r\n\r\n");
    URL = URL1;                                                   //Set the GET URL to select.
    //                                                            Serial.println("Request sent."); Serial.println(); Serial.println("Reply was:"); Serial.println("==========");
    while (client_sec.connected()) {
      line = client_sec.readStringUntil('\r');

      if (line.indexOf("Date:") != -1) {                          //Set uBot's clock to server's clock.
        gmt_poz = line.indexOf("GMT");
        setTime(line.substring(gmt_poz - 9, gmt_poz - 7).toInt() + TZ, line.substring(gmt_poz - 6, gmt_poz - 4).toInt(), line.substring(gmt_poz - 3, gmt_poz - 1).toInt(), 01, 01, 2018);
      }

      if ((line.indexOf(char(17)) != -1) && (line.indexOf(char(18)) != -1) && (line.indexOf(char(19)) != -1)) { //Does the line contain AP record?
        origo[0] = line.indexOf(char(17));
        origo[1] = line.indexOf(char(18));
        origo[2] = line.indexOf(char(19));
        issid = line.substring(origo[0] + 1, origo[1]);
        ipassword = line.substring(origo[1] + 1, origo[2]);

        origo[0] = eeprom_ssid;
        for (int i = 0; i < eeprom_ssid; i++) {                       //~REOR1(); Find any AP in EEPROM's copy. If there is char(20), ...
          if (earray[i] == 20) {
            origo[0] = i;
            break;
          }
        }

        if (origo[0] == eeprom_ssid) {                                 //Is there any AP?
          origo[0] = 0;                                                //No. This will be the first.
          EEPROM.write(0, 20);
        } else {
          REOR2();                                                     //Yes. Find the remaining boundaries.
          EEPROM.write(origo[0], 17);                                  //Outdate the last AP (20 -> 17).
          origo[2] > eeprom_ssid - 2 ? origo[0] = 0 : origo[0] = origo[2] + 1; //Step one after the outdated AP record.
          EEPROM.write(origo[0], 20);                                  //Start new record.
        }
        origo[1] = origo[0];
        for (byte i = 0; i < issid.length(); i++) {                    //Write SSID in EEPROM. The loop's variable is for SSID[i]
          origo[1] > eeprom_ssid - 2 ? origo[1] = 0 : origo[1]++;      //and the origo[1] for position.
          EEPROM.write(origo[1], issid[i]);
        }
        origo[1] > eeprom_ssid - 2 ? origo[1] = 0 : origo[1]++;
        EEPROM.write(origo[1], 18);
        origo[2] = origo[1];
        for (byte i = 0; i < ipassword.length(); i++) {                //Write PWD in EEPROM. The loop's variable is for PWD[i]
          origo[2] > eeprom_ssid - 2 ? origo[2] = 0 : origo[2]++;      //and the origo[2] for position.
          EEPROM.write(origo[2], ipassword[i]);
        }
        origo[2] > eeprom_ssid - 2 ? origo[2] = 0 : origo[2]++;
        EEPROM.write(origo[2], 19);
        EEPROM.commit();
        URL = URL0;                                                     //Set the GET URL to pseudodelete.
        for (int i = 0; i < eeprom_ssid; i++)  earray[i] = EEPROM.read(i); //Refresh.
      }
      //                                                                Serial.print(line);
    }
    //                                                                  Serial.println("=========="); Serial.println("Closing connection."); Serial.println(); Serial.println();
    client_sec.stop();
    return;
  }





  if (wifiMulti.run() == WL_CONNECTED) {
    if (!s_on) {
      server.begin();
      s_on = true;
    }
  } else {
    s_on = false;
    return;
  }

  client = server.available();
  if (!client) return;

  while (!client.available()) {
    if (WiFi.status() != WL_CONNECTED) {
      while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        //Serial.print(".");
      }
    }
  }

  request = client.readStringUntil('\r');
  //Serial.println(request);
  client.flush();
  MOT();

  if (request.indexOf("/OFF") != -1)   MOT();
  if (request.indexOf("/FORW") != -1)  CMD(1,1);
  if (request.indexOf("/BACKW") != -1) CMD(2,2);
  if (request.indexOf("/LFT") != -1)   CMD(2,1);   
  if (request.indexOf("/RGT") != -1)   CMD(1,2);


  if (request.indexOf("/PWMA-01") != -1)  pwmA--;
  if (request.indexOf("/PWMA+01") != -1)  pwmA++;
  if (request.indexOf("/PWMB-01") != -1)  pwmB--;
  if (request.indexOf("/PWMB+01") != -1)  pwmB++;
  if (request.indexOf("/PWMT-01") != -1)  pwmT--;
  if (request.indexOf("/PWMT+01") != -1)  pwmT++;
  if (request.indexOf("/PWMCY-01") != -1) pwmCY--;
  if (request.indexOf("/PWMCY+01") != -1) pwmCY++;
  if (request.indexOf("/PWMA-05") != -1)  pwmA -= 5; 
  if (request.indexOf("/PWMA+05") != -1)  pwmA += 5;
  if (request.indexOf("/PWMB-05") != -1)  pwmB -= 5;
  if (request.indexOf("/PWMB+05") != -1)  pwmB += 5;
  if (request.indexOf("/PWMT-05") != -1)  pwmT -= 5;
  if (request.indexOf("/PWMT+05") != -1)  pwmT += 5;
  if (request.indexOf("/PWMCY-05") != -1) pwmCY -= 5;
  if (request.indexOf("/PWMCY+05") != -1) pwmCY += 5;
  if (request.indexOf("/PWMA-10") != -1)  pwmA -= 10;
  if (request.indexOf("/PWMA+10") != -1)  pwmA += 10;
  if (request.indexOf("/PWMB-10") != -1)  pwmB -= 10;
  if (request.indexOf("/PWMB+10") != -1)  pwmB += 10;
  if (request.indexOf("/PWMT-10") != -1)  pwmT -= 10;
  if (request.indexOf("/PWMT+10") != -1)  pwmT += 10;
  if (request.indexOf("/PWMCY-10") != -1) pwmCY -= 10;
  if (request.indexOf("/PWMCY+10") != -1) pwmCY += 10;
  MOT_init();
  
  if (request.indexOf("/LNGAB-01") != -1)  pwmAB_lng--;
  if (request.indexOf("/LNGAB+01") != -1)  pwmAB_lng++;
  if (request.indexOf("/LNGT-01") != -1)   pwmT_lng--;
  if (request.indexOf("/LNGT+01") != -1)   pwmT_lng++;

  if (request.indexOf("/LNGAB-05") != -1)  pwmAB_lng -= 5;
  if (request.indexOf("/LNGAB+05") != -1)  pwmAB_lng += 5;
  if (request.indexOf("/LNGT-05") != -1)   pwmT_lng  -= 5;
  if (request.indexOf("/LNGT+05") != -1)   pwmT_lng  += 5;
  
  if (request.indexOf("/LNGAB-10") != -1)  pwmAB_lng -= 10;
  if (request.indexOf("/LNGAB+10") != -1)  pwmAB_lng += 10;
  if (request.indexOf("/LNGT-10") != -1)   pwmT_lng  -= 10;
  if (request.indexOf("/LNGT+10") != -1)   pwmT_lng  += 10;


  if (request.indexOf("/TURTLE-F") != -1)  input_btn = 1;
  if (request.indexOf("/TURTLE-L") != -1)  input_btn = 2;
  if (request.indexOf("/TURTLE-R") != -1)  input_btn = 3;
  if (request.indexOf("/TURTLE-B") != -1)  input_btn = 4;
  if (request.indexOf("/TURTLE-G") != -1)  input_btn = 5;
  if (request.indexOf("/TURTLE-C") != -1)  input_btn = 6;
  if (request.indexOf("/TURTLE-U") != -1)  input_btn = 7;
  if (request.indexOf("/TURTLE-D") != -1)  input_btn = 8;
  if (request.indexOf("/TURTLE-P") != -1)  input_btn = 9;
  if (request.indexOf("/TURTLE") != -1)    input_lng = 5;

  if (request.indexOf("/BEEP0") != -1) BEEPon = 0;
  if (request.indexOf("/BEEP1") != -1) BEEPon = 1;
  if (request.indexOf("/BEEP2") != -1) BEEPon = 2;
  if (request.indexOf("/BEEP3") != -1) BEEPon = 3;
  if (request.indexOf("/BEEP4") != -1) BEEPon = 4;


  client.println("HTTP/1.1 200 OK");
  client.println("Content-Type: text/html");
  client.println("");                                                                       //Necessary...
  client.println("<!DOCTYPE HTML>");
  client.println("<html>");
  client.println("<table border='0'><tr><td width=300 height=300></td>");
  client.println("<td width=300 height=300><a href=\"/FORW\"><h1>FORW</h1></a></td><td width=300 height=300></td></tr><tr>");
  client.println("<td width=300 height=300><a href=\"/LFT\"><h1>LFT</h1></a></td>");
  client.println("<td width=300 height=300><a href=\"/OFF\"><h1>OFF</h1></a></td>");
  client.println("<td width=300 height=300><a href=\"/RGT\"><h1>RGT</h1></a></td></tr><tr>");
  client.println("<td width=300 height=300></td>");
  client.println("<td width=300 height=300><a href=\"/BACKW\"><h1>BACKW</h1></a></td>");
  client.println("<td width=300 height=300></td></tr></table>");
  client.println("<br /><br />");


  client.println("<table border='0'><tr><td width=300 height=300></td>");
  client.println("<td width=300 height=300><a href=\"/TURTLE-F\"><h1>FORW</h1></a></td><td width=300 height=300></td></tr><tr>");
  client.println("<td width=300 height=300><a href=\"/TURTLE-L\"><h1>LFT</h1></a></td>");
  client.println("<td width=300 height=300><a href=\"/TURTLE-G\"><h1>GO</h1></a></td>");
  client.println("<td width=300 height=300><a href=\"/TURTLE-R\"><h1>RGT</h1></a></td></tr><tr>");
  client.println("<td width=300 height=300><a href=\"/TURTLE-U\"><h1>U</h1></a></td>");
  client.println("<td width=300 height=300><a href=\"/TURTLE-B\"><h1>BACKW</h1></a></td>");
  client.println("<td width=300 height=300><a href=\"/TURTLE-D\"><h1>X</h1></a></td>");
  client.println("</tr></table>");
  client.println("<br /><br />");

  client.println("<br/><br/>########<br/><br/><br/><br/>");
  for (int i = 0; i < 512; i++) {
    if (EEPROM.read(i) != 0) {
      if (EEPROM.read(i) < 32) {
        client.println("<br/>");
        client.println(EEPROM.read(i));
      } else if (EEPROM.read(i) > 32) {
        client.print(char(EEPROM.read(i)));
      }
    }
  }
  client.println("<br/><br/>########<br/><br/><br/><br/>");
  for(int i = 0; i < ptr; i++) client.println(cmd[i]);
  client.println("<br/><br/>########<br/><br/><br/><br/>");
  for(int i = 0; i < ptre; i++) client.println(exe[i]);
  client.println("<br/><br/>########<br/><br/><br/><br/>");

  client.println("<table border='0'>");
  client.println("<tr><td><a href=\"/PWMA-10\"><h1>A-10</h1></a></td>");
  client.println("<td><a href=\"/PWMA-05\"><h1>A-5</h1></a></td>");
  client.println("<td><a href=\"/PWMA-01\"><h1>A-1</h1></a></td>");
  client.println("<td>");
  client.println(pwmA);
  client.println("</td>");
  client.println("<td><a href=\"/PWMA+01\"><h1>A+1</h1></a></td>");
  client.println("<td><a href=\"/PWMA+05\"><h1>A+5</h1></a></td>");
  client.println("<td><a href=\"/PWMA+10\"><h1>A+10</h1></a></td></tr>");

  client.println("<tr><td><a href=\"/PWMB-10\"><h1>B-10</h1></a></td>");
  client.println("<td><a href=\"/PWMB-05\"><h1>B-5</h1></a></td>");
  client.println("<td><a href=\"/PWMB-01\"><h1>B-1</h1></a></td>");
  client.println("<td>");
  client.println(pwmB);
  client.println("</td>");
  client.println("<td><a href=\"/PWMB+01\"><h1>B+1</h1></a></td>");
  client.println("<td><a href=\"/PWMB+05\"><h1>B+5</h1></a></td>");
  client.println("<td><a href=\"/PWMB+10\"><h1>B+10</h1></a></td></tr>");

  client.println("<tr><td><a href=\"/PWMT-10\"><h1>T-10</h1></a></td>");
  client.println("<td><a href=\"/PWMT-05\"><h1>T-5</h1></a></td>");
  client.println("<td><a href=\"/PWMT-01\"><h1>T-1</h1></a></td>");
  client.println("<td>");
  client.println(pwmT);
  client.println("</td>");
  client.println("<td><a href=\"/PWMT+01\"><h1>T+1</h1></a></td>");
  client.println("<td><a href=\"/PWMT+05\"><h1>T+5</h1></a></td>");
  client.println("<td><a href=\"/PWMT+10\"><h1>T+10</h1></a></td></tr>");

  client.println("<tr><td><a href=\"/PWMCY-10\"><h1>CY-10</h1></a></td>");
  client.println("<td><a href=\"/PWMCY-05\"><h1>CY-5</h1></a></td>");
  client.println("<td><a href=\"/PWMCY-01\"><h1>CY-1</h1></a></td>");
  client.println("<td>");
  client.println(pwmCY);
  client.println("</td>");
  client.println("<td><a href=\"/PWMCY+01\"><h1>CY+1</h1></a></td>");
  client.println("<td><a href=\"/PWMCY+05\"><h1>CY+5</h1></a></td>");
  client.println("<td><a href=\"/PWMCY+10\"><h1>CY+10</h1></a></td></tr>");

  client.println("<tr><td><a href=\"/LNGAB-10\"><h1>AB-10</h1></a></td>");
  client.println("<td><a href=\"/LNGAB-05\"><h1>AB-5</h1></a></td>");
  client.println("<td><a href=\"/LNGAB-01\"><h1>AB-1</h1></a></td>");
  client.println("<td>");
  client.println(pwmAB_lng);
  client.println("</td>");
  client.println("<td><a href=\"/LNGAB+01\"><h1>AB+1</h1></a></td>");  
  client.println("<td><a href=\"/LNGAB+05\"><h1>AB+5</h1></a></td>");
  client.println("<td><a href=\"/LNGAB+10\"><h1>AB+10</h1></a></td></tr>");


  client.println("<tr><td><a href=\"/LNGT-10\"><h1>T-10</h1></a></td>");
  client.println("<td><a href=\"/LNGT-05\"><h1>T-5</h1></a></td>");
  client.println("<td><a href=\"/LNGT-01\"><h1>T-1</h1></a></td>");
  client.println("<td>");
  client.println(pwmT_lng);
  client.println("</td>");
  client.println("<td><a href=\"/LNGT+01\"><h1>T+1</h1></a></td>");
  client.println("<td><a href=\"/LNGT+05\"><h1>T+5</h1></a></td>");
  client.println("<td><a href=\"/LNGT+10\"><h1>T+10</h1></a></td></tr>");
  client.println("</table>");
  client.println("<br /><br />");
  client.println(LOOPcount);
  client.println("<br /><br />");
  
  if (BEEPon!=4) {
    client.println("<a href=\"/BEEP4\"><h1>Hang: BE /// Szakaszok: BE /// UV LED: GPIO2</h1></a>");
  } else {
    client.println("<h1>Hang: BE /// Szakaszok: BE /// UV LED: GPIO2</h1>");
  }
  
  if (BEEPon!=3) {
    client.println("<a href=\"/BEEP3\"><h1>Hang: KI /// Szakaszok: BE /// UV LED: GPIO2</h1></a>");
  } else {
    client.println("<h1>Hang: KI /// Szakaszok: BE /// UV LED: GPIO2</h1>");
  }

  if (BEEPon!=2) {
    client.println("<a href=\"/BEEP2\"><h1>Hang: BE /// Szakaszok: KI /// UV LED: GPIO2</h1></a>");
  } else {
    client.println("<h1>Hang: BE /// Szakaszok: KI /// UV LED: GPIO2</h1>");
  }

  if (BEEPon!=1) {
    client.println("<a href=\"/BEEP1\"><h1>Hang: KI /// Szakaszok: KI /// UV LED: GPIO2</h1></a>");
  } else {
    client.println("<h1>Hang: KI /// Szakaszok: KI /// UV LED: GPIO2</h1>");
  }
  
  if (BEEPon!=0) {
    client.println("<a href=\"/BEEP0\"><h1>Hang: KI /// Szakaszok: KI /// UV LED: GPIO15</h1></a>");
  } else {
    client.println("<h1>Hang: KI /// Szakaszok: KI /// UV LED: GPIO15</h1>");
  }

  client.println("<br /><br />");

  
  client.println("</html>");
  //Serial.println("Client disonnected");
  //Serial.println("");

}
