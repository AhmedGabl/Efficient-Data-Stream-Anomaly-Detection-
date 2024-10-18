import numpy as np
import matplotlib.pyplot as plt
import random
from collections import deque

# Configuration settings
WINDOW_SIZE = 50          # Size of the rolling window for calculating mean and standard deviation
Z_THRESHOLD = 3           # Z-score threshold to identify anomalies
SEASONALITY_PERIOD = 100   # Periodicity for the seasonal component in the simulated data
ANOMALY_PROBABILITY = 0.1  # Probability of introducing an anomaly (higher values = more anomalies)

class AnomalyDetector:
    """
    Anomaly detection using rolling Z-scores.

    This class monitors a stream of data and flags any values that
    deviate significantly from the norm based on a rolling window of past data.
    It uses the Z-score method to assess whether a new value is an anomaly.
    """

    def __init__(self, window_size, z_threshold):
        """
        Initializes the anomaly detector.

        Args:
            window_size (int): Number of data points to keep in the rolling window.
            z_threshold (float): Z-score value above which a data point is flagged as an anomaly.
        """
        self.window_size = window_size
        self.z_threshold = z_threshold
        self.data_window = deque(maxlen=window_size)  # A deque to store the rolling window of data
        self.mean = 0
        self.std = 0

    def update(self, new_value):
        """
        Add a new data point to the window and determine if it's an anomaly.

        Args:
            new_value (float): The latest value from the data stream.
        
        Returns:
            bool: True if the value is flagged as an anomaly, otherwise False.
        """
        try:
            # Ensure the new value is a number (int or float)
            if not isinstance(new_value, (float, int)):
                raise ValueError("The new value must be a numeric type (int or float).")
            
            # Add the new value to the rolling window
            self.data_window.append(new_value)

            # Once the window is full, calculate mean and std deviation for Z-score
            if len(self.data_window) == self.window_size:
                self.mean = np.mean(self.data_window)
                self.std = np.std(self.data_window)

                # Compute the Z-score for the new value
                z_score = (new_value - self.mean) / self.std if self.std else 0

                # Return True if the Z-score exceeds the threshold, indicating an anomaly
                return abs(z_score) > self.z_threshold
            return False
        except Exception as e:
            print(f"Error in AnomalyDetector: {e}")
            return False


def generate_data_stream(steps, seasonality_period=100, anomaly_prob=0.1):
    """
    Simulates a continuous stream of data with seasonal trends, noise, and occasional anomalies.

    Args:
        steps (int): Number of data points to generate.
        seasonality_period (int): The period of the seasonal component (e.g., how often it repeats).
        anomaly_prob (float): Probability that an anomaly will be injected into the stream.
    
    Yields:
        float: The next data point in the stream.
    """
    for step in range(steps):
        # Create a repeating seasonal pattern using a sine wave
        seasonal = 10 * np.sin(2 * np.pi * step / seasonality_period)
        
        # Introduce a slow upward trend
        trend = 0.05 * step
        
        # Add some randomness to simulate real-world noise
        noise = random.uniform(-1, 1)
        
        # Combine the seasonal pattern, trend, and noise to create the data point
        value = seasonal + trend + noise
        
        # Occasionally inject an anomaly (large spike) based on the anomaly probability
        if random.random() < anomaly_prob:
            value += random.uniform(10, 20)  # Add a large positive spike to create an anomaly
        
        yield value


def run_detection_and_visualization(steps=500):
    """
    Runs the anomaly detection system and visualizes the data in real time.

    This function generates a simulated data stream, applies anomaly detection, 
    and continuously updates a plot to show the data stream and any detected anomalies.

    Args:
        steps (int): Number of data points to generate and analyze.
    """
    try:
        # Initialize the anomaly detector with the chosen window size and Z-score threshold
        detector = AnomalyDetector(WINDOW_SIZE, Z_THRESHOLD)
        
        # Start generating the data stream
        data_stream = generate_data_stream(steps, SEASONALITY_PERIOD, ANOMALY_PROBABILITY)
        
        # Lists to hold the data values and detected anomalies
        values = []
        anomalies = []

        # Set up the real-time plot
        plt.ion()  # Turn on interactive mode for real-time plotting
        fig, ax = plt.subplots()
        ax.set_title("Real-Time Anomaly Detection")
        ax.set_xlabel("Time Step")
        ax.set_ylabel("Data Value")
        
        # Line plot for the normal data stream
        line, = ax.plot([], [], label='Data Stream')
        # Scatter plot for marking anomalies
        anomaly_scatter = ax.scatter([], [], color='red', label='Anomaly', zorder=5)

        # Process the data stream, update the anomaly detector, and update the plot
        for i, value in enumerate(data_stream):
            values.append(value)

            # Check if the current data point is an anomaly
            is_anomaly = detector.update(value)

            # If it's an anomaly, store the value for the scatter plot
            anomalies.append(value if is_anomaly else None)

            # Update the line and scatter plot with new data
            line.set_xdata(range(len(values)))
            line.set_ydata(values)
            anomaly_scatter.set_offsets(np.column_stack((range(len(values)), anomalies)))

            # Adjust the plot's axes to fit the data
            ax.relim()
            ax.autoscale_view()
            plt.pause(0.01)  # Short pause for real-time effect

        plt.ioff()  # Turn off interactive mode
        plt.show()  # Display the final plot
    except Exception as e:
        print(f"Error in visualization: {e}")


if __name__ == "__main__":
    run_detection_and_visualization()
