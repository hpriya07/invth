from flask import Flask, render_template, request, jsonify, session
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
import mysql.connector
import math
import uuid
import os
import matplotlib   #
matplotlib.use('Agg')  #
import matplotlib.pyplot as plt  #

app = Flask(__name__, static_folder='static')
app.secret_key = 'spark'
app.use_x_sendfile = False

def generate_unique_filename():
    unique_id = str(uuid.uuid4())  # Generate a unique ID (UUID)
    filename = f"image_{unique_id}.png"  # Create a filename using the unique ID
    return filename

@app.route('/')
def index():
    return render_template('page1.html')

@app.route('/add_coordinates',methods=['POST'])
def add_coordinates():
    # Your existing code for calculations and image generation
    data = request.json  # Get the JSON data from the POST request
    latitude = data['latitude']
    longitude = data['longitude']
 
    # Replace these values with your database credentials
    db_config = {
    "host": "localhost",
    "user": "root",
    "password": "1234",
    "database": "gwat"
    }
 
# Establish a connection to the database
    conn = mysql.connector.connect(**db_config)
 
# Create a cursor object
    cursor = conn.cursor()
 
# Execute a SQL query
    query = "SELECT ph, chlorine, fluorine, nitrate, sulphate FROM cgwb WHERE lattitude=%s AND longitude=%s"
    cursor.execute(query, (latitude, longitude))
 
# Fetch and print the data
    data = cursor.fetchone()  # Assuming you expect only one row
    def yvalue(i, j, X):
        value = [
        [0, 25, 50, 100, 100, 0],
        [(-0.4 * math.log(X) + 175), (-0.0714 * math.log(X) + 92.86), (-0.125 * math.log(X) + 125)],
        [0, 100, (-260.8 * math.log(X) + 205.38), 0],
        [(-2 * X + 115), (-0.8333 * X + 91.67), (-0.5 * X + 75), (-0.25 * X + 50)],
        [100, (-0.16 * X + 99), (-0.25 * X + 112.5), (-0.1667 * X + 91.67), (-0.0156 * X + 31.25)]]
        return value[i][j]
 
# Convert data fetched from the database to appropriate data types
    ph, chlorine, fluorine, nitrate, sulphate = map(float, data)
 
    my_list = [ph, chlorine, fluorine, nitrate, sulphate]
    parameters = ["ph", "chlorine", "fluorine", "nitrate", "sulfate"]
    provided_values = [7, 200, 1.1, 1, 25]
    
 
    # Create a bar plot of the water quality parameters
    plt.figure(figsize=(10, 6))
    plt.plot(parameters, my_list, marker='o', linestyle='-', color='blue', label='Actual Values')
 
    # Plot the provided values in green
    plt.plot(parameters, provided_values, marker='o', linestyle='-', color='green', label='Provided Values')
 
    plt.title("Water Quality Parameters")
    plt.xlabel("Parameter")
    plt.ylabel("Value")
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plot_file_path = os.path.join('static', generate_unique_filename())
    plt.savefig(plot_file_path)  # Save the plot as an image
 
    para = [
    [(0, 5.5), (5.5, 5.9), (6, 6.4), (6.5, 8.5), (8.6, 9), (9, 10)],
    [(201, 250), (251, 600), (800, 1000)],
    [(0, 0.7), (0.7, 1.2), (1.6, 2.0), (2.0, 5.0)],
    [(11, 20), (21, 50), (51, 100), (101, 110)],
    [(0, 25), (26, 150), (151, 250), (251 ,400), (401 ,1000)]]
 
    weight = [1, 1, 3, 3, 2]
    total_sum = 0
 
    for i in range(len(my_list)):
        value = my_list[i]
        for j in range(len(para[i])):
            start, end = para[i][j]
            if start <= value <= end:
                get = yvalue(i, j, value)
                total_sum += (get * weight[i])
    total=total_sum/5
    session['total'] = total
    print(total)
    if(0<=total<=24):
        print("HEAVILY POLLUTED")
        print("Unsuitable for any purpose")
        sterilise="HEAVILY POLLUTED unsuitable for any purpose"
    elif(25<=total<=49):
        print("POOR")
        print("special treatment required, hence use only after treating it")
        sterilise="POOR CONDITION OF WATER,1)use water only after treating it  2) Boil water 3) doFiltration & UV Sterilization"
    elif(50<=total<=74):
        print("FAIR")
        print("FAIR CONDITION OF WATER  needs treatment, filter at your home once or use disinfectants")
        sterilise="FAIR QUALITY OF WATER, NEEDS TREATMENT.Refer to graph for details."
    elif(75<=total<=94):
        print("GOOD")
        print("acceptable quality")
        sterilise="ACCEPTABLE QUALITY OF WATER Basic water filtration is required"
    else:
        print("EXCELLENT")
        print("pristine quality")
        sterilise="PRISTINE QUALITY OF WATER,basic filter is enough"
    session['sterilise'] = sterilise
 
# Close the cursor and the connection
    cursor.close()
    conn.close()
    session['unique_filename'] = plot_file_path
 
    # Respond with a JSON message
    response = {'message': 'Coordinates received successfully'}
    return jsonify(response)

    # Generate a unique filename for the image
    unique_filename = generate_unique_filename()
    image_path = os.path.join('static', unique_filename)
    plt.savefig(image_path)  # Save the plot as an image with the unique filename

    # Pass the unique image filename to the 'result.html' template
    return render_template('page2.html', water_quality=total, sterilise=sterilise, image_filename=unique_filename, os=os)

@app.route('/page2.html',methods=['GET'])
def result_page():
        # Create an empty list to store the predictions
    predictions = []

# Create a DataFrame with the provided data
    data = {
        "YEAR": [2021, 2020, 2019, 2018, 2017, 2016, 2015, 2014, 2013, 2012, 2011, 2010, 2009, 2008, 2007, 2006, 2005, 2004, 2003, 2002, 2001, 2000],
        "ph": [7.32, 7.28, 7.21, 7.0, 7.0, 7.0, 7.0, 6.90, 6.91, 6.97, 6.87, 6.89, 6.85, 6.81, 6.3, 6.29, 6.35, 6.29, 6.32, 6.30, 6.27, 6.27],
        "chlorine": [137, 156, 157, 149, 128, 158, 136, 154, 153, 122, 150, 150, 148, 118, 140, 141, 132, 127, 129, 120, 126, 147],
        "fluorine": [0.5, 0.51, 0.51, 0.51, 0.48, 0.49, 0.45, 0.5, 0.56, 0.45, 0.59, 0.5, 0.51, 0.51, 0.51, 0.48, 0.49, 0.45, 0.5, 0.56, 0.45, 0.59],
        "nitrate": [12,32,29, 39,34,32,31,28,29,29,29,34,32,29,39,34,32,31,28,29,29,29],
        "sulphate": [20, 21, 26, 27, 26, 36, 36, 26, 36, 36, 26, 26, 28, 26, 26, 28, 28, 27, 25, 27, 26, 26]
    }

    df = pd.DataFrame(data)

    # Define the target variables
    target_variables = ['ph', 'chlorine', 'fluorine', 'nitrate', 'sulphate']

    for target_var in target_variables:
        y = df[target_var]

        # Train the ARIMA model
        p, d, q = 1, 1, 1  # Adjust these values based on your analysis
        model = ARIMA(y, order=(p, d, q))
        model_fit = model.fit(start_params=[0.5, 0.2, 0.3])

        # Make predictions for 2024, 2025, and 2026
        forecast_steps = 3  # Adjust the number of steps as needed
        predicted_values = model_fit.forecast(steps=forecast_steps).values
        predictions.append(predicted_values.tolist())

        for i, year in enumerate(range(2024, 2027)):
            print(f"Predicted {target_var} value for {year}: {predicted_values[i]}")
            
    total = session.get('total', 0)
    sterilise = session.get('sterilise', 'N/A')
    unique_filename = session.get('unique_filename', 'default.png')
    yr24 = predictions[0][0]
    cl1=predictions[1][0]
    fl1=predictions[2][0]
    ni1=predictions[3][0]
    su1=predictions[4][0]
    yr25=predictions[0][1]
    cl2=predictions[1][1]
    fl2=predictions[2][1]
    ni2=predictions[3][1]
    su2=predictions[4][1]
    yr26=predictions[0][2]
    cl3=predictions[1][2]
    fl3=predictions[2][2]
    ni3=predictions[3][2]
    su3=predictions[4][2]
    return render_template('page2.html', water_quality=total, sterilise=sterilise,image_filename=unique_filename,
                           os=os,yr24=yr24,cl1=cl1,fl1=fl1,ni1=ni1,su1=su1,yr25=yr25,cl2=cl2,fl2=fl2,ni2=ni2,su2=su2,yr26=yr26,cl3=cl3,fl3=fl3,ni3=ni3,su3=su3)

if __name__ == '__main__':
    app.run(debug=True)
