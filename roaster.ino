#define FAN_CTRL_PIN 4
#define FAN_RPM_PIN 2
#define CMD_SIZE 10

#define THERMO_BT_DO 52
#define THERMO_BT_CS 48
#define THERMO_BT_CLK 50

#define THERMO_ET_DO 49
#define THERMO_ET_CS 51
#define THERMO_ET_CLK 53

#define MOTOR_PIN1 22
#define MOTOR_PIN2 24
#define MOTOR_PIN3 26
#define MOTOR_PIN4 28

#include <max6675.h>

#include <AccelStepper.h>

volatile byte half_revs;
unsigned int current_rpm;
unsigned long timer;
char buff[CMD_SIZE];

struct inCmd {
    char *cmd;
    unsigned int val;
} cmd;

MAX6675 thermocouple_bt(THERMO_BT_CLK, THERMO_BT_CS, THERMO_BT_DO);
MAX6675 thermocouple_et(THERMO_ET_CLK, THERMO_ET_CS, THERMO_ET_DO);

AccelStepper stoveStepper(AccelStepper::BYJ, MOTOR_PIN1, MOTOR_PIN2, MOTOR_PIN3, MOTOR_PIN4);

void setup() {
    Serial.begin(9600);
    stoveStepper.setMaxSpeed(1000);
    stoveStepper.setAcceleration(800);
}

unsigned int i = 0;
void loop() {
    while (Serial.available()) {
        //read a line ending with \n and store in buff
        char ch = Serial.read();
        buff[i] = ch;
        if (ch == '\n' || i >= CMD_SIZE) {
            parseCommand();
            runCommand();
            i = 0;
            break;
        }
        ++i;
    }
    stoveStepper.run();
}

void moveStoveMotor(int position) {
    stoveStepper.move(position);
}

void moveStoveMotorTo(int position) {
    stoveStepper.moveTo(position);
}

long getStoveMotorPosition() {
    return stoveStepper.currentPosition();
}

void setStoveCurrentAsZero() {
    stoveStepper.setCurrentPosition(0);
}

void parseCommand() {
    //parse command in format COMMAND:VALUE
    //and store cmd/val in cmd struct
    char *valpos;
    for (int i = 0; i < CMD_SIZE; ++i) {
        if (buff[i] == ':') {
            valpos = &buff[i + 1];
            buff[i] = '\0';
        } else if (buff[i] == '\n') {
            buff[i] = '\0';
            break;
        }
    }
    cmd.cmd = buff;
    cmd.val = atoi(valpos);
}

void runCommand() {
    if (strncmp("FAN", cmd.cmd, CMD_SIZE) == 0) {
        analogWrite(FAN_CTRL_PIN, cmd.val);
    } else if (strncmp("TMP", cmd.cmd, CMD_SIZE) == 0) {
        Serial.print(thermocouple_et.readCelsius());
        Serial.print(",");
        Serial.println(thermocouple_bt.readCelsius());
    } else if (strncmp("KPA", cmd.cmd, CMD_SIZE) == 0) {
        moveStoveMotorTo(cmd.val);
    } else if (strncmp("MTR", cmd.cmd, CMD_SIZE) == 0) {
        moveStoveMotor(cmd.val);
    } else if (strncmp("KPQ", cmd.cmd, CMD_SIZE) == 0) {
        Serial.println(getStoveMotorPosition());
    } else if (strncmp("MZR", cmd.cmd, CMD_SIZE) == 0) {
        setStoveCurrentAsZero();
    } else {
        //Serial.print("Got unknown command!");
    }
}
