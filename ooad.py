from dataclasses import dataclass
from typing import List
from uuid import UUID
from datetime import datetime

class RegisterStudentForClassService:
    def _init_(
        self,
        unit_of_work,
        student_repository,
        course_offering_repository,
        message_bus
    ):
        self.unit_of_work = unit_of_work
        self.student_repository = student_repository
        self.course_offering_repository = course_offering_repository
        self.message_bus = message_bus
    
    def register_student_for_class(
        self,
        student_id: UUID,
        course_offering_id: UUID,
        semester: 'Semester'
    ) -> 'RegistrationResult':
        try:
            self.unit_of_work.begin_transaction()
            
            student = self.student_repository.get_by_id(student_id)
            if not student:
                return RegistrationResult.failure("Student not found")
            
            course_offering = self.course_offering_repository.get_by_id(course_offering_id)
            if not course_offering:
if not course_offering:
                return RegistrationResult.failure("Course offering not found")
                
            if not student.is_eligible_for_registration():
                return RegistrationResult.failure("Student is not eligible for registration")
                
            if not course_offering.can_accept_enrollment():
                if course_offering.allows_waitlist():
                    return self._handle_waitlist(student, course_offering, semester)
                return RegistrationResult.failure("Course has reached capacity and waitlist is not available")
                
            if not course_offering.validate_prerequisites(student.completed_courses):
                return RegistrationResult.failure("Prerequisites not met")
                
            enrollment = student.register_for_class(course_offering_id, semester)
            course_offering.add_student(student_id)
            
            self.student_repository.save(student)
            self.course_offering_repository.save(course_offering)
            
            registration_event = StudentRegisteredEvent(
                student_id=student_id,
                course_offering_id=course_offering_id,
                semester=semester,
                timestamp=datetime.utcnow()
            )
            self.message_bus.publish(registration_event)
            
            self.unit_of_work.commit()
            return RegistrationResult.success()
            
        except Exception as ex:
            self.unit_of_work.rollback()
            return RegistrationResult.failure(f"Registration failed: {str(ex)}")
def _handle_waitlist(
        self,
        student: 'Student',
        course_offering: 'CourseOffering',
        semester: 'Semester'
    ) -> 'RegistrationResult':
        enrollment = student.add_to_waitlist(course_offering.id, semester)
        course_offering.add_to_waitlist(student.id)
        
        self.student_repository.save(student)
        self.course_offering_repository.save(course_offering)
        
        waitlist_event = StudentWaitlistedEvent(
            student_id=student.id,
            course_offering_id=course_offering.id,
            timestamp=datetime.utcnow()
        )
        self.message_bus.publish(waitlist_event)
        
        return RegistrationResult.success()

@dataclass
class StudentRegisteredEvent:
    student_id: UUID
    course_offering_id: UUID
    semester: 'Semester'
    timestamp: datetime

@dataclass
class StudentWaitlistedEvent:
    student_id: UUID
    course_offering_id: UUID
@dataclass
class StudentWaitlistedEvent:
    student_id: UUID
    course_offering_id: UUID
    timestamp: datetime
    
class Student:
    def is_eligible_for_registration(self) -> bool:
        raise NotImplementedError
        
    def register_for_class(self, course_offering_id: UUID, semester: 'Semester') -> 'Enrollment':
        raise NotImplementedError
        
    def add_to_waitlist(self, course_offering_id: UUID, semester: 'Semester') -> 'Enrollment':
        raise NotImplementedError
        
class CourseOffering:
    def can_accept_enrollment(self) -> bool:
        raise NotImplementedError
        
    def allows_waitlist(self) -> bool:
        raise NotImplementedError
        
    def validate_prerequisites(self, completed_courses: List[UUID]) -> bool:
        raise NotImplementedError
        
    def add_student(self, student_id: UUID) -> None:
        raise NotImplementedError
        
    def add_to_waitlist(self, student_id: UUID) -> None:
        raise NotImplementedError