from flask import render_template, url_for, flash, redirect, request, jsonify, session
from models import db, Student, Faculty, Department, Subject, Mark, Reward
from logic import RewardCalculator



def configure_routes(app):
    @app.route('/')
    def home():
        return render_template('home.html')

    # ------------------ Student Routes ------------------

    @app.route('/student/login', methods=['GET', 'POST'])
    def student_login():
        if request.method == 'POST':
            name = request.form.get('name')
            usn = request.form.get('usn')
            
            student = Student.query.filter_by(usn=usn).first()
            if not student:
                student = Student(name=name, usn=usn)
                db.session.add(student)
                db.session.commit()
            
            session['student_id'] = student.id
            session['user_type'] = 'student'
            flash(f'Welcome, {name}!', 'success')
            return redirect(url_for('student_dashboard'))
            
        return render_template('student_login.html')

    @app.route('/student/dashboard')
    def student_dashboard():
        if 'student_id' not in session:
            flash('Please login first', 'error')
            return redirect(url_for('student_login'))

        student_id = session['student_id']
        student = Student.query.get(student_id)

        subject_ids = db.session.query(Mark.subject_id).filter_by(student_id=student_id).distinct()
        subjects = Subject.query.filter(Subject.id.in_(subject_ids)).all()


        subjects_data = []
        for subject in subjects:
            marks = Mark.query.filter_by(student_id=student_id, subject_id=subject.id).all()
            mark_map = {m.internal_number: m.marks for m in marks}

            avg = sum(mark_map.values()) / 3 if len(mark_map) == 3 else None
            rewards = Reward.query.filter_by(student_id=student_id, subject_id=subject.id).all()

            subjects_data.append({
                'subject': subject,
                'i1': mark_map.get(1, '-'),
                'i2': mark_map.get(2, '-'),
                'i3': mark_map.get(3, '-'),
                'avg': f"{avg:.2f}" if avg else 'Incomplete',
                'rewards': rewards
            })

        return render_template('student_dashboard.html', student=student, subjects_data=subjects_data)

    '''@app.route('/student/add_marks', methods=['POST'])
    def add_marks():
        if 'student_id' not in session:
            flash('Please login first', 'error')
            return redirect(url_for('student_login'))
            
        student_id = session['student_id']
        subject_id = request.form.get('subject_id')
        internal_number = int(request.form.get('internal_number'))
        marks = float(request.form.get('marks'))
        
        if marks < 0 or marks > 30:
            flash('Marks must be between 0 and 30', 'error')
            return redirect(url_for('student_dashboard'))
        
        existing_mark = Mark.query.filter_by(
            student_id=student_id,
            subject_id=subject_id,
            internal_number=internal_number
        ).first()
        
        if existing_mark:
            existing_mark.marks = marks
        else:
            mark = Mark(
                student_id=student_id,
                subject_id=subject_id,
                internal_number=internal_number,
                marks=marks
            )
            db.session.add(mark)
        db.session.commit()
        
        reward = RewardCalculator.assign_reward(student_id, subject_id, internal_number, marks)
        flash(f'Marks added successfully! You earned: {reward.reward_type}', 'success')
        return redirect(url_for('student_dashboard'))'''

    # ------------------ Faculty Routes ------------------

    @app.route('/faculty/login', methods=['GET', 'POST'])
    def faculty_login():
        if request.method == 'POST':
            name = request.form.get('name')
            subject_code = request.form.get('subject_code')
            
            faculty = Faculty.query.filter_by(name=name, subject_code=subject_code).first()
            if not faculty:
                faculty = Faculty(name=name, subject_code=subject_code)
                db.session.add(faculty)
                db.session.commit()
                
                subject = Subject.query.filter_by(code=subject_code).first()
                if not subject:
                    subject = Subject(
                        name=request.form.get('subject_name', f'Subject {subject_code}'), 
                        code=subject_code, 
                        faculty_id=faculty.id
                    )
                    db.session.add(subject)
                    db.session.commit()
            
            session['faculty_id'] = faculty.id
            session['user_type'] = 'faculty'
            flash(f'Welcome, {name}!', 'success')
            return redirect(url_for('faculty_dashboard'))
            
        return render_template('faculty_login.html')

    @app.route('/faculty/dashboard')
    def faculty_dashboard():
        if 'faculty_id' not in session:
            flash('Please login first', 'error')
            return redirect(url_for('faculty_login'))
            
        faculty_id = session['faculty_id']
        faculty = Faculty.query.get(faculty_id)
        subjects = Subject.query.filter_by(faculty_id=faculty_id).all()

        subjects_data = []
        for subject in subjects:
            # Top students per internal
            top_students = []
            for internal in range(1, 4):
                marks = db.session.query(Mark, Student)\
                    .join(Student, Mark.student_id == Student.id)\
                    .filter(Mark.subject_id == subject.id, Mark.internal_number == internal)\
                    .order_by(Mark.marks.desc())\
                    .limit(5)\
                    .all()
                top_students.append({
                    'internal': internal,
                    'students': marks
                })

            # Rewards for subject
            rewards = db.session.query(Reward, Student)\
                .join(Student, Reward.student_id == Student.id)\
                .filter(Reward.subject_id == subject.id)\
                .all()

            # Full mark sheet: all students for the subject
            students = Student.query.all()
            full_marks = []
            for student in students:
                marks = Mark.query.filter_by(student_id=student.id, subject_id=subject.id).all()
                mark_map = {m.internal_number: m for m in marks}  # store full Mark objects

                # Calculate average only if all 3 internals are present
                if len(mark_map) == 3:
                    avg = sum(m.marks for m in mark_map.values()) / 3
                else:
                    avg = None

                reward = Reward.query.filter_by(student_id=student.id, subject_id=subject.id).first()

                full_marks.append({
                    'name': student.name,
                    'usn': student.usn,
                    'm1': mark_map.get(1),
                    'm2': mark_map.get(2),
                    'm3': mark_map.get(3),
                    'avg': f"{avg:.2f}" if avg else 'Incomplete',
                    'reward': reward.reward_type if reward else '-'
                })

            subjects_data.append({
                'subject': subject,
                'top_students': top_students,
                'rewards': rewards,
                'full_marks': full_marks
            })

        return render_template('faculty_dashboard.html', faculty=faculty, subjects_data=subjects_data)

    @app.route('/faculty/edit_marks', methods=['POST'])
    def faculty_edit_marks():
        if 'faculty_id' not in session:
            flash('Please login first', 'error')
            return redirect(url_for('faculty_login'))

        student_usn = request.form.get('student_usn')
        subject_id = request.form.get('subject_id')
        internal_number = int(request.form.get('internal_number'))
        marks = float(request.form.get('marks'))

        student = Student.query.filter_by(usn=student_usn).first()
        if not student:
            flash('Student not found.', 'error')
            return redirect(url_for('faculty_dashboard'))

        # Update or insert the mark
        mark = Mark.query.filter_by(student_id=student.id, subject_id=subject_id, internal_number=internal_number).first()
        if mark:
            mark.marks = marks
        else:
            mark = Mark(
                student_id=student.id,
                subject_id=subject_id,
                internal_number=internal_number,
                marks=marks
            )
            db.session.add(mark)

        # Update reward
        RewardCalculator.assign_reward(student.id, subject_id, internal_number, marks)
        db.session.commit()

        flash(f'Marks updated for {student.name} - Internal {internal_number}', 'success')
        return redirect(url_for('faculty_dashboard'))

    @app.route('/faculty/send_motivation', methods=['POST'])
    def send_motivation():
        if 'faculty_id' not in session:
            flash('Please login first', 'error')
            return redirect(url_for('faculty_login'))

        student_usn = request.form.get('student_usn')
        subject_id = request.form.get('subject_id')
        message = request.form.get('message')

        student = Student.query.filter_by(usn=student_usn).first()
        subject = Subject.query.get(subject_id)

        if student and subject:
            # Simulate storing or sending the message (e.g., log or flash for now)
            flash(f'Motivation sent to {student.name} for {subject.name}: "{message}"', 'info')
            # You could optionally store this in a new Motivation model if needed.
        else:
            flash('Failed to send motivation. Student or subject not found.', 'error')

        return redirect(url_for('faculty_dashboard'))
    
    @app.route('/faculty/delete_subject/<int:subject_id>', methods=['POST'])
    def delete_subject(subject_id):
        if 'faculty_id' not in session:
            flash('Please login first', 'error')
            return redirect(url_for('faculty_login'))

        subject = Subject.query.get(subject_id)
        if not subject or subject.faculty_id != session['faculty_id']:
            flash('Unauthorized or subject not found.', 'error')
            return redirect(url_for('faculty_dashboard'))

        # Delete related marks and rewards
        Mark.query.filter_by(subject_id=subject.id).delete()
        Reward.query.filter_by(subject_id=subject.id).delete()
        db.session.delete(subject)
        db.session.commit()

        flash(f"Subject '{subject.name}' deleted.", 'success')
        return redirect(url_for('faculty_dashboard'))


    # ------------------ Department Routes ------------------

    @app.route('/department/login', methods=['GET', 'POST'])
    def department_login():
        if request.method == 'POST':
            department_name = request.form.get('department_name')
            class_name = request.form.get('class_name')
            
            department = Department.query.filter_by(name=department_name, class_name=class_name).first()
            if not department:
                department = Department(name=department_name, class_name=class_name)
                db.session.add(department)
                db.session.commit()
            
            session['department_id'] = department.id
            session['user_type'] = 'department'
            flash(f'Welcome, {department_name} Department!', 'success')
            return redirect(url_for('department_dashboard'))
            
        return render_template('department_login.html')

    @app.route('/department/dashboard')
    def department_dashboard():
        if 'department_id' not in session:
            flash('Please login first', 'error')
            return redirect(url_for('department_login'))
            
        department_id = session['department_id']
        department = Department.query.get(department_id)

        all_rewards = db.session.query(Reward, Student, Subject)\
            .join(Student, Reward.student_id == Student.id)\
            .join(Subject, Reward.subject_id == Subject.id)\
            .all()

        reward_stats = {}
        for reward_type in ['Excellence Award', 'Gold Star', 'Silver Star', 'Bronze Star', 
                            'Achievement Badge', 'Effort Recognition', 'Participation']:
            count = Reward.query.filter_by(reward_type=reward_type).count()
            reward_stats[reward_type] = count

        return render_template('department_dashboard.html', 
                               department=department, 
                               all_rewards=all_rewards,
                               reward_stats=reward_stats)
