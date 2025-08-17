import smaract.ctl as ctl
import numpy as np
import matplotlib.pyplot as plt
import time

# Dummy function to simulate Thorlabs power meter reading
def read_power_meter():
    return np.random.rand() * 10  # Replace with actual API call

# Connect to the first available MCS2 device
devices = ctl.FindDevices()
if not devices:
    raise RuntimeError("No MCS2 devices found!")

device_id = ctl.Open(devices[0])

# Define scan area (units in nanometers)
x_start, x_end, x_steps = 0, 50000, 10  # X-axis from 0 to 50µm in 10 steps
y_start, y_end, y_steps = 0, 50000, 10  # Y-axis from 0 to 50µm in 10 steps
x_positions = np.linspace(x_start, x_end, x_steps)
y_positions = np.linspace(y_start, y_end, y_steps)

# Store power measurements and positions
power_data = np.zeros((x_steps, y_steps))
max_power = 0
max_position = (0, 0)

# Perform scan
for i, x in enumerate(x_positions):
    for j, y in enumerate(y_positions):
        ctl.Move(device_id, 0, x, 500)  # Move X
        ctl.Move(device_id, 1, y, 500)  # Move Y
        ctl.WaitForMotionDone(device_id, 0)
        ctl.WaitForMotionDone(device_id, 1)
        
        time.sleep(0.5)  # Wait for stability before measurement
        power = read_power_meter()
        power_data[i, j] = power
        
        if power > max_power:
            max_power = power
            max_position = (x, y)

# Move back to maximum power position
ctl.Move(device_id, 0, max_position[0], 500)
ctl.Move(device_id, 1, max_position[1], 500)
ctl.WaitForMotionDone(device_id, 0)
ctl.WaitForMotionDone(device_id, 1)

# Close connection
ctl.Close(device_id)

# Plot intensity map
plt.figure(figsize=(8, 6))
plt.imshow(power_data.T, extent=[x_start, x_end, y_start, y_end], origin='lower', cmap='hot')
plt.colorbar(label='Power (mW)')
plt.scatter(*max_position, color='blue', marker='x', label='Max Power')
plt.xlabel('X Position (nm)')
plt.ylabel('Y Position (nm)')
plt.title('Power Intensity Map')
plt.legend()
plt.show()

print(f"Max power found at: {max_position} with power: {max_power} mW")
