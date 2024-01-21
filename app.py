# Import necessary libraries
from flask import Flask, render_template, request, redirect, url_for,session,send_from_directory
from bs4 import BeautifulSoup
import requests
import csv
import re
import pandas as pd 
import json 
import json
import os
from flask_login import login_required, logout_user,LoginManager
import PyPDF2

app = Flask(__name__, template_folder='templates')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}  # Add allowed file extensions

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
# Set a secret key
app.config['SECRET_KEY'] = '123'

# Initialize a list to store job data
job_data = []
saved_jobs = []

class InterviewResourceLibrary:
    def __init__(self):
        self.resources = []

    def add_article(self, title, content):
        article = {
            'type': 'article',
            'title': title,
            'content': content,
        }
        self.resources.append(article)

    def add_video(self, title, url):
        video = {
            'type': 'video',
            'title': title,
            'url': url,
        }
        self.resources.append(video)

    def add_checklist(self, title, items):
        checklist = {
            'type': 'checklist',
            'title': title,
            'items': items,
        }
        self.resources.append(checklist)

    def display_resources(self):
        for index, resource in enumerate(self.resources):
            print(f"{index + 1}. {resource['title']} ({resource['type']})")
            if resource['type'] == 'checklist':
                for item in resource['items']:
                    print(f"   - {item}")
            else:
                print(f"   - {resource['content']}" if resource['type'] == 'article' else f"   - Watch at {resource['url']}")
            print("\n")

# Example usage:
library = InterviewResourceLibrary()

library.add_article('Top 10 Interview Questions', "Common interview questions \n "
" Tell me about yourself.Why are you interested in working for this company?Tell me about your education. Why have you chosen this particular field?Describe your best/worst boss.What is your major weakness?")
library.add_video('Interview Tips Video', 'https://www.youtube.com/watch?v=t0u6RgriZRY')
library.add_checklist('Interview Preparation Checklist', ['Research the Company','Practice Common Questions','Dress Appropriately'])

library.display_resources()

# Home page
@app.route('/')
def homepage():
    return render_template('homepage.html')

# Registration form
@app.route('/sign_up')
def registration_form():
    return render_template('sign_up.html')

# Handle registration form submission
@app.route('/submit', methods=['POST'])
def submit_form():
    name = request.form.get('n')
    email = request.form.get('el')
    password = request.form.get('cpsw')
    
    # Save data to a CSV file (you can replace 'registration.csv' with your desired filename)
    with open('registration.csv', mode='a+', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([name, email, password])
    
    return redirect(url_for('login_form'))

# Main page
@app.route('/main')
def main_page():
    return render_template('main.html')

# Login page
@app.route('/login')
def login_form():
    return render_template('login.html')

# Check login credentials
@app.route('/check_login', methods=['POST'])
def check_login():
    username = request.form.get('n')
    password = request.form.get('psw')
    
    # Check the CSV file for the given username and password
    with open('registration.csv', mode='r', newline='') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] == username and row[2] == password: 
                session['username'] = username  # Check username and password
                return redirect(url_for('main_page'))  # Redirect to job listings after successful login
    
    return redirect(url_for('login_form'))


def scrape_jobs():
    try:
        from bs4 import BeautifulSoup
        import requests

        response1 = requests.get("https://www.freshersworld.com/jobs?src=homeheader")
        page = response1.text

        # Parse the HTML content
        soup = BeautifulSoup(page, "html.parser")

        # Find all span elements with class "wrap-title seo_title"
        job_tags = soup.find_all(name="span", class_="wrap-title seo_title")

        education_tags = soup.find_all(name="span", class_="bold_elig")

        # Find all elements with class "loctext"
        location_tags = soup.find_all(name="span", class_="job-location display-block modal-open job-details-span")

        experieince_tags = soup.find_all(name="span", class_="experience job-details-span")

        url_tag=soup.find_all(name="div",class_="col-md-12 col-lg-12 col-xs-12 padding-none job-container jobs-on-hover top_space", id="all-jobs-append")

        # Initialize a list to store the scraped job data
        job_data = []

        # Determine the minimum length among the tag lists
        min_length = min(len(job_tags), len(education_tags), len(experieince_tags), len(location_tags))

        for i in range(min_length):
            job_title = job_tags[i].get_text() if job_tags and job_tags[i] else "N/A"
            education_criteria = education_tags[i].get_text() if education_tags and education_tags[i] else "N/A"
            experience = experieince_tags[i].get_text() if experieince_tags and experieince_tags[i] else "N/A"

            location_tag = location_tags[i] if location_tags else None
            location = "N/A"
            if location_tag:
                parent = location_tag.find_parent()
                bold_font = parent.find(class_="bold_font")
                if bold_font:
                    location = bold_font.get_text()
            url_job=url_tag[i].get_text()

            job_data.append({
                'title': job_title,
                'education': education_criteria,
                'experience': experience,
                'location': location,
                'url':url_job
            })

        with open('job.json', 'w') as json_file:
            json.dump(job_data, json_file)

        return job_data

    except requests.exceptions.RequestException as e:
        # Handle network-related errors
        print("Request Exception:", e)
        return []

    except Exception as e:
        # Handle other exceptions
        print("An error occurred:", e)
        return []
    
@app.route('/job_details')
def detail_job():
    try:
        # from bs4 import BeautifulSoup
        # import requests

        # response1 = requests.get("https://www.freshersworld.com/jobs?src=homeheader")
        # page = response1.text

        # # Parse the HTML content
        # soup = BeautifulSoup(page, "html.parser")

        # listing = soup.find_all(class_="col-md-12 col-lg-12 col-xs-12 padding-none job-container jobs-on-hover top_space", id="all-jobs-append")
        
        # # urls = []
        
        # job_details = []
        # for a in listing:
        #     job_display_url = a['job_display_url']
        #     response2 = requests.get(job_display_url)
        #     page2 = response2.text
        #     soup2 = BeautifulSoup(page2, "html.parser")
            
        #     detail = soup2.find_all(name="div", class_="jobs_contents")
            
        #     for i in detail:
        #         text_content = i.get_text()
        #         # urls.append(text_content)
        #         job_details.append(text_content)

        # result = '\n'.join(job_details[0])

        # return result
        from bs4 import BeautifulSoup
        import requests

        response1 = requests.get("https://www.freshersworld.com/jobs?src=homeheader")
        page = response1.text

        # Parse the HTML content
        soup = BeautifulSoup(page, "html.parser")

        listing = soup.find(class_="col-md-12 col-lg-12 col-xs-12 padding-none job-container jobs-on-hover top_space",
                                id="all-jobs-append")

        job_display_url = listing['job_display_url']
        response2 = requests.get(job_display_url)
        page2 = response2.text
        soup2 = BeautifulSoup(page2, "html.parser")
        # print(1)
        job_details = []
        ul = soup2.find('ul')
        if ul:
            start_value = int(ul.get('start', '1'))
            job_details.append('<h2>Job Description:</h2>')

            for li in ul.find_all('li'):
                job_details.append(f'<p>{start_value}. {li.text}</p>')
                start_value += 1
        job_details.append('<a href="/apply_job" class="btn btn-primary">Apply Now</a>')
        result = '\n'.join(job_details)
        return result
        

    
    except requests.exceptions.RequestException as e:
        # Handle network-related errors
        print("Request Exception:", e)
        return []

    except Exception as e:
        # Handle other exceptions
        print("An error occurred:", e)
        return []
    
@app.route('/apply_job')
def apply():
        from bs4 import BeautifulSoup
        import requests

        response1 = requests.get("https://www.freshersworld.com/jobs?src=homeheader")
        page = response1.text

        # Parse the HTML content
        soup = BeautifulSoup(page, "html.parser")

        listing = soup.find(class_="col-md-12 col-lg-12 col-xs-12 padding-none job-container jobs-on-hover top_space",
                                id="all-jobs-append")

        job_display_url = listing['job_display_url']
        response2 = requests.get(job_display_url)
        page2 = response2.text
        soup2 = BeautifulSoup(page2, "html.parser")
        # print(1)
        job_details = []
        ul = soup2.find('ul')
        if ul:
            start_value = int(ul.get('start', '1'))
            job_details.append('<h2>Job Description:</h2>')

            for li in ul.find_all('li'):
                job_details.append(f'<p>{start_value}. {li.text}</p>')
                start_value += 1
        result = '\n'.join(job_details)
        return render_template('apply.html', result=result)

@app.route('/save_job', methods=['POST'])
def save_job():
    title = request.form.get('title')
    education=request.form.get('education')
    experience=request.form.get('experience')
    location = request.form.get('location')

    json_file = 'saved_jobs.json'

# Open the file in a context manager to ensure it's properly closed
    with open(json_file, mode='r+') as file:
    # Load existing data, if any
        try:
            data = json.load(file)
        except json.decoder.JSONDecodeError:
            data = []

    # Append the new job data
    data.append({'title': title, 'education': education, 'experience': experience, 'location': location})

# Write the updated data back to the JSON file (outside the 'with' block)
    with open(json_file, mode='w') as file:
        json.dump(data, file, indent=4)

    return redirect(url_for('job_listings'))


@app.route('/job_listings')
def job_listings():
    global job_data  

    # Check if job_data is empty, if so, scrape the data
    if not job_data:
        job_data = scrape_jobs()

    return render_template('index.html', job_data=job_data)


@app.route('/saved')
def saved():
    json_file = 'saved_jobs.json'
    try:
        with open(json_file, 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        data = []  # If the file doesn't exist or is empty

    return render_template('saved_jobs.html', jobs=data)

@app.route('/remove_job/<int:index>', methods=['POST'])
def remove_job(index):
    json_file = 'saved_jobs.json'
    try:
        with open(json_file, 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        data = []  # If the file doesn't exist or is empty
   
    if 0 <= index < len(data):
        removed_job = data.pop(index)
        with open(json_file, 'w') as file:
            json.dump(data, file)

    return redirect(url_for('saved'))

@app.route('/search', methods=['POST'])
def search_jobs():
    global job_data  # Declare job_data as a global variable

    search_query = request.form.get('search_query')

    if search_query:
        search_query = search_query.lower()  # Convert to lowercase for case-insensitive search

       
        if not job_data:
            job_data = scrape_jobs()

        # Filter jobs that have an exact match with the search query in any field
        search_results = [job for job in job_data if
                          search_query in job['title'].lower() or
                          search_query in job['education'].lower() or
                          search_query in job['experience'].lower() or
                          search_query in job['location'].lower()]

    else:
        search_results = []  

    return render_template('search_job.html', search_results=search_results)

def secure_filename(filename):
    # Remove any path information and keep only the filename
    filename = os.path.basename(filename)
    
    # Replace any non-alphanumeric characters with underscores
    filename = re.sub(r"[^a-zA-Z0-9.]", "_", filename)
    
    return filename

@app.route('/profile')
def profile():
    if 'username' in session:
        username = session['username']
        email = get_email_for_username(username)  # Function to retrieve the email

        if email:
            return render_template('profile.html', username=username, email=email)
        else:
            return 'Email not found for the user.'
    else:
        return 'Not logged in'

# Function to retrieve the email for a given username
def get_email_for_username(username):
    with open('registration.csv', mode='r', newline='') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] == username:
                return row[1]  # Email is in the second column (index 1) in the CSV
    return None  # Return None if email is not found
# Initialize the LoginManager


login_manager = LoginManager()
login_manager.init_app(app)

# Set the login view (the view that users are redirected to when they need to log in)
login_manager.login_view = '/login'  # Replace 'login' with the name of your login route

import csv

@login_manager.user_loader
def load_user(user_id):
    # Open the CSV file for reading
    with open('registration.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        
        # Search for a user with a matching username (user_id)
        for row in reader:
            if row['username'] == user_id:
                # You can create a User object or return the user data as a dictionary
                # Example: return User(username=row['username'], email=row['email'])
                return row

    # Return None if the user does not exist
    return None

# Logout route
@app.route('/signout')
@login_required
def signout():
    logout_user()
    return redirect(url_for('homepage'))



@app.route('/upload_profile_pic', methods=['POST'])
def upload_profile_pic():
    if 'profile_pic' in request.files:
        profile_pic = request.files['profile_pic']
        if profile_pic.filename != '' and allowed_file(profile_pic.filename):
            filename = secure_filename(profile_pic.filename)
            profile_pic.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('profile'))
    return "Invalid file or upload failed."

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/upload_resume', methods=['POST'])
def upload_resume():
    if 'resume' in request.files:
        resume = request.files['resume']
    if resume.filename != '':
        filename = secure_filename(resume.filename)
        resume.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
    return render_template('main.html')

@app.route('/display_profile')
def display():
    return redirect(url_for('display_profile_pic.html'))

recommended_job_data = []


def generate_recommended_jobs():
    # Open the PDF file
    with open("uploads/resume.pdf", 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)  # Use PdfFileReader instead of PdfReader
    
    # Extract text from all pages
        text = ""
        for page in pdf_reader.pages:  # Loop through pages directly
            text += page.extract_text()


    # Initialize a list to store recommended job listings
    recommended_jobs = []

    # Load job listings from job.json
    with open('job.json', 'r') as job_file:
        job_listings = json.load(job_file)

    # Match job_keywords with the extracted text and store in resume_keywords
    resume_keywords = []
    job_keywords = ["QA", "Content", "Full Stack", "Fullstack", "C", "Android", "Java", "Software", "Front-End",
                    "Technical", "Application", "Medical", "Customer", "Automation", "Business", "Finance"]

    for keyword in job_keywords:
        if keyword in text:
            resume_keywords.append(keyword)

    # Loop through the job listings and check if any keywords from `resume_keywords` are present in the job title
    for job in job_listings:
        title = job["title"]
        for keyword in resume_keywords:
            if keyword.lower() in title.lower():
                recommended_jobs.append(job)

    # Define the JSON file path to save recommended jobs
    json_file_path = 'recommended_jobs.json'

    # Save the recommended jobs to the JSON file
    if recommended_jobs:
        with open(json_file_path, 'w', encoding='utf-8') as json_file:
            json.dump(recommended_jobs, json_file, indent=4)

        print(f"Recommended jobs have been saved to {json_file_path}.")
    else:
        print("No recommended jobs found.")

    num_jobs = len(recommended_jobs)

    print(f"Number of recommended jobs in {json_file_path}: {num_jobs}")

    return recommended_jobs

# Example usage:
# recommended_job_data = generate_recommended_jobs('uploads/resume.pdf')

# Your existing code for scraping recommended jobs, extracting text from resumes, and matching keywords should be placed here

@app.route('/recommended_job_list')
def recommended_job_list():
    global recommended_job_data

    # Check if recommended_job_data is empty, if so, generate the recommended job data
    if not recommended_job_data:
        recommended_job_data = generate_recommended_jobs()  # Replace with your recommended job generation logic

    return render_template('recommended_job.html', recommended_job_data=recommended_job_data)

@app.route('/job_help')
def help():
    return render_template('interview_help.html', resources=library.resources)

if __name__ == '__main__':
    app.run(debug=True)
