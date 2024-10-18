import requests
import cv2
import numpy as np
from PIL import Image
from shapely.geometry import Polygon


# NASA POWER API request for solar data
def get_solar_data(lat, lon, start, end):
    url = f"https://power.larc.nasa.gov/api/temporal/hourly/point?parameters=ALLSKY_SFC_SW_DWN&community=RE&longitude={lon}&latitude={lat}&format=JSON&start={start}&end={end}"
    response = requests.get(url)
    return response.json()


# Function to calculate rooftop area from the image
def calculate_rooftop_area(image_path):
    # Read the image
    image = cv2.imread(image_path)

    # Convert to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply thresholding to create binary image
    _, binary_image = cv2.threshold(gray_image, 200, 255, cv2.THRESH_BINARY)

    # Detect contours
    contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Assume the largest contour is the rooftop
    largest_contour = max(contours, key=cv2.contourArea)

    # Calculate the area of the rooftop in pixels
    area_in_pixels = cv2.contourArea(largest_contour)

    # Convert pixel area to real-world area (meters squared)
    # Assuming 1 pixel corresponds to X square meters (you will need to provide scale)
    scale_factor = 0.25  # Placeholder: 1 pixel = 0.25 square meters (adjust as needed)
    area_in_meters = area_in_pixels * scale_factor

    return area_in_meters
    print("Rooftop area")
    print(area_in_meters)


# Function to calculate solar energy production
"""def calculate_solar_energy(irradiance_data, rooftop_area, panel_efficiency=0.18):
    total_energy = 0  # in watt-hours (Wh)

    # Iterate over the hourly solar irradiance values
    for date, hourly_values in irradiance_data['properties']['parameter']['ALLSKY_SFC_SW_DWN'].items():
        for hour, irradiance in hourly_values.items():
            if irradiance is not None:
                # Convert irradiance to energy (Wh)
                energy = irradiance * rooftop_area * panel_efficiency
                total_energy += energy

    return total_energy """


def calculate_solar_energy(irradiance_data, rooftop_area, panel_efficiency=0.18):
    total_energy = 0  # in watt-hours (Wh)

    # Check if the data contains the expected 'ALLSKY_SFC_SW_DWN' key
    if 'ALLSKY_SFC_SW_DWN' not in irradiance_data['properties']['parameter']:
        print("Error: Solar irradiance data not found in the response.")
        return total_energy

    # Iterate over the hourly solar irradiance values
    for date, hourly_values in irradiance_data['properties']['parameter']['ALLSKY_SFC_SW_DWN'].items():
        print(f"Processing data for date: {date}")  # Debugging: show the date being processed

        # Check if hourly_values is valid (some dates might not have data)
        if not isinstance(hourly_values, dict):
            print(f"Warning: Data for {date} is not in the expected format. Skipping...")
            continue

        for hour, irradiance in hourly_values.items():
            if irradiance is not None:
                # Convert irradiance to energy (Wh)
                energy = irradiance * rooftop_area * panel_efficiency
                total_energy += energy
            else:
                print(f"Missing irradiance data for {date} at hour {hour}. Skipping...")

    return total_energy


# Example usage
if __name__ == "__main__":
    lat = 18.5204  # Latitude of building
    lon = 73.8567  # Longitude of building
    start = '20200101'  # Start date (YYYYMMDD)
    end = '20200131'  # End date (YYYYMMDD)

    # Path to the rooftop image
    image_path = '1.jpg'

    # Get rooftop area from image
    rooftop_area = calculate_rooftop_area(image_path)

    # Get solar irradiance data
    data = get_solar_data(lat, lon, start, end)

    # Calculate total solar energy potential for the given period
    total_energy = calculate_solar_energy(data, rooftop_area)

    # Convert to kilowatt-hours (kWh)
    total_energy_kwh = total_energy / 1000
    print(f"Total solar energy potential: {total_energy_kwh:.2f} kWh for the selected period.")
