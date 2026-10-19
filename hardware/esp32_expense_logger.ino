// OPTIONAL IoT extension: log quick expenses with push buttons on an ESP32.
// Wiring: one leg of each button to its GPIO, other leg to GND. No resistor needed,
// because INPUT_PULLUP uses the ESP32's internal pull-up (pressed = LOW).
// Read the Serial output and paste the lines into data/user_expenses.csv, or extend
// with a Python serial reader (pyserial) that appends rows automatically.

const int FOOD_BTN = 4;     // logs Rs 100 Food
const int TRAVEL_BTN = 5;   // logs Rs 150 Transport
const int RESET_BTN = 18;   // resets session counters

int foodCount = 0, travelCount = 0;

void setup() {
  Serial.begin(115200);
  pinMode(FOOD_BTN, INPUT_PULLUP);
  pinMode(TRAVEL_BTN, INPUT_PULLUP);
  pinMode(RESET_BTN, INPUT_PULLUP);
  Serial.println("Date,Category,Description,Amount,Type,Payment_Method");
}

void loop() {
  if (digitalRead(FOOD_BTN) == LOW) {
    foodCount++;
    Serial.println("today,Food,Button log,100,Expense,Cash");
    delay(300);                       // simple debounce
  }
  if (digitalRead(TRAVEL_BTN) == LOW) {
    travelCount++;
    Serial.println("today,Transport,Button log,150,Expense,Cash");
    delay(300);
  }
  if (digitalRead(RESET_BTN) == LOW) {
    foodCount = 0; travelCount = 0;
    Serial.println("# session reset");
    delay(500);
  }
}
