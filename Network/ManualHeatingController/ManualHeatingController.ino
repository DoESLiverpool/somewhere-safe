// Manual replacement for the YaHMS controller used on the
// heating in DoES Liverpool
//
// Use it when the network is down and the existing controller
// can't receive its instructions
//
// Circuit:
// Needs a pushbutton connected to 5V on one side and kSwitchPin
// on the other, with kSwitchPin also connected to ground through
// a pull-down resistor
// And an LED connected to pin kIndicatorPin will illuminate
// whenever the heating is on
//
// Usage:
// Heating is turned on when the LED is lit
// Pressing the pushbutton will toggle the heating between
// on and off

const int kHeatingPin = 14;
const int kSwitchPin = 2;
const int kIndicatorPin = 13;
const int kDebounceDelay = 500;

int gLastButtonState = LOW;
unsigned long gLastSwitchTime = 0UL;
bool gHeatingState = false;

void setup() {
  // put your setup code here, to run once:
  pinMode(kHeatingPin, OUTPUT);
  pinMode(kSwitchPin, INPUT);
  pinMode(kIndicatorPin, OUTPUT);

  digitalWrite(kIndicatorPin, HIGH);
  delay(300);
  digitalWrite(kIndicatorPin, LOW);  
}

void loop() {
  // put your main code here, to run repeatedly:
  int buttonState = digitalRead(kSwitchPin);
//Serial.print("buttonState: ");
//Serial.println(buttonState);
  if (buttonState != gLastButtonState) {
    //Serial.println("Setting gLastSwitchTime");
    gLastSwitchTime = millis();
    gLastButtonState = buttonState;
  }

  if ((millis() - gLastSwitchTime) > kDebounceDelay) {
    // We've got a button press
//Serial.println("Switching...");

    if (buttonState == HIGH) {
      // It's a press
//Serial.print("Changing heating state to ");
      gHeatingState = !gHeatingState;
//Serial.println(gHeatingState);
    }
  }

  digitalWrite(kHeatingPin, gHeatingState);
  digitalWrite(kIndicatorPin, gHeatingState);

  delay(10);
}
