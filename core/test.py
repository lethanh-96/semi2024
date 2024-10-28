import matplotlib.pyplot as plt
import numpy as np
import time

# Turn on the interactive mode.
plt.ion()

# Create a figure and an axis.
fig, ax = plt.subplots()

# Initial data.
data = np.random.rand(10, 10)

# Create the imshow plot.
img = ax.imshow(data, cmap='viridis')

# Update loop
try:
    for _ in range(100):  # Update the image 100 times.
        # Generate new data.
        data = np.random.rand(10, 10)

        # Update the image data.
        img.set_data(data)

        # Pause to allow updates.
        plt.pause(0.1)  # Pause for a short time to update the plot (units are in seconds).

        # Optional: Do other tasks here (e.g., data processing, computation).
except KeyboardInterrupt:
    # Handle the case if you want to stop the update loop with a keyboard interrupt.
    pass

# Keep plot open
plt.ioff()  # Turn off interactive mode to keep the plot open.
plt.show()  # Show the final plot.
