from flask import Flask, render_template, request, redirect, url_for
import pickle
import pandas as pd
from datetime import datetime, timedelta
from pytz import timezone

app = Flask(__name__)

# Load ARIMA models for Cargo and Passengers
cargo_models = {}
passengers_models = {}
cargo_countries = ["europe", "france", "germany","hong_kong","indonesia","japan","mainland_china","malaysia","middle_east","north_america","north_east_asia","sout_east","thailand","uk","vietnam"]  # Update with cargo countries
passengers_countries = ["europe", "france", "germany","hong_kong","indonesia","japan","mainland_china","malaysia","middle_east","north_america","north_east_asia","sout_east","thailand","uk","vietnam"]  # Update with passenger countries
countries = [
    "sout_east","indonesia",
    "malaysia","thailand","vietman",
    "north_east_asia","mainland_china",
    "hong_kong","japan","middle_east","europe","france","germany","uk","north_america"]

for country in cargo_countries:
    with open(f"{country.lower().replace(' ', '_')}_cargo_arima_model.pkl", "rb") as f:
        cargo_models[country] = pickle.load(f)

for country in passengers_countries:
    with open(f"{country.lower().replace(' ', '_')}_arima_model.pkl", "rb") as f:
        passengers_models[country] = pickle.load(f)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        selected_type = request.form.get("forecast_type")
        return redirect(url_for("forecast", forecast_type=selected_type))

    return render_template("index.html")

@app.route("/forecast/<forecast_type>", methods=["GET", "POST"])
def forecast(forecast_type):
    if request.method == "POST":
        selected_country = request.form.get("country")
        forecast_periods = int(request.form.get("forecast_periods"))
        forecast_period_td = timedelta(days=forecast_periods)
        if forecast_type =="cargo":
            df = pd.read_csv("Cargo_Prepared_Dataset.csv")
            plot = pd.read_excel("New_Cargo_plots.xlsx")
        else:
            df = pd.read_csv("Prepared_Dataset.csv")
            plot = pd.read_excel("New_Passengers_plots.xlsx")
        if forecast_type == "cargo":
            plot = pd.read_excel("New_Cargo_plots.xlsx")
            selected_model = cargo_models.get(selected_country)
            selected_cols_filter = plot.filter(items=['Year',selected_country])
            print("My selected country",selected_country)
            print(selected_cols_filter,"My selected dataframe")
            if selected_model:
                # Perform cargo forecasting logic using the selected model
                last_date = datetime.fromtimestamp(df.index[-1])
                forecast_dates = [last_date + timedelta(days=i) for i in range(1, forecast_periods + 1)]
                forecast = selected_model.forecast(steps=forecast_periods)
                user_timezone = timezone("Asia/Singapore")
                forecast_dates = [forecast_date.astimezone(user_timezone) for forecast_date in forecast_dates]
                #forecast_data = pd.DataFrame({"Date": '', "Forecast": forecast})
                forecast_data = pd.DataFrame({'Date': forecast.index, 'Forecast': forecast.values}).reset_index(drop=True)
                forecast_data['Date'] = forecast_data['Date'].dt.strftime('%Y-%m-%d')
                forecast_data['Forecast'] = forecast_data['Forecast'].astype(int)
                #pd.to_datetime(df['ColumnName'])
                #forecast_data['Date'].dt.strftime('%Y-%m-%d')
                #forecast_data = forecast_data.to_string(index=False)
                #forecast_data.set_index("Date", inplace=True)
                return render_template("index.html", countries=cargo_countries, forecast_type=forecast_type,
                                       selected_country=selected_country, forecast_periods=forecast_periods,
                                       forecast_data=forecast_data[['Date', 'Forecast']].to_dict('records'),
                               selected_cols_data=selected_cols_filter.to_dict('records'))

        elif forecast_type == "passengers":
            selected_model = passengers_models.get(selected_country)
            selected_cols_filter = plot.filter(items=['Year', selected_country])
            print("My selected country",selected_country)
            print(selected_cols_filter, "My selected dataframe")
            if selected_model:

                # Perform passengers forecasting logic using the selected model
                last_date = datetime.fromtimestamp(df.index[-1])
                forecast_dates = [last_date + timedelta(days=i) for i in range(1, forecast_periods + 1)]
                forecast = selected_model.forecast(steps=forecast_periods)
                user_timezone = timezone("Asia/Singapore")
                forecast_dates = [forecast_date.astimezone(user_timezone) for forecast_date in forecast_dates]
                #forecast_data = pd.DataFrame({"Date": '', "Forecast": forecast})
                forecast_data = pd.DataFrame({'Date': forecast.index, 'Forecast': forecast.values}).reset_index(drop=True)
                forecast_data['Date'] = forecast_data['Date'].dt.strftime('%Y-%m-%d')
                forecast_data['Forecast'] = forecast_data['Forecast'].astype(int)
                #forecast_data = forecast_data.to_string(index=False)
                #forecast_data.set_index("Date", inplace=True)
                return render_template("index.html", countries=passengers_countries, forecast_type=forecast_type,
                                       selected_country=selected_country, forecast_periods=forecast_periods,
                                       forecast_data=forecast_data[['Date', 'Forecast']].to_dict('records'),
                               selected_cols_data=selected_cols_filter.to_dict('records'))

    return render_template("index.html", countries=passengers_countries, forecast_type=forecast_type)
if __name__ == "__main__":
    app.run(debug=True)

#cargo = Forecarst (Tons KG)
#passenger = Forecast (Thousands Pax)