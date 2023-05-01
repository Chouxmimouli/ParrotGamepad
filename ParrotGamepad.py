import asyncio
from bleak import BleakScanner, BleakClient
import vgamepad as vg

# Define the virtual gamepad
gamepad = vg.VX360Gamepad()

DEVICE_UUID = "9e35fa01-4344-44d4-a2e2-0c7f6046878b"

# Define the callback function for receiving data from the BLE device
def notification_handler(sender, data):
    # Extract the joystick data from the received data
    Lx, Ly = data[3], data[4]
    Rx, Ry = data[5], data[6]

    # convert 0 > 255 to -1 > 1
    def conversion(input):
        OldMin = 0
        OldMax = 255
        NewMin = -1
        NewMax = 1

        OldValue = input

        OldRange = (OldMax - OldMin)
        NewRange = (NewMax - NewMin)
        NewValue = float((((OldValue - OldMin) * NewRange) / OldRange) + NewMin)

        return NewValue

    def Buttons(data):
        # Assume the byte is stored in a variable called 'data'
         # Create a dictionary to map button numbers to their corresponding bits
        button_map = {"To": 0, 1: 1, 2: 2, "B": 3, "A": 4, "R1": 5, "R2": 6, "L1": 7}

        # Initialize a list to store the pressed buttons
        pressed_buttons = []

        # Iterate through the button map
        for button, bit in button_map.items():
            # Use a bitwise AND operation to check if the bit is set to 1 in the data byte
            if data[1] & (1 << bit):
                # If the bit is set, add the button number to the pressed buttons list
                pressed_buttons.append(button)

        # Print the list of pressed buttons
        print("Pressed buttons:", pressed_buttons)

    # Map the joystick data from the range of 0-255 to -32768-32767
    R_Joystick_Yaw = conversion(Rx)
    R_Joystick_Pitch = conversion(Ry) * -1

    L_Joystick_Yaw = conversion(Lx)
    L_Joystick_Pitch = conversion(Ly) * -1

    # Set the virtual gamepad joystick positions
    gamepad.left_joystick_float(x_value_float=R_Joystick_Yaw, y_value_float=R_Joystick_Pitch)  # values between -1.0 and 1.0
    gamepad.right_joystick_float(x_value_float=L_Joystick_Yaw, y_value_float=L_Joystick_Pitch)  # values between -1.0 and 1.0


async def run():
    # Discover nearby devices
    print("Looking for Bluetooth (BLE) devices in range...")
    print("The default UUID is : 9e35fa01-4344-44d4-a2e2-0c7f6046878b. It works with the Parrot FlyPad")

    devices = await BleakScanner.discover()
    # Print the list of discovered devices
    for i, device in enumerate(devices):
        print(f"{i+1}. {device.name} ({device.address})")

    # Ask the user to select a device to connect to
    selection = input("Select a device to connect to: ")
    selected_device = devices[int(selection)-1]

    # Connect to the selected device
    async with BleakClient(selected_device.address) as client:
        # Enable notifications for the specified UUID
        await client.start_notify(DEVICE_UUID, notification_handler)
        print("The specified device should now be connected.")

        # Loop indefinitely to keep the program running
        while True:
            # Update the virtual gamepad state
            gamepad.update()

            # Wait for a short period to prevent excessive CPU usage
            await asyncio.sleep(0.001)


if __name__ == "__main__":
    asyncio.run(run())
