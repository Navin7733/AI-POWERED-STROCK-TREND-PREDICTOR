from django.shortcuts import render
from .forms import UploadCSVForm
import pandas as pd
import os
from dotenv import load_dotenv
from openai import OpenAI  # Notice: imported as a class, not a module

#from .mongo_utils import save_analysis, get_recent_analyses #mongodb code line


from .models import UserData
from django.http import HttpResponse


#new
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect
from .forms import RegisterForm
#new

#new
from django.contrib.auth.decorators import login_required




# Load .env file
load_dotenv()

# Initialize OpenRouter client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

def predict_stock_trends(csv_data):
    prompt = f"Analyze the following stock market data and predict the future trend:\n\n{csv_data}\n\nPrediction:"

    try:
        completion = client.chat.completions.create(
            model="deepseek/deepseek-chat",
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            extra_headers={
                "HTTP-Referer": "http://127.0.0.1:8000/",  # optional
                "X-Title": "StockPredictor",               # optional
            },
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {str(e)}"
    
#new
from django.contrib.auth.decorators import login_required

@login_required
def upload_file(request):
    '''#new
    # Force logout if session is old
    if not request.session.get('visited'):
        logout(request)
        return redirect('login')

    request.session['visited'] = True  # Mark session as active
    #new
    '''

    if request.method == 'POST':
        form = UploadCSVForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['file']
            df = pd.read_csv(csv_file)
            csv_data = df.to_string(index=False)

            # Get prediction using OpenRouter + DeepSeek
            prediction = predict_stock_trends(csv_data)

            return render(request, 'result.html', {
                'csv_data': csv_data,
                'prediction': prediction
            })
    else:
        form = UploadCSVForm()

    return render(request, 'upload.html', {'form': form})

                #mongoDB code :

'''def analyze_stock(request):
    if request.method == 'POST':
        symbol = request.POST.get('symbol')
        prompt = request.POST.get('prompt')
        # Combine symbol and prompt for analysis
        combined_prompt = f"Stock symbol: {symbol}\nPrompt: {prompt}"
        ai_response = predict_stock_trends(combined_prompt)

        # Save to MongoDB
        save_analysis(symbol, prompt, ai_response)

        return render(request, 'result.html', {
            'response': ai_response,
            'recent': get_recent_analyses()
        })

    return render(request, 'analyze.html')
    '''

def test_mongo_connection(request):
    try:
        # Attempt to count documents in the collection
        count = UserData.objects.count()
        return HttpResponse(f"✅ MongoDB is connected! {count} records found.")
    except Exception as e:
        return HttpResponse(f"❌ MongoDB connection failed: {str(e)}")
    
#new
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('upload_file')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('upload_file')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')
#new

