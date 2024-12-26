from django.shortcuts import render,redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import pandas as pd
import joblib
from keras.models import load_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login as auth_login
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

import matplotlib.pyplot as plt
import io
import base64
from django.conf import settings
import os
dir = os.path.join(settings.BASE_DIR , 'predict')
# Load the model and preprocessor

model1 = load_model(os.path.join('predict','tomato_ann.h5'))
preprocessor = joblib.load(os.path.join('predict','tomato.pkl'))
model2 = load_model(os.path.join('predict','coconut_ann.h5'))
preprocessor2 = joblib.load(os.path.join('predict','coconut.pkl'))
model3 = load_model(os.path.join('predict','arecanut_ann.h5'))
preprocessor3 = joblib.load(os.path.join('predict','arecanut.pkl'))
model4=load_model(os.path.join('predict','onion_ann.h5'))
preprocessor4 = joblib.load(os.path.join('predict','onion.pkl'))
def get_prices_from_website(url,flag):
    f=flag

    try:
        # Send a request to the website
        response = requests.get(url)
        response.raise_for_status()  # Check for request errors

        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the relevant section in the HTML
        price_section = soup.find('div', {'class': 'mandhi-highlight-details'})

        # Check if price_section is found
        if price_section is None:
            raise ValueError("Could not find the price section in the HTML.")

        # Extract the text from the section
        price_text = price_section.get_text(strip=True)
        print(f"Extracted Text: {price_text}")  # Debug print

        # Use regular expressions to extract only the numeric values of the prices
        min_price_match = re.search(r'lowest market price is₹(\d+)/Quintal', price_text)
        max_price_match = re.search(r'costliest market price is₹(\d+)/Quintal', price_text)

        if min_price_match and max_price_match:
            min_price = min_price_match.group(1)
            max_price = max_price_match.group(1)
        else:
            raise ValueError("Could not find the price data in the text.")
        if f==1:
            return min_price
        else:
            
            return max_price

    except requests.RequestException as e:
        print(f"HTTP request failed: {e}")
        return None, None
    except ValueError as e:
        print(f"Value error: {e}")
        return None, None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None, None

def land(request):
     return render(request,'landing.html')
def home(request):
    return render(request,'home.html')
    

import io
import base64
import pandas as pd
import matplotlib.pyplot as plt
from django.shortcuts import render
from django.http import JsonResponse

def get_prices_from_website(url):
    try:
        # Send a request to the website
        response = requests.get(url)
        response.raise_for_status()  # Check for request errors

        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the relevant section in the HTML
        price_section = soup.find('div', {'class': 'mandhi-highlight-details'})

        # Check if price_section is found
        if price_section is None:
            raise ValueError("Could not find the price section in the HTML.")

        # Extract the text from the section
        price_text = price_section.get_text(strip=True)
        print(f"Extracted Text: {price_text}")  # Debug print

        # Use regular expressions to extract only the numeric values of the prices
        min_price_match = re.search(r'lowest market price is₹(\d+)/Quintal', price_text)
        max_price_match = re.search(r'costliest market price is₹(\d+)/Quintal', price_text)

        if min_price_match and max_price_match:
            min_price = float(min_price_match.group(1))
            max_price = float(max_price_match.group(1))
            return min_price, max_price
        else:
            raise ValueError("Could not find the price data in the text.")

    except requests.RequestException as e:
        print(f"HTTP request failed: {e}")
        return None, None
    except ValueError as e:
        print(f"Value error: {e}")
        return None, None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None, None
    
def predict_modal_price(request):
    predicted_modal_prices = {}
    market_names = ["Udupi", "Kolar", "Bangarpet", "Chickkaballapura", "Chintamani", "Gowribidanoor", "Mangalore"]

    urls = {
        "Udupi": "https://www.commodityonline.com/mandiprices/tomato/karnataka/udupi",
        "Kolar": "https://www.commodityonline.com/mandiprices/tomato/karnataka/kolar",
        "Bangarpet": "https://www.commodityonline.com/mandiprices/tomato/karnataka/bangarpet",
        "Chickkaballapura": "https://www.commodityonline.com/mandiprices/tomato/karnataka/chickkaballapura",
        "Chintamani": "https://www.commodityonline.com/mandiprices/tomato/karnataka/chintamani",
        "Gowribidanoor": "https://www.commodityonline.com/mandiprices/tomato/karnataka/gowribidanoor",
        "Mangalore": "https://www.commodityonline.com/mandiprices/tomato/karnataka/mangalore"
    }

    if request.method == 'POST':
        try:
            year = int(request.POST['year'])
            month = int(request.POST['month'])
            day = int(request.POST['day'])

            for market_name in market_names:
                url = urls[market_name]
                min_price, max_price = get_prices_from_website(url)

                # Default values if prices could not be fetched
                if min_price is None:
                    min_price = 0
                if max_price is None:
                    max_price = 0

                example_input = pd.DataFrame({
                    'Market Name': [market_name],
                    'Year': [year],
                    'Month': [month],
                    'Day': [day],
                    'Min Price (Rs./Quintal)': [min_price],
                    'Max Price (Rs./Quintal)': [max_price],
                })

                # Ensure the input data types are correct
                numerical_features = ['Year', 'Month', 'Day', 'Min Price (Rs./Quintal)', 'Max Price (Rs./Quintal)']
                categorical_features = ['Market Name']

                for col in numerical_features:
                    example_input[col] = example_input[col].astype(float)

                for col in categorical_features:
                    example_input[col] = example_input[col].astype(str)

                # Transform the new input using the preprocessor
                example_input_transformed = preprocessor.transform(example_input)

                # Predict the modal price using the trained model
                predicted_modal_price = model1.predict(example_input_transformed)[0][0]
                predicted_modal_prices[market_name] = predicted_modal_price

            # Generate the plot
            fig, ax = plt.subplots()
            market_names_list = list(predicted_modal_prices.keys())
            predicted_prices_list = list(predicted_modal_prices.values())
            ax.bar(market_names_list, predicted_prices_list, color='#66B2FF')  # Change color to #66B2FF
            ax.set_xlabel('Market Name')
            ax.set_ylabel('Predicted Modal Price (Rs./Quintal)')
            ax.set_title('Predicted Modal Prices for Tomato')

            # Rotate the x-axis labels
            plt.xticks(rotation=45, ha='right')

            # Convert the plot to an image and encode it as a base64 string
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            image_base64 = base64.b64encode(buf.read()).decode('utf-8')
            buf.close()

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return render(request, 'predict_price.html', {
        'predicted_modal_prices': predicted_modal_prices,
        'chart': image_base64 if 'image_base64' in locals() else None
    })
    
def coconut(request):
    predicted_modal_prices = {}
    market_names = ["Udupi", "Kundapura", "Puttur", "Mangalore", "Sulya", "Bantwala"]

    urls = {
        "Udupi": "https://www.commodityonline.com/mandiprices/coconut/karnataka/udupi",
        "Kundapura": "https://www.commodityonline.com/mandiprices/coconut/karnataka/kundapura",
        "Puttur": "https://www.commodityonline.com/mandiprices/coconut/karnataka/puttur",
        "Mangalore": "https://www.commodityonline.com/mandiprices/coconut/karnataka/mangalore",
        "Belthangdi": "https://www.commodityonline.com/mandiprices/coconut/karnataka/belthangdi",
        "Karkala": "https://www.commodityonline.com/mandiprices/coconut/karnataka/karkala",
        "Sulya": "https://www.commodityonline.com/mandiprices/coconut/karnataka/sulya",
        "Bantwala": "https://www.commodityonline.com/mandiprices/coconut/karnataka/bantwala"
    }

    if request.method == 'POST':
        try:
            year = int(request.POST['year'])
            month = int(request.POST['month'])
            day = int(request.POST['day'])

            for market_name in market_names:
                url = urls[market_name]
                min_price, max_price = get_prices_from_website(url)

                # Default values if prices could not be fetched
                if min_price is None:
                    min_price = 0
                if max_price is None:
                    max_price = 0

                example_input = pd.DataFrame({
                    'Market Name': [market_name],
                    'Year': [year],
                    'Month': [month],
                    'Day': [day],
                    'Min Price (Rs./Quintal)': [min_price],
                    'Max Price (Rs./Quintal)': [max_price],
                })

                # Ensure the input data types are correct
                numerical_features = ['Year', 'Month', 'Day', 'Min Price (Rs./Quintal)', 'Max Price (Rs./Quintal)']
                categorical_features = ['Market Name']

                for col in numerical_features:
                    example_input[col] = example_input[col].astype(float)

                for col in categorical_features:
                    example_input[col] = example_input[col].astype(str)

                # Transform the new input using the preprocessor
                example_input_transformed = preprocessor2.transform(example_input)

                # Predict the modal price using the trained model
                predicted_modal_price = model2.predict(example_input_transformed)[0][0]
                predicted_modal_prices[market_name] = predicted_modal_price

            # Generate the plot
            fig, ax = plt.subplots()
            market_names_list = list(predicted_modal_prices.keys())
            predicted_prices_list = list(predicted_modal_prices.values())
            ax.bar(market_names_list, predicted_prices_list, color='#66B2FF')  # Change color to #66B2FF
            ax.set_xlabel('Market Name')
            ax.set_ylabel('Predicted Modal Price (Rs./Quintal)')
            ax.set_title('Predicted Modal Prices for Coconut')

            # Rotate the x-axis labels
            plt.xticks(rotation=45, ha='right')

            # Convert the plot to an image and encode it as a base64 string
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            image_base64 = base64.b64encode(buf.read()).decode('utf-8')
            buf.close()

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return render(request, 'coconut.html', {
        'predicted_modal_prices': predicted_modal_prices,
        'chart': image_base64 if 'image_base64' in locals() else None
    })

def onion(request):
    predicted_modal_prices = {}
    market_names = ["Udupi", "Davangere", "Belgaum", "Gadag", "Bijapur", "Mangalore"]

    urls = {
        "Udupi": "https://www.commodityonline.com/mandiprices/onion/karnataka/udupi",
        "Davangere": "https://www.commodityonline.com/mandiprices/onion/karnataka/davangere",
        "Belgaum": "https://commodityonline.com/mandiprices/onion/karnataka/belgaum",
        "Gadag": "https://www.commodityonline.com/mandiprices/onion/karnataka/gadag",
        "Bijapur": "https://www.commodityonline.com/mandiprices/onion/karnataka/bijapur",
        "Kundapura": "https://www.commodityonline.com/mandiprices/onion/karnataka/kundapura",
        "Mangalore": "https://www.commodityonline.com/mandiprices/onion/karnataka/mangalore"
    }

    if request.method == 'POST':
        try:
            year = int(request.POST['year'])
            month = int(request.POST['month'])
            day = int(request.POST['day'])

            for market_name in market_names:
                url = urls[market_name]
                min_price, max_price = get_prices_from_website(url)

                # Default values if prices could not be fetched
                if min_price is None:
                    min_price = 0
                if max_price is None:
                    max_price = 0

                example_input = pd.DataFrame({
                    'Market Name': [market_name],
                    'Year': [year],
                    'Month': [month],
                    'Day': [day],
                    'Min Price (Rs./Quintal)': [min_price],
                    'Max Price (Rs./Quintal)': [max_price],
                })


                # Ensure the input data types are correct
                numerical_features = ['Year', 'Month', 'Day', 'Min Price (Rs./Quintal)', 'Max Price (Rs./Quintal)']
                categorical_features = ['Market Name']

                for col in numerical_features:
                    example_input[col] = example_input[col].astype(float)

                for col in categorical_features:
                    example_input[col] = example_input[col].astype(str)

                # Transform the new input using the preprocessor
                example_input_transformed = preprocessor4.transform(example_input)

                # Predict the modal price using the trained model
                predicted_modal_price = model4.predict(example_input_transformed)[0][0]
                predicted_modal_prices[market_name] = predicted_modal_price

            # Generate the plot
            fig, ax = plt.subplots()
            market_names_list = list(predicted_modal_prices.keys())
            predicted_prices_list = list(predicted_modal_prices.values())
            ax.bar(market_names_list, predicted_prices_list, color='#66B2FF')  # Change color to #66B2FF
            ax.set_xlabel('Market Name')
            ax.set_ylabel('Predicted Modal Price (Rs./Quintal)')
            ax.set_title('Predicted Modal Prices for Onion')

            # Rotate the x-axis labels
            plt.xticks(rotation=45, ha='right')

            # Convert the plot to an image and encode it as a base64 string
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            image_base64 = base64.b64encode(buf.read()).decode('utf-8')
            buf.close()

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return render(request, 'onion.html', {
        'predicted_modal_prices': predicted_modal_prices,
        'chart': image_base64 if 'image_base64' in locals() else None
    })


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            
            auth_login(request, form.instance)
            return redirect('home')  
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            return redirect('home')  
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def arecanut(request):
    predicted_modal_prices = {}
    market_names = ["Kundapura", "Puttur", "Mangalore", "Sulya", "Belthangdi","Karkala","Bantwala"]

    urls = {
        
        "Kundapura": "https://www.commodityonline.com/mandiprices/arecanut-betelnutsupari/karnataka/kundapura",
        "Puttur": "https://www.commodityonline.com/mandiprices/arecanut-betelnutsupari/karnataka/puttur",
        "Mangalore": "https://www.commodityonline.com/mandiprices/arecanut-betelnutsupari/karnataka/mangalore",
        "Belthangdi": "https://www.commodityonline.com/mandiprices/arecanut-betelnutsupari/karnataka/belthangdi",
        "Karkala": "https://www.commodityonline.com/mandiprices/arecanut-betelnutsupari/karnataka/karkala",
        "Sulya": "https://www.commodityonline.com/mandiprices/arecanut-betelnutsupari/karnataka/sulya",
        "Bantwala": "https://www.commodityonline.com/mandiprices/arecanut-betelnutsupari/karnataka/bantwala"
    }

    if request.method == 'POST':
        try:
            year = int(request.POST['year'])
            month = int(request.POST['month'])
            day = int(request.POST['day'])

            for market_name in market_names:
                url = urls[market_name]
                min_price, max_price = get_prices_from_website(url)

                # Default values if prices could not be fetched
                if min_price is None:
                    min_price = 0
                if max_price is None:
                    max_price = 0

                example_input = pd.DataFrame({
                    'Market Name': [market_name],
                    'Year': [year],
                    'Month': [month],
                    'Day': [day],
                    'Min Price (Rs./Quintal)': [min_price],
                    'Max Price (Rs./Quintal)': [max_price],
                })

                # Ensure the input data types are correct
                numerical_features = ['Year', 'Month', 'Day', 'Min Price (Rs./Quintal)', 'Max Price (Rs./Quintal)']
                categorical_features = ['Market Name']

                for col in numerical_features:
                    example_input[col] = example_input[col].astype(float)

                for col in categorical_features:
                    example_input[col] = example_input[col].astype(str)

                # Transform the new input using the preprocessor
                example_input_transformed = preprocessor3.transform(example_input)

                # Predict the modal price using the trained model
                predicted_modal_price = model3.predict(example_input_transformed)[0][0]
                predicted_modal_prices[market_name] = predicted_modal_price

            # Generate the plot
            fig, ax = plt.subplots()
            market_names_list = list(predicted_modal_prices.keys())
            predicted_prices_list = list(predicted_modal_prices.values())
            ax.bar(market_names_list, predicted_prices_list, color='#66B2FF')  # Change color to #66B2FF
            ax.set_xlabel('Market Name')
            ax.set_ylabel('Predicted Modal Price (Rs./Quintal)')
            ax.set_title('Predicted Modal Prices for Arecanut')

            # Rotate the x-axis labels
            plt.xticks(rotation=45, ha='right')

            # Convert the plot to an image and encode it as a base64 string
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            image_base64 = base64.b64encode(buf.read()).decode('utf-8')
            buf.close()

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return render(request, 'arecanut.html', {
        'predicted_modal_prices': predicted_modal_prices,
        'chart': image_base64 if 'image_base64' in locals() else None
    })
