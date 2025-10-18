#pragma config(Motor,  port1, motor1, tmotorVex393_HBridge, openLoop) // bucket
#pragma config(Motor,  port2, motor2, tmotorVex393_MC29, openLoop)   // conveyor
#pragma config(Sensor, dgtl1, pieceSensor, sensorDigitalIn)

task main()
{
    string command;
    while(true)
    {
        if(getChar(UART1) != -1)  // check if a byte is available
        {
            command = ""; 
            
            // read a full command (terminated by newline)
            while(getChar(UART1) != '\n')
            {
                command += getChar(UART1);
            }

            // --- Parse command ---
            if(command == "M1_CW90")
            {
                motor[motor1] = 127;
                wait1Msec(1000); // fixed time for 90°, tune experimentally
                motor[motor1] = 0;
            }
            else if(command == "M1_CCW90")
            {
                motor[motor1] = -127;
                wait1Msec(1000);
                motor[motor1] = 0;
            }
            else if(command == "M1_STOP")
            {
                motor[motor1] = 0;
            }
            else if(command == "M2_START")
            {
                motor[motor2] = 127;
            }
            else if(command == "M2_STOP")
            {
                motor[motor2] = 0;
            }
        }
    }
}
