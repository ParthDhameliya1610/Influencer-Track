Influencer Track
-----------------

Project Overview
----------------

In today's digital marketing landscape, brands waste thousands of dollars on influencers who have fake followers or audiences that simply don't care. Influencer Track was built for Crunch Collective (our marketing agency) to solve this exact problem.

We didn't just build a database; we built an intelligent decision-making tool. It connects brands with high-performing creators by analyzing their real engagement, filtering out mismatched niches, preventing double-booking, and tracking live campaign ROI through simulated API webhooks.


Core Features
-------------

1. Secure Authentication & Role Management
2. Tabbed Analytics Dashboard
3. Contextual Influencer Discovery & Brand Fit Score
4. Double-Booking Prevention
5. Campaign Management & KPI Thresholds
6. Dynamic "Live API" Sync
7. Public Agency Portal (Crunch Collective)
8. Comprehensive Database Architecture


Technologies 
-----------

Backend: Python, Flask, Pandas (for data processing)

Database: MySQL (Relational schema, Foreign Keys, Joins)

Frontend: HTML5, CSS3, Bootstrap 5, JavaScript (Fetch API), Chart.js

Version Control: Git & GitHub


Database Architecture
---------------------

ADMIN (System users)

INFLUENCER & CATEGORY (Creator profiles & niches)

PRODUCT (Brands we represent)

CAMPAIGN & CAMPAIGN_INFLUENCER (Campaign management & KPI thresholds)

SOCIAL_MEDIA_ITEM (Live performance metrics)

CONTACT (Outreach history)



How to Run the Project
----------------------

Install Dependencies
---------------------

pip install flask mysql-connector-python pandas werkzeug ( use this command to install)

Setup the Database
------------------

Open MySQL Workbench.
Open the schema.sql file located in the root directory.
Execute the script (⚡) to create the influencer_db database and populate it with initial test data.

Start the Application
---------------------

python app.py



How to add this to GitHub:
--------------------------

1. Open Terminal in the Project Folder

2. Open your project folder (802Project) in VS Code.

3. Create the .gitignore file

Run this command to create the file and open it: 
	notepad .gitignore
	if you are using mac run this: nano .gitignore

When Notepad opens, paste these exact lines and save it


__pycache__/
*.pyc
.vscode/
.env


3. Initialize Git

	git init

4. Add all your files

	git add .

5. Commit your code

	git commit -m "Final Project Influencer Track"

6. Link your GitHub Repository

		Go to GitHub.com in your browser and click New Repository.
		Name it (e.g., Influencer-Track-Project).
		Do NOT check "Add a README file" (you already have one).
		Click Create Repository.
		Copy the URL (it will look like https://github.com/YourUsername/Influencer-Track-Project.git).
		Go back to your VS Code terminal and paste this (replace the URL with your actual URL):

	git remote add origin https://github.com/YourUsername/Influencer-Track-Project.git

7. Push the entire project to GitHub

	git branch -M main
	git push -u origin main


	(If a window pops up asking you to log into GitHub, just click "Sign in with Browser" and authorize it).

Now whole Project will pushed into github

