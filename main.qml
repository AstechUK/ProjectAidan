// Parts Washer Project "AIDAN" by ASTech.
//
// The Aim of the software is to power a nema17 motor in the machanical operations
// of a watchworks parts washer and dryer. its designed to be a user friendly simple to use yet
// smart in capabilty. here is a more technical overview.

// the soft ware runs on a raspberry pi zero and utilises a rpi 3.5 screen connected as a hat.

// there will be 1 momentary switch will for powering on and off the pi connected to ground and gpio6
// the power button will require the button to be held for 2 seconds to work either way.

// the nema 17 is driven by a bigtree tech tmc 2208 v3.0, it operaters at 1/16
// pins are as follows for stepper, en > gpio13, dir > gpio 19 and step > gpio 26.

// the nema17 and runs at 1.8 degrees per step an capable of half steps. its 200 steps per revolution.
//
//"low" 500 rpm, "mid" 1000rpm and "high" 1500rpm.
//there should always be a 1 second acceleration and deacceleration.

// the motor spins in different patterns and speeds depandent
// on the states of different buttons.

// the timer applies to all modes when applied via the buttontimemode "timed" applies countdown
//"Constant" is continous run.

// here is an example of motor cycle modes.

// "fwd(forward) and "rwd"(reverse) refers to direction and will spin in the direction selected only with
// the speed being determined by "low", "mid" and "high". while in "fwd", "rwd" and "mix"
// while in "pulse" the the motor will will spin at selected speed for 30 seconds
// then change to the next speed down for 15 sends and repeat, if "low" is selected on start then
// sequence will start at "mid" speed. the only 2 pairs to sequnce list ("high"/"mid") and ("mid"/"low")
// while in "mix" the motor will spin in mid for 30 seconds deaccelerate to 0 the spin in
// reverse for 5 second then deaccelerate 0 the spin forward again for 30  then reverse and so on.

// buttonheater states toggle a signal for relay to switch on a element.

import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

ApplicationWindow {
    id: mainWindow
    visible: true
    width: 480
    height: 320
    color: "dark grey"


 // Timer For Countdown

    Timer {
        id: countdownTimer
        interval: 1000 // One second
        repeat: true
        running: false // Should start only after time is set
        onTriggered: {
            if (mainScreen.cumulativeTime > 0) {
                mainScreen.cumulativeTime--;
                mainScreen.updateUI(); // Update every second
            } else {
                buttonStartStop.state = "idle"; // Reset the state to "idle" when time runs out
                motorController.start_stop_motor("idle"); // Signal to stop the motor in the backend
                countdownTimer.stop(); // Stop the timer
                mainScreen.updateUI(); // Ensure UI reflects the "idle" state
            }
        }
    }




 // StartScreeen popup
    Popup {
        id: loadingPopup
        width: 460
        height: 300
        modal: true
        anchors.centerIn: parent
        background: Rectangle {
            color: "light grey"
            radius: 10
            anchors.fill: parent
            Image {
                id: logo
                source: "svg/ASTech.svg"
                anchors.centerIn: parent
                width: 300
                height: 300
                fillMode: Image.PreserveAspectFit
            }
        }
        Component.onCompleted: open()
    }

    Timer {
        interval: 5000
        running: true
        repeat: false
        onTriggered: loadingPopup.close()
    }

    Component.onCompleted: loadingPopup.open()
 //Main Screen
    Rectangle {
        id: mainScreen
        color: "grey"
        anchors.fill: parent
        property int cumulativeTime: 0 // Holds the total selected time in seconds



        // Timer to reset textOutput after 2 seconds
        Timer {
            id: resetTextOutputTimer
            interval: 2000 // 2 seconds
            repeat: false
            onTriggered: {
                // Check the application's current state to decide what text to display
                if (buttonStartStop.state === "idle") {
                    labelText.text = "IDLE";
                } else if (buttonStartStop.state === "run" || buttonStartStop.state === "timed run") {
                    labelText.text = "RUNNING";
                } else {
                    // This condition can be adjusted based on other states or requirements
                    labelText.text = mainScreen.cumulativeTime > 0 ? mainScreen.formatTime(mainScreen.cumulativeTime) : "IDLE";
                }
            }
        }


           function updateTextOutputWithStateChange(newState) {
               // Update the textOutput to reflect the new state
               labelText.text =  newState;
               // Start the timer to revert back to normal after 2 seconds
               resetTextOutputTimer.restart();
           }

        function formatTime(seconds) {
            var minutes = Math.floor(seconds / 60);
            var remainingSeconds = seconds % 60;
            return (minutes < 10 ? "0" : "") + minutes + ":" + (remainingSeconds < 10 ? "0" : "") + remainingSeconds;
        }

        function updateUI() {
            if (buttonStartStop.state === "idle") {
                if (cumulativeTime > 0) {
                    // Display the formatted cumulativeTime if time has been selected but not started
                    labelText.text = formatTime(cumulativeTime);
                } else {
                    labelText.text = "IDLE";
                }
            } else if (buttonStartStop.state === "run") {
                labelText.text = "RUNNING";
            } else if (buttonStartStop.state === "timed run") {
                labelText.text = formatTime(cumulativeTime);
            }
        }

        // Button for Starting and Stopping the nema17 motor.

        RoundButton {
            id: buttonStartStop
            text: ""
            font.bold: true
            state: "idle"
            font.pixelSize: 30
            width: 140
            height: 140
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.margins: 10
            background: Rectangle {
                color: (buttonStartStop.state === "run" || buttonStartStop.state === "timed run") ? "#FF0000" : "#00FF00"
                radius: 70
                border.color: "white"
                border.width: 3
            }

            contentItem: Text {
                text: buttonStartStop.text
                font: buttonStartStop.font
                color: "white"
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
            }
            states: [
                State {
                    name: "idle"
                    PropertyChanges { target: buttonStartStop; text: "START" }
                },
                State {
                    name: "run"
                    PropertyChanges { target: buttonStartStop; text: "STOP" }
                },
                State {
                    name: "timed run"
                    PropertyChanges { target: buttonStartStop; text: "STOP" }
                }
            ]



            onClicked: {
                if (buttonTimeMode.state === "constant") {
                    // Toggle between "idle" and "run" states for constant mode
                    var motorState = (state === "idle") ? "run" : "idle";
                    motorController.start_stop_motor(motorState); // Signal to start or stop the motor in constant mode
                    state = motorState; // Update the button state accordingly
                    mainScreen.updateUI();
                } else if (buttonTimeMode.state === "timed") {
                    // For "timed" mode, handle differently based on whether it's starting or stopping
                    if (state === "idle" && mainScreen.cumulativeTime > 0) {
                        state = "timed run";
                        motorController.start_stop_motor("run"); // Signal to start the motor in timed mode
                        countdownTimer.start();
                        mainScreen.updateUI();
                    } else if (state === "timed run") {
                        // Stopping the timer from "timed run" state
                        countdownTimer.stop();
                        motorController.start_stop_motor("idle"); // Signal to stop the motor
                        state = "idle";
                        mainScreen.cumulativeTime = 0; // Reset time or handle as needed
                        mainScreen.updateUI();
                    }
                    // If "timed run" is selected but no time is set, you could open the time selection popup again
                    else if (mainScreen.cumulativeTime <= 0) {
                        timeSelectionPopup.open();
                    }
                }
            }



        }
// a display output for user to read.
        Rectangle {
            id: textOutput
            width: 286
            height: 120
            color: "white"
            anchors.top: parent.top
            anchors.left: buttonStartStop.right
            anchors.margins: 20
            radius: 10
            Text {
                id: labelText
                anchors.fill: parent
                font.bold: true
                font.pixelSize: 50
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                wrapMode: Text.Wrap
                text: buttonStartStop.state === "idle" ? "IDLE" : buttonStartStop.state === "run" ? "RUNNING" : "00:00" // Placeholder for timer logic
            }
        }


// the time interface for setting countdown.
        Popup {
            id: timeSelectionPopup
            width: 460
            height: 150
            background: Rectangle{
                x:-5
                width:470
                height:150
                radius:10
                color:"light grey"
            }

            modal: true

            // Use Component.onCompleted for initial positioning
            Component.onCompleted: {
                x = (mainWindow.width - width) / 2; // Center horizontally
                y = mainWindow.height - height - 10; // Position at the bottom with a margin
            }



            Row {
                  id: rowtime
                  anchors.fill: parent
                  spacing: 10

                 // Buttons for time selection.
                  Repeater {
                      model: 4 // For three time buttons and one "SET" button
                      delegate: Button {
                          id: delegateButton
                          width: 104
                          height: 120
                          font.pixelSize: 30
                          font.bold: true
                          y:10
                          // The text property of the Button is set below, but we use contentItem for custom text styling.

                          contentItem: Text {
                              text: {
                                  var texts = ["30 Sec", "1 Min", "5 Min", "SET"];
                                  return texts[model.index];
                              }
                              color: "white" // Set the text color to white
                              font: delegateButton.font
                              horizontalAlignment: Text.AlignHCenter
                              verticalAlignment: Text.AlignVCenter
                          }
                          // Apply the regular onClicked behavior for time buttons, but not for the "SET" button
                          onClicked: {
                              if (model.index < 3) {
                                  var timeToAdd = [30, 60, 300][model.index];
                                  mainScreen.cumulativeTime += timeToAdd;
                                  mainScreen.updateUI();
                              }
                          }


                          // For the "SET" button, use a MouseArea to detect long press
                          MouseArea {
                              anchors.fill: parent
                              visible: model.index === 3 // Applies only to the "SET" button
                              onPressed: {
                                  if (model.index === 3) {
                                      resetTimer.start();
                                  }
                              }
                              onReleased: {
                                  if (model.index === 3) {
                                      if (resetTimer.running) {
                                          resetTimer.stop(); // Stop the timer if it was running (short press)
                                          // Close the popup without resetting the timer since it's a short press
                                          timeSelectionPopup.close();
                                      }
                                      // No additional action needed here for a short press
                                      // The reset action is now handled within the timer's triggered condition
                                  }
                              }
                          }
// logic to reset timer with 3 second press
                          Timer {
                              id: resetTimer
                              interval: 3000 // 3 seconds for a long press
                              repeat: false
                              onTriggered: {
                                  // This block now only executes if the timer completes, indicating a long press
                                  mainScreen.cumulativeTime = 0;
                                  mainScreen.updateUI();
                                  buttonStartStop.state = "idle"; // Update this line if you do not want to revert to "idle"
                                  timeSelectionPopup.close();
                              }
                          }


                          // Change the background color based on whether the button is pressed
                          background: Rectangle {
                              anchors.fill: parent
                              color:" light blue"
                              radius: 10
                          }
                      }
                  }



              }
          }
        Row {
            id:rowmain
            anchors.bottom: parent.bottom
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.margins: 0
            spacing: 10 // Adjust spacing between buttons as needed


//button for swithcing on the countdown timer or having in constant run mode.
            Button {
            id: buttonTimeMode
            text: "TIME"
            font.bold: true
            width: 100
            height: 140
            anchors.bottom: parent.bottom
            anchors.left: parent.left
            anchors.margins: 16

            font.pixelSize: 18
            property string state: "constant" // Initial state
            onClicked: {
                    var feedbackText = "";

                    // Check if buttonStartStop is in "run" or "timed run" states
                    if (buttonStartStop.state !== "run" && buttonStartStop.state !== "timed run") {
                        state = state === "constant" ? "timed" : "constant";

                        if (state === "timed") {
                            timeSelectionPopup.open();
                            feedbackText = "TIMED";
                        } else {
                            // When switching to "constant" state, reset countdown and update UI accordingly
                            mainScreen.cumulativeTime = 0; // Reset countdown
                            countdownTimer.stop(); // Stop the countdown timer if running
                            mainScreen.updateUI(); // Update the UI to reflect the reset
                            feedbackText = "CONSTANT";
                        }
                    } else {
                        // If in "run" or "timed run", only allow opening the time selection popup
                        // without toggling the "constant" or "timed" state
                        if (state === "timed") {
                            timeSelectionPopup.open();

                        } else {
                            // Provide feedback that changing modes is not allowed while the timer is running
                            mainScreen.updateTextOutputWithStateChange("Not Permitted");

                        }
                    }

                    // Update textOutput with the feedback text, ensuring it's not empty
                    if (feedbackText !== "") {
                        mainScreen.updateTextOutputWithStateChange(feedbackText);
                    }
                }



            contentItem: Text {
                text: buttonTimeMode.text
                font: buttonTimeMode.font
                color: "white"
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVTop
            }
            background: Item {
                width: parent.width
                height: parent.height
                Rectangle {
                    color: "dark grey"
                    width: parent.width
                    height: parent.height
                    border.color: "white"
                    border.width: 3
                    radius: 10
                }
                Rectangle {
                    id: stateIndicator
                    color: buttonTimeMode.state === "constant" ? "light blue" : "blue"
                    width: parent.width - 10
                    height: 20
                    y: parent.height - 25
                    x: 5
                    radius: 5
                    Text {
                        text: buttonTimeMode.state.toUpperCase()
                        color: "white"
                        anchors.centerIn: parent
                        font.pixelSize: 14 // Adjust as needed
                        font.bold: true
                    }
                }
            }
        }

// button for selection the run pattern.
            Button {
                id: buttonMode
                text: "MODE"
                font.bold: true
                width: 100
                height: 140
                anchors.bottom: parent.bottom
                anchors.left: buttonTimeMode.right
                anchors.margins: 16

                font.pixelSize: 18
                property string modeState: "FWD" // Initial mode state
                property var states: ["FWD", "RWD", "PULSE", "MIX"]
                property int stateIndex: 0 // Index to cycle through states
                // Map each mode to a specific color
                property var modeColors: {"FWD": "#FFA500", "RWD": "#FF8C00", "PULSE": "#FF7F50", "MIX": "#FF4500"}


                onClicked: {
                       if (buttonStartStop.state === "idle") {
                           // Allow cycling through all modes when idle
                           stateIndex = (stateIndex + 1) % states.length;
                           modeState = states[stateIndex];
                           motorController.set_mode(modeState);
                           mainScreen.updateTextOutputWithStateChange(modeState);
                       } else if (buttonStartStop.state === "run" || buttonStartStop.state === "timed run") {
                           // When not idle, restrict toggling between "FWD" and "RWD"
                           if (modeState === "FWD" || modeState === "RWD") {
                               // Toggle between "FWD" and "RWD"
                               modeState = (modeState === "FWD") ? "RWD" : "FWD";
                               motorController.set_mode(modeState);
                               mainScreen.updateTextOutputWithStateChange(modeState);
                           } else {
                               // If mode is "PULSE" or "MIX", do not allow changes and show a message
                               mainScreen.updateTextOutputWithStateChange("Not Permitted");
                           }
                       } else {
                           // For any other state of buttonStartStop, prevent mode changes
                           mainScreen.updateTextOutputWithStateChange("Not Permitted");
                       }
                   }


                contentItem: Text {
                    text: buttonMode.text
                    font: buttonMode.font
                    color: "white"
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVTop
                }

                background: Item {
                    width: parent.width
                    height: parent.height
                    Rectangle {
                        color: "dark grey"
                        width: parent.width
                        height: parent.height
                        border.color: "white"
                        border.width: 3
                        radius: 10
                    }
                    Rectangle {
                        id: modeIndicator
                        // Use the modeState to determine the color dynamically
                        color: buttonMode.modeColors[buttonMode.modeState]
                        width: parent.width - 10
                        height: 20
                        y: parent.height - 25
                        x: 5
                        radius: 5
                        Text {
                            text: buttonMode.modeState // Display the current mode state
                            color: "white"
                            anchors.centerIn: parent
                            font.pixelSize: 14
                            font.bold: true
                        }
                    }
                }
            }

// button for selecting speed
            Button {
                id: buttonSpeed
                text: "SPEED"
                font.bold: true
                width: 100
                height: 140
                anchors.bottom: parent.bottom
                anchors.left: buttonMode.right
                anchors.margins: 16

                font.pixelSize: 18
                property string speedState: "LOW" // Initial speed state
                property var speeds: ["LOW", "MID", "HIGH"]
                property int speedIndex: 0 // Index to cycle through speeds
                // Map each speed to a specific shade of yellow
                property var speedColors: {"LOW": "#98FB98", "MID": "#66CDAA" , "HIGH": "#00FF00"}


                onClicked: {
                       // Check if system is in "idle" state or if the mode is "FWD" or "RWD"
                       if (buttonStartStop.state === "idle" || buttonMode.modeState === "FWD" || buttonMode.modeState === "RWD") {
                           // Proceed with speed change logic
                           speedIndex = (speedIndex + 1) % speeds.length;
                           speedState = speeds[speedIndex];
                           motorController.set_speed(speedState);
                           mainScreen.updateTextOutputWithStateChange(speedState.toUpperCase());
                       } else {
                           // If buttonStartStop is in "run" or "timed run" and not in allowed modes, display a message
                           mainScreen.updateTextOutputWithStateChange("Not Permitted");
                       }
                   }



                contentItem: Text {
                    text: buttonSpeed.text
                    font: buttonSpeed.font
                    color: "white"
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVTop
                }

                background: Item {
                    width: parent.width
                    height: parent.height
                    Rectangle {
                        color: "dark grey"
                        width: parent.width
                        height: parent.height
                        border.color: "white"
                        border.width: 3
                        radius: 10
                    }
                    Rectangle {
                        id: speedIndicator
                        // Use the speedState to determine the color dynamically
                        color: buttonSpeed.speedColors[buttonSpeed.speedState]
                        width: parent.width - 10
                        height: 20
                        y: parent.height - 25
                        x: 5
                        radius: 5
                        Text {
                            text: buttonSpeed.speedState // Display the current speed state
                            color: "white"
                            anchors.centerIn: parent
                            font.pixelSize: 14
                            font.bold: true
                        }
                    }
                }
            }
// button for output to relay, "off" is open "hot" is closed.
            Button {
                id: buttonHeat
                text: "HEATER"
                font.bold: true
                width: 100
                height: 140
                anchors.bottom: parent.bottom
                anchors.left: buttonSpeed.right
                anchors.margins: 16

                font.pixelSize: 18
                property string heatState: "OFF" // Initial heater state
                property var heatStates: ["OFF", "HOT"]
                property int heatIndex: 0 // Index to cycle through heat states
                // Map each heat state to a specific color
                property var heatColors: {"OFF": "#FFC0CB", "HOT": "#FF0000"}

                onClicked: {
                      heatIndex = (heatIndex + 1) % heatStates.length;
                      heatState = heatStates[heatIndex];

                      // Update the textOutput to reflect the new state of the heater
                      mainScreen.updateTextOutputWithStateChange( heatState.toUpperCase());
                  }


                contentItem: Text {
                    text: buttonHeat.text
                    font: buttonHeat.font
                    color: "white"
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVTop
                }

                background: Item {
                    width: parent.width
                    height: parent.height
                    Rectangle {
                        color: "dark grey"
                        width: parent.width
                        height: parent.height
                        border.color: "white"
                        border.width: 3
                        radius: 10
                    }
                    Rectangle {
                        id: heatIndicator
                        // Use the heatState to determine the color dynamically
                        color: buttonHeat.heatColors[buttonHeat.heatState]
                        width: parent.width - 10
                        height: 20
                        y: parent.height - 25
                        x: 5
                        radius: 5
                        Text {
                            text: buttonHeat.heatState // Display the current heater state
                            color: "white"
                            anchors.centerIn: parent
                            font.pixelSize: 14
                            font.bold: true
                        }
                    }
                }
            }

        }
    }

}
