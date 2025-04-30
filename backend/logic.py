from models import db, Mark, Reward

class RewardCalculator:
    @staticmethod
    def calculate_required_marks(student_id, subject_id):
        """Calculate marks needed in remaining internals to get avg of 12"""
        marks = Mark.query.filter_by(student_id=student_id, subject_id=subject_id).all()
        completed_internals = len(marks)
        
        if completed_internals >= 3:
            return 0, "All internals completed"
            
        total_marks = sum(mark.marks for mark in marks)
        
        # Target is average of 12 across 3 internals (total 36)
        target_total = 36  # 12 * 3
        
        # Calculate needed marks for remaining internals
        remaining_internals = 3 - completed_internals
        needed_marks = target_total - total_marks
        
        if remaining_internals > 0:
            marks_per_internal = needed_marks / remaining_internals
            return max(0, marks_per_internal), f"Need {max(0, marks_per_internal):.1f} marks per remaining internal"
        
        return 0, "All internals completed"
    
    @staticmethod
    def determine_reward(marks):
        """Determine reward based on marks achieved"""
        if marks >= 28:
            return ("Excellence Award", "Outstanding performance with exceptional understanding")
        elif marks >= 24:
            return ("Gold Star", "Excellent performance with strong subject knowledge")
        elif marks >= 20:
            return ("Silver Star", "Very good performance showing solid understanding")
        elif marks >= 16:
            return ("Bronze Star", "Good performance with clear grasp of concepts")
        elif marks >= 12:
            return ("Achievement Badge", "Satisfactory performance meeting required average")
        elif marks >= 8:
            return ("Effort Recognition", "Shows effort but needs improvement")
        else:
            return ("Participation", "Participation recognized, significant improvement needed")
    
    @staticmethod
    def assign_reward(student_id, subject_id, internal_number, marks):
        """Assign reward to a student based on their marks"""
        reward_type, description = RewardCalculator.determine_reward(marks)
        
        # Check if reward already exists
        existing_reward = Reward.query.filter_by(
            student_id=student_id,
            subject_id=subject_id,
            internal_number=internal_number
        ).first()
        
        if existing_reward:
            # Update existing reward
            existing_reward.reward_type = reward_type
            existing_reward.description = description
            db.session.commit()
            return existing_reward
        
        # Create new reward
        reward = Reward(
            student_id=student_id,
            subject_id=subject_id,
            internal_number=internal_number,
            reward_type=reward_type,
            description=description
        )
        
        db.session.add(reward)
        db.session.commit()
        return reward
