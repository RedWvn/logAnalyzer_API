from flask import Flask, request
from flask_restful import Resource, Api
from werkzeug.utils import secure_filename
import pandas as pd
import subprocess
import os

app = Flask(__name__)
api = Api(app)

# def extract_bindata(bin_file):
#     mavlogdump_path = "site-packages/pymavlink/tools/mavlogdump.py"
#     csv_file = 'temp.csv'
#     temp_bin_file = 'temp.bin'
#     # with open(temp_bin_file, 'wb') as f:
#     #     f.write(bin_file.getvalue())
#     with open(bin_file, 'rb') as f:
#         bin_data = f.read()
#     with open(temp_bin_file, 'wb') as f:
#         f.write(bin_data)

#     log_types = ['ATT', 'BAT', 'CTUN', 'TECS', 'GPS', 'CMD']
#     dfs = []
#     for log_type in log_types:
#         with open(csv_file, 'w') as f:
#             subprocess.run(['python', mavlogdump_path, '--types', log_type, '--format', 'csv', temp_bin_file], stdout=f)
#         df = pd.read_csv(csv_file)
#         df.columns = [f'{log_type}.{col}' for col in df.columns]
#         dfs.append(df)
#     df = pd.concat(dfs, axis=1)
#     df_CTUN = df[['CTUN.ThO', 'CTUN.As', 'ATT.Pitch']]
#     df_CMD = df[[col for col in df.columns if col.startswith('CMD.')]]
#     df = df[['GPS.TimeUS', 'BAT.Volt', 'BAT.Curr',  'TECS.sp', 'GPS.Spd', 'GPS.Alt']]
#     df_waypoints = df_CMD[df_CMD['CMD.CId'] == 16]
#     df_waypoints.columns = [f'Waypoint.{col}' for col in df_waypoints.columns]
#     df['Power'] = df['BAT.Volt'] * df['BAT.Curr']
#     df['Efficiency'] = (df['BAT.Volt'] * df['BAT.Curr']) / (df['GPS.Spd'] * 3.6)
#     return df, df_CTUN, df_CMD, df_waypoints

def extract_bindata(bin_file):
    mavlogdump_path = "site-packages/pymavlink/tools/mavlogdump.py"
    csv_file = 'temp.csv'
    temp_bin_file = 'temp.bin'
    with open(bin_file, 'rb') as f:
        bin_data = f.read()
    with open(temp_bin_file, 'wb') as f:
        f.write(bin_data)
        
    log_types = ['ATT', 'BAT', 'CTUN', 'TECS', 'GPS', 'CMD']
    dfs = []
    for log_type in log_types:
        with open(csv_file, 'w') as f:
            subprocess.run(['python', mavlogdump_path, '--types', log_type, '--format', 'csv', temp_bin_file], stdout=f)
        df = pd.read_csv(csv_file)
        df.columns = [f'{log_type}.{col}' for col in df.columns]
        dfs.append(df)
    df = pd.concat(dfs, axis=1)

    # Calculate the number of kilometers traveled
    df['GPS.Dist'] = df['GPS.Spd'] * df['GPS.TimeUS'] / (1000 * 60 * 60)
    km_travelled = df['GPS.Dist'].sum()

    # Get the mAh consumed
    mah_consumed = df['BAT.Curr'].sum() / (60 * 60)

    # Calculate the flight time
    flight_time = df['GPS.TimeUS'].max() - df['GPS.TimeUS'].min()

    return km_travelled, mah_consumed, flight_time


# class FlightLogAnalyzer(Resource):
#     def post(self):
#         bin_file = request.files['file']
#         filename = secure_filename(bin_file.filename)
#         bin_file.save(filename)
#         df, df_CTUN, df_CMD, df_waypoints = extract_bindata(filename)
#         return {'data': df.to_dict(), 'CTUN': df_CTUN.to_dict(), 'CMD': df_CMD.to_dict(), 'waypoints': df_waypoints.to_dict()}
class FlightLogAnalyzer(Resource):
    def post(self):
        bin_file = request.files['file']
        filename = secure_filename(bin_file.filename)
        bin_file.save(filename)
        km_travelled, mah_consumed, flight_time = extract_bindata(filename)
        return {'km_travelled': km_travelled, 'mah_consumed': mah_consumed, 'flight_time': flight_time}


api.add_resource(FlightLogAnalyzer, '/analyze')

if __name__ == '__main__':
    app.run(debug=True)

