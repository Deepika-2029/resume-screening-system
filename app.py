from flask import Flask, render_template, request, jsonify, session, redirect, url_for, make_response
import os
import json
from datetime import datetime
import PyPDF2
import re
import csv
from io import StringIO
import socket
# ========== STEP 1: EMAIL IMPORTS ADD KARO ==========
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
app.static_folder = 'static'
app.secret_key = os.environ.get('SECRET_KEY', 'resume_screening_2026_super_secret_key_12345')
app.config['PERMANENT_SESSION_LIFETIME'] = __import__('datetime').timedelta(days=7)

# ========== FOLDERS SETUP ==========
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ========== JSON DATABASES ==========
APPLICANTS_FILE = 'applicants.json'
COMPANIES_FILE = 'companies.json'
ADMIN_FILE = 'admin.json'

# Create admin credentials
if not os.path.exists(ADMIN_FILE):
    with open(ADMIN_FILE, 'w') as f:
        json.dump({
            "username": "admin",
            "password": "admin123",
            "email": "admin@resumeai.com"
        }, f)

# Create companies database if not exists
if not os.path.exists(COMPANIES_FILE):
    with open(COMPANIES_FILE, 'w') as f:
        json.dump([], f)

# Create applicants database if not exists
if not os.path.exists(APPLICANTS_FILE):
    with open(APPLICANTS_FILE, 'w') as f:
        json.dump([], f)
        print(f"✅ Created {APPLICANTS_FILE}")

# ========== COMPANY DATABASE 2026 ==========
COMPANY_DATA = [
    {
        "id": 1, "name": "Google", "logo": "G", "industry": "AI/ML, Cloud, Search",
        "skills": ["Python", "C++", "Java", "TensorFlow", "PyTorch", "Kubernetes", "System Design", "DSA", "Distributed Systems"],
        "salary": "₹30-80 LPA", "role": "Software Engineer, AI/ML", "batch": "2026", "last_date": "2026-03-30"
    },
    {
        "id": 2, "name": "Microsoft", "logo": "MS", "industry": "Cloud, AI, Enterprise",
        "skills": ["C#", "Python", "Azure", "SQL", "Power BI", ".NET Core", "System Design", "DSA", "Data Governance"],
        "salary": "₹30-80 LPA", "role": "SDE, Technology Consulting", "batch": "2026", "last_date": "2026-04-15"
    },
    {
        "id": 3, "name": "Amazon", "logo": "AMZ", "industry": "E-commerce, Cloud",
        "skills": ["Java", "C++", "Python", "AWS", "Distributed Systems", "DSA", "System Design", "OOPs"],
        "salary": "₹30-70 LPA", "role": "SDE", "batch": "2026", "last_date": "2026-03-25"
    },
    {
        "id": 4, "name": "TCS", "logo": "TCS", "industry": "IT Services, Consulting",
        "skills": ["Java", "Python", "SQL", "Spring Boot", "AWS", "DSA", "OOPs", "DBMS", "Operating Systems"],
        "salary": "₹4-9 LPA", "role": "Ninja/Digital", "batch": "2026", "last_date": "2026-04-10"
    },
    {
        "id": 5, "name": "Infosys", "logo": "INFY", "industry": "IT Services, Digital",
        "skills": ["Python", "Java", "Spring", "AWS", "Azure", "SQL", "DSA", "AI/ML Basics", "Cloud Computing"],
        "salary": "₹6.25-21 LPA", "role": "Specialist Programmer", "batch": "2026", "last_date": "2026-04-05"
    },
    {
        "id": 6, "name": "Thoughtworks", "logo": "TW", "industry": "Technology Consulting",
        "skills": ["C#", "Java", "Python", "TDD", "CI/CD", "Docker", "Microservices", "Pair Programming", "Agile"],
        "salary": "₹12-25 LPA", "role": "Associate Graduate Developer", "batch": "2026", "last_date": "2026-03-28"
    },
    {
        "id": 7, "name": "Meta", "logo": "M", "industry": "Social Media, AI",
        "skills": ["Python", "C++", "React", "PyTorch", "System Design", "DSA", "Distributed Systems"],
        "salary": "₹35-85 LPA", "role": "Software Engineer", "batch": "2026", "last_date": "2026-04-20"
    },
    {
        "id": 8, "name": "Apple", "logo": "APL", "industry": "Hardware, Software",
        "skills": ["Swift", "C++", "Python", "iOS", "macOS", "System Design", "DSA"],
        "salary": "₹35-75 LPA", "role": "Software Engineer", "batch": "2026", "last_date": "2026-04-18"
    },
    {
        "id": 9, "name": "Salesforce", "logo": "SF", "industry": "CRM, Cloud",
        "skills": ["Apex", "Java", "JavaScript", "SQL", "Cloud Computing", "Lightning", "DSA"],
        "salary": "₹20-45 LPA", "role": "Associate Technical Consultant", "batch": "2026", "last_date": "2026-03-31"
    },
    {
        "id": 10, "name": "Adobe", "logo": "ADB", "industry": "Creative Software",
        "skills": ["JavaScript", "C++", "Python", "React", "Node.js", "Cloud", "DSA"],
        "salary": "₹25-50 LPA", "role": "Software Engineer", "batch": "2026", "last_date": "2026-04-12"
    }
]

# ========== STEP 2: EMAIL SEND FUNCTION ==========
# Email credentials - set as environment variables on hosting
SENDER_EMAIL = os.environ.get('SENDER_EMAIL', 'mohitnjatt1122@gmail.com')
SENDER_PASSWORD = os.environ.get('SENDER_PASSWORD', 'nvkn lbrt hxqx umqx')

def send_status_email(applicant, status):
    """Candidate ko status update ki email bhejo"""
    try:
        # Email content based on status
        if status == "Shortlisted":
            subject = f"🎉 Congratulations! Shortlisted for {applicant['company']} 2026"
            body = f"""
            Dear {applicant['name']},
            
            CONGRATULATIONS! 🎉
            
            You have been SHORTLISTED for {applicant['company']} (Batch 2026).
            
           
            📊 YOUR APPLICATION SUMMARY:
            
            🏢 Company    : {applicant['company']}
            📈 Match Score: {applicant['score']}%
            ✅ Skills Matched: {', '.join(applicant['matched_skills'][:5])}
            🎓 Qualification: {applicant['qualification']}
            
            ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            🎯 NEXT STEPS:
            ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            📌 Interview details will be sent within 48 hours.
            📌 Keep checking your email.
            
            Best regards,
            {applicant['company']} Recruitment Team
            AI Resume Screening System
            """
            
        elif status == "Selected":
            subject = f"🎉🎉 SELECTED! You're hired by {applicant['company']}!"
            body = f"""
            Dear {applicant['name']},
            
            🎉🎉🎉 WOW! Congratulations! 🎉🎉🎉
            
            You have been SELECTED for {applicant['company']}!
            
          
            📊 YOUR ACHIEVEMENT:
            
            🏢 Company    : {applicant['company']}
            📈 Match Score: {applicant['score']}%
            ✅ Skills: {', '.join(applicant['matched_skills'][:5])}
            
           
            📧 Offer letter will be sent to your email soon!
            
            Best regards,
            {applicant['company']} Recruitment Team
            """
            
        elif status == "Rejected":
            subject = f"Update regarding {applicant['company']} Application"
            body = f"""
            Dear {applicant['name']},
            
            Thank you for applying to {applicant['company']}.
            
           
            📊 APPLICATION STATUS:
            
            🏢 Company    : {applicant['company']}
            📈 Match Score: {applicant['score']}%
            ❌ Status     : Not Selected this time
            
            We encourage you to apply again in future.
            Keep improving your skills!
            
            Best regards,
            {applicant['company']} Recruitment Team
            """
        else:
            return False  # Unknown status
        
        # Create email
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = applicant['email']
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        print(f"✅ Email sent to {applicant['email']} for {status}")
        return True
        
    except Exception as e:
        print(f"❌ Email Error: {e}")
        return False

# ========== HOME PAGE ==========
@app.route('/')
def home():
    return render_template('index.html')

# ========== APPLY PAGE ==========
@app.route('/apply')
def apply():
    company = request.args.get('company', '')
    return render_template('apply.html', company=company)

# ========== ADMIN LOGIN PAGE ==========
@app.route('/admin')
def admin():
    if session.get('admin_logged_in'):
        return redirect(url_for('admin_dashboard'))
    return render_template('admin_login.html')

# ========== ADMIN LOGIN VERIFY ==========
@app.route('/admin/login', methods=['POST'])
def admin_login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    with open(ADMIN_FILE, 'r') as f:
        admin = json.load(f)
    
    if username == admin['username'] and password == admin['password']:
        session.permanent = True  # 7 din tak session rahegi
        session['admin_logged_in'] = True
        session['admin_username'] = username
        return jsonify({'success': True, 'message': 'Login successful!'})
    else:
        return jsonify({'success': False, 'message': 'Invalid credentials!'})

# ========== ADMIN LOGOUT ==========
@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    session.pop('admin_username', None)
    return redirect(url_for('admin'))

# ========== ADMIN DASHBOARD ==========
@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin'))
    return render_template('admin_dashboard.html', companies=COMPANY_DATA)

# ========== API: GET ALL APPLICANTS WITH RANKING ==========
@app.route('/api/admin/applicants')
def api_admin_applicants():
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    with open(APPLICANTS_FILE, 'r') as f:
        applicants = json.load(f)
    
    company = request.args.get('company', '')
    status = request.args.get('status', '')
    min_score = request.args.get('min_score', 0, type=int)
    
    filtered = []
    for app in applicants:
        if company and app['company'] != company:
            continue
        if status and app.get('status', 'Pending') != status:
            continue
        if min_score and app['score'] < min_score:
            continue
        filtered.append(app)
    
    filtered.sort(key=lambda x: x['score'], reverse=True)
    return jsonify(filtered)

# ========== API: GET COMPANY STATISTICS ==========
@app.route('/api/admin/stats')
def api_admin_stats():
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        with open(APPLICANTS_FILE, 'r') as f:
            applicants = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        applicants = []
        # File missing hai to create karo
        with open(APPLICANTS_FILE, 'w') as f:
            json.dump([], f)
    
    stats = {
        'total_applications': len(applicants),
        'total_companies': len(COMPANY_DATA),
        'pending_review': len([a for a in applicants if a.get('status', 'Pending') == 'Pending']),
        'shortlisted': len([a for a in applicants if a.get('status') == 'Shortlisted']),
        'selected': len([a for a in applicants if a.get('status') == 'Selected']),
        'rejected': len([a for a in applicants if a.get('status') == 'Rejected']),
        'avg_score': round(sum([a['score'] for a in applicants]) / len(applicants), 2) if applicants else 0,
        'company_wise': {}
    }
    
    for company in COMPANY_DATA:
        company_apps = [a for a in applicants if a['company'] == company['name']]
        stats['company_wise'][company['name']] = {
            'total': len(company_apps),
            'avg_score': round(sum([a['score'] for a in company_apps]) / len(company_apps), 2) if company_apps else 0,
            'top_score': max([a['score'] for a in company_apps]) if company_apps else 0
        }
    
    return jsonify(stats)

# ========== STEP 3: UPDATE STATUS WITH EMAIL ==========
@app.route('/api/admin/update_status', methods=['POST'])
def api_update_status():
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    applicant_id = data.get('id')
    new_status = data.get('status')
    
    with open(APPLICANTS_FILE, 'r') as f:
        applicants = json.load(f)
    
    for app in applicants:
        if app['id'] == applicant_id:
            app['status'] = new_status
            app['reviewed_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # ✅ EMAIL BHEJO - YEH LINE ADD KARO
            send_status_email(app, new_status)
            break
    
    with open(APPLICANTS_FILE, 'w') as f:
        json.dump(applicants, f, indent=2)
    
    return jsonify({'success': True, 'message': f'Status updated to {new_status} & email sent'})

# ========== DELETE APPLICANT ==========
@app.route('/api/admin/delete_applicant', methods=['POST'])
def delete_applicant():
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    applicant_id = data.get('id')

    with open(APPLICANTS_FILE, 'r') as f:
        applicants = json.load(f)

    # Remove jiska id match ho
    new_applicants = [app for app in applicants if app['id'] != applicant_id]

    with open(APPLICANTS_FILE, 'w') as f:
        json.dump(new_applicants, f, indent=2)

    return jsonify({'success': True, 'message': 'Applicant deleted successfully'})

# ========== API: GET TOP 10 APPLICANTS BY COMPANY ==========
@app.route('/api/admin/top10/<company>')
def api_top10(company):
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    with open(APPLICANTS_FILE, 'r') as f:
        applicants = json.load(f)
    
    company_apps = [a for a in applicants if a['company'] == company]
    company_apps.sort(key=lambda x: x['score'], reverse=True)
    
    return jsonify(company_apps[:10])

# ========== STEP 6 - EXPORT TO CSV WITH QUALIFICATION ==========
@app.route('/api/admin/export_csv/<company>')
def export_csv(company):
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        with open(APPLICANTS_FILE, 'r') as f:
            applicants = json.load(f)
        
        company_apps = [a for a in applicants if a['company'] == company]
        company_apps.sort(key=lambda x: x['score'], reverse=True)
        
        si = StringIO()
        cw = csv.writer(si)
        
        cw.writerow(['Rank', 'Name', 'Email', 'Qualification', 'Score', 'Matched Skills', 'Status', 'Applied Date'])
        
        for idx, app in enumerate(company_apps[:10], 1):
            cw.writerow([
                idx,
                app['name'],
                app['email'],
                app.get('qualification', 'N/A'),
                f"{app['score']}%",
                ', '.join(app.get('matched_skills', [])[:5]),
                app.get('status', 'Pending'),
                app.get('applied_date', 'N/A')
            ])
        
        output = make_response(si.getvalue())
        output.headers["Content-Disposition"] = f"attachment; filename={company}_Top10_{datetime.now().strftime('%Y%m%d')}.csv"
        output.headers["Content-type"] = "text/csv"
        
        return output
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ========== API: ADD NEW COMPANY ==========
@app.route('/api/admin/add_company', methods=['POST'])
def api_add_company():
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    new_company = {
        "id": len(COMPANY_DATA) + 1,
        "name": data.get('name'),
        "logo": data.get('logo', data.get('name')[:2].upper()),
        "industry": data.get('industry'),
        "skills": data.get('skills', []),
        "salary": data.get('salary'),
        "role": data.get('role'),
        "batch": data.get('batch', '2026'),
        "last_date": data.get('last_date')
    }
    
    COMPANY_DATA.append(new_company)
    
    with open(COMPANIES_FILE, 'r') as f:
        companies = json.load(f)
    
    companies.append(new_company)
    
    with open(COMPANIES_FILE, 'w') as f:
        json.dump(companies, f, indent=2)
    
    return jsonify({'success': True, 'message': 'Company added successfully!', 'company': new_company})

# ========== RESUME PARSER ==========
def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() + " "
        return text.lower()
    except Exception as e:
        print(f" PDF Error: {e}")
        return ""

# ========== SKILL EXTRACTOR ==========
def extract_skills_from_text(text):
    skills_db = {
        'python': ['python', 'django', 'flask', 'fastapi', 'pandas', 'numpy'],
        'java': ['java', 'spring', 'hibernate', 'j2ee', 'maven'],
        'javascript': ['javascript', 'js', 'react', 'angular', 'vue', 'node', 'express'],
        'cpp': ['c++', 'cpp', 'c plus plus'],
        'csharp': ['c#', 'c sharp', '.net'],
        'sql': ['sql', 'mysql', 'postgresql', 'oracle', 'database'],
        'aws': ['aws', 'amazon web services', 'ec2', 's3'],
        'azure': ['azure', 'microsoft azure'],
        'gcp': ['gcp', 'google cloud'],
        'tensorflow': ['tensorflow', 'tf'],
        'pytorch': ['pytorch', 'torch'],
        'docker': ['docker', 'container'],
        'kubernetes': ['kubernetes', 'k8s'],
        'dsa': ['dsa', 'data structures', 'algorithms', 'leetcode'],
        'system design': ['system design', 'architecture', 'distributed'],
        'react': ['react', 'reactjs'],
        'node': ['node', 'nodejs', 'express'],
        'devops': ['devops', 'ci/cd', 'jenkins', 'github actions'],
    }
    
    found_skills = []
    text_lower = text.lower()
    
    for category, skills in skills_db.items():
        for skill in skills:
            if skill in text_lower:
                found_skills.append(skill)
    
    return list(set(found_skills))


# main code: skill match calculation

# ========== MATCH SCORE CALCULATOR ==========
def calculate_match_score(resume_skills, company_name):
    company = next((c for c in COMPANY_DATA if c['name'].lower() == company_name.lower()), None)
    
    if not company:
        return 0, [], []
    
    required_skills = [s.lower() for s in company['skills']]
    resume_skills_lower = [s.lower() for s in resume_skills]
    
    matched_skills = []
    for skill in required_skills:
        if any(skill in rs or rs in skill for rs in resume_skills_lower):
            matched_skills.append(skill)
    
    score = (len(matched_skills) / len(required_skills)) * 100 if required_skills else 0
    missing_skills = [s for s in required_skills if s not in matched_skills][:5]
    
    return round(score, 2), matched_skills[:8], missing_skills

# ========== SUBMIT APPLICATION WITH QUALIFICATION ==========
@app.route('/submit_application', methods=['POST'])
def submit_application():
    try:
        name = request.form.get('name')
        email = request.form.get('email')
        qualification = request.form.get('qualification')
        company = request.form.get('company')
        resume_file = request.files.get('resume')
        
        print("\n" + "="*60)
        print("📥 NEW APPLICATION RECEIVED")
        print("="*60)
        print(f"👤 Name: {name}")
        print(f"📧 Email: {email}")
        print(f"🎓 Qualification: {qualification}")
        print(f"🏢 Company: {company}")
        print(f"📄 Resume: {resume_file.filename}")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{resume_file.filename}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        resume_file.save(filepath)
        print(f"✅ Resume saved: {filename}")
        
        resume_text = extract_text_from_pdf(filepath)
        resume_skills = extract_skills_from_text(resume_text)
        print(f"🔍 Skills found: {len(resume_skills)}")
        print(f"   Skills: {resume_skills[:10]}")
        
        score, matched_skills, missing_skills = calculate_match_score(resume_skills, company)
        print(f"📊 Match Score: {score}%")
        print(f"✅ Matched Skills: {matched_skills[:5]}")
        print(f" Missing Skills: {missing_skills[:5]}")
        
        applicant = {
            'id': timestamp,
            'name': name,
            'email': email,
            'qualification': qualification,
            'company': company,
            'resume': filename,
            'skills_found': resume_skills[:15],
            'matched_skills': matched_skills,
            'missing_skills': missing_skills,
            'score': score,
            'status': 'Pending',
            'applied_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        with open(APPLICANTS_FILE, 'r') as f:
            applicants = json.load(f)
        
        print(f"📊 Before append: {len(applicants)} applicants in database")
        
        applicants.append(applicant)
        
        print(f"📊 After append: {len(applicants)} applicants in database")
        
        with open(APPLICANTS_FILE, 'w') as f:
            json.dump(applicants, f, indent=2)
        
        print(f"💾 Data saved to {APPLICANTS_FILE}")
        print("="*60 + "\n")
        
        return jsonify({
            'success': True,
            'message': f'✅ Application submitted successfully for {company}!',
            'score': score,
            'matched_skills': matched_skills,
            'missing_skills': missing_skills
        })
        
    except Exception as e:
        print(f" ERROR: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

# ========== API: GET ALL COMPANIES =====
@app.route('/api/companies')
def api_companies():
    return jsonify(COMPANY_DATA)

if __name__ == '__main__':
    print("\n" + "="*80)
    print(" AI RESUME SCREENING SYSTEM 2026 - READY!")
    print("="*80)
    print("🏢 Companies: 10 Top Tech Companies Loaded")
    print("📍 Home Page: http://localhost:5000")
    print("📍 Apply Page: http://localhost:5000/apply")
    print("📍 Admin Login: http://localhost:5000/admin")
    print("\n🔐 Admin Credentials:")
    print("   Username: admin")
    print("   Password: admin123")
    print("\n✅ Features Active:")
    print("   • Resume Upload & Parsing")
    print("   • AI Skill Matching")
    print("   • Admin Dashboard")
    print("   • Top 10 Ranking")
    print("   • CSV Export with Qualification")
    print("   • Diploma/B.Tech/M.Tech Support")
    print("   • ✅ DELETE BUTTON ADDED")
    print("   • ✅ EMAIL NOTIFICATION ADDED")
    print("="*80)
    print("📁 JSON Database Files:")
    print(f"   • {APPLICANTS_FILE}")
    print(f"   • {COMPANIES_FILE}")
    print(f"   • {ADMIN_FILE}")
    print("="*80 + "\n")

    try:
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        print("\n" + "="*60)
        print("📱 SHARE THIS LINK WITH FRIENDS:")
        print(f" http://{ip_address}:5000")
        print("="*60)
    except Exception:
        pass

    debug_mode = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))