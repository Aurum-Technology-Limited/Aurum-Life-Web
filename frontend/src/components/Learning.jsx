import React, { useState } from 'react';
import { BookOpen, Play, CheckCircle, Clock, User, Award } from 'lucide-react';
import { mockCourses } from '../data/mock';

const CourseCard = ({ course, onEnroll, onContinue }) => (
  <div className="p-6 rounded-xl border border-gray-800 bg-gradient-to-br from-gray-900/50 to-gray-800/30 hover:border-yellow-400/30 transition-all duration-300 group hover:scale-105">
    <img 
      src={course.image} 
      alt={course.title}
      className="w-full h-48 object-cover rounded-lg mb-4 group-hover:scale-105 transition-transform duration-300"
    />
    
    <div className="mb-4">
      <h3 className="text-xl font-semibold text-white mb-2">{course.title}</h3>
      <p className="text-gray-400 text-sm mb-3">{course.description}</p>
      
      <div className="flex items-center space-x-4 text-sm text-gray-400 mb-4">
        <div className="flex items-center space-x-1">
          <User size={14} />
          <span>{course.instructor}</span>
        </div>
        <div className="flex items-center space-x-1">
          <Clock size={14} />
          <span>{course.duration}</span>
        </div>
        <span className="capitalize text-yellow-400">{course.category}</span>
      </div>
    </div>
    
    {course.progress > 0 ? (
      <div className="mb-4">
        <div className="flex justify-between text-sm text-gray-400 mb-2">
          <span>Progress</span>
          <span>{course.progress}%</span>
        </div>
        <div className="w-full bg-gray-700 rounded-full h-2">
          <div 
            className="h-2 rounded-full transition-all duration-500"
            style={{ 
              backgroundColor: '#F4B400',
              width: `${course.progress}%`
            }}
          />
        </div>
      </div>
    ) : null}
    
    <button
      onClick={() => course.progress > 0 ? onContinue(course) : onEnroll(course)}
      className="w-full py-3 rounded-lg font-medium transition-all duration-200 hover:scale-105 flex items-center justify-center space-x-2"
      style={{ backgroundColor: '#F4B400', color: '#0B0D14' }}
    >
      {course.progress > 0 ? (
        <>
          <Play size={20} />
          <span>Continue Learning</span>
        </>
      ) : (
        <>
          <BookOpen size={20} />
          <span>Enroll Now</span>
        </>
      )}
    </button>
  </div>
);

const CourseModal = ({ course, isOpen, onClose }) => {
  const [currentLesson, setCurrentLesson] = useState(0);
  
  const lessons = [
    { title: 'Introduction & Overview', duration: '12:30', completed: true },
    { title: 'Core Principles', duration: '18:45', completed: true },
    { title: 'Practical Applications', duration: '24:15', completed: false },
    { title: 'Advanced Techniques', duration: '20:30', completed: false },
    { title: 'Case Studies', duration: '16:20', completed: false },
    { title: 'Final Assessment', duration: '8:10', completed: false }
  ];

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-gray-900 rounded-xl w-full max-w-4xl border border-gray-800 max-h-screen overflow-y-auto">
        <div className="p-6 border-b border-gray-800">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold text-white">{course.title}</h2>
              <p className="text-gray-400 mt-2">{course.description}</p>
            </div>
            <button
              onClick={onClose}
              className="p-2 rounded-lg hover:bg-gray-800 transition-colors"
            >
              <BookOpen size={20} className="text-gray-400 rotate-45" />
            </button>
          </div>
        </div>

        <div className="flex">
          {/* Lesson List */}
          <div className="w-1/3 p-6 border-r border-gray-800">
            <h3 className="text-lg font-semibold text-white mb-4">Course Content</h3>
            <div className="space-y-2">
              {lessons.map((lesson, index) => (
                <button
                  key={index}
                  onClick={() => setCurrentLesson(index)}
                  className={`w-full text-left p-3 rounded-lg transition-all duration-200 ${
                    currentLesson === index 
                      ? 'bg-yellow-400 text-gray-900' 
                      : 'bg-gray-800/50 text-white hover:bg-gray-700/50'
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    {lesson.completed ? (
                      <CheckCircle size={16} className={currentLesson === index ? 'text-gray-700' : 'text-green-400'} />
                    ) : (
                      <div className={`w-4 h-4 rounded-full border-2 ${
                        currentLesson === index ? 'border-gray-700' : 'border-gray-500'
                      }`} />
                    )}
                    <div className="flex-1">
                      <p className="font-medium text-sm">{lesson.title}</p>
                      <p className={`text-xs ${currentLesson === index ? 'text-gray-600' : 'text-gray-400'}`}>
                        {lesson.duration}
                      </p>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Video Player Area */}
          <div className="flex-1 p-6">
            <div className="bg-gray-800 rounded-lg aspect-video mb-6 flex items-center justify-center">
              <div className="text-center">
                <Play size={64} className="text-yellow-400 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-white mb-2">
                  {lessons[currentLesson].title}
                </h3>
                <p className="text-gray-400">Duration: {lessons[currentLesson].duration}</p>
                <button
                  className="mt-4 px-6 py-3 rounded-lg font-medium transition-all duration-200 hover:scale-105"
                  style={{ backgroundColor: '#F4B400', color: '#0B0D14' }}
                >
                  {lessons[currentLesson].completed ? 'Review Lesson' : 'Start Lesson'}
                </button>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <button
                onClick={() => setCurrentLesson(Math.max(0, currentLesson - 1))}
                disabled={currentLesson === 0}
                className="px-4 py-2 rounded-lg border border-gray-700 text-gray-300 hover:bg-gray-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Previous
              </button>
              <span className="text-gray-400">
                {currentLesson + 1} of {lessons.length}
              </span>
              <button
                onClick={() => setCurrentLesson(Math.min(lessons.length - 1, currentLesson + 1))}
                disabled={currentLesson === lessons.length - 1}
                className="px-4 py-2 rounded-lg bg-yellow-400 text-gray-900 hover:bg-yellow-300 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Next
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const Learning = () => {
  const [selectedCourse, setSelectedCourse] = useState(null);
  const [modalOpen, setModalOpen] = useState(false);

  const handleEnrollCourse = (course) => {
    console.log(`Enrolling in: ${course.title}`);
    // Here you would typically make an API call to enroll the user
  };

  const handleContinueCourse = (course) => {
    setSelectedCourse(course);
    setModalOpen(true);
  };

  const completedCourses = mockCourses.filter(course => course.progress === 100);
  const inProgressCourses = mockCourses.filter(course => course.progress > 0 && course.progress < 100);

  return (
    <div className="space-y-8">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-white mb-2">Learning & Development</h1>
        <p className="text-gray-400 max-w-2xl mx-auto">
          Expand your knowledge and develop new skills with our curated collection of personal growth courses
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="p-6 rounded-xl border border-gray-800 bg-gradient-to-br from-gray-900/50 to-gray-800/30">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 rounded-lg bg-yellow-400 flex items-center justify-center">
              <BookOpen size={20} style={{ color: '#0B0D14' }} />
            </div>
            <div>
              <h3 className="text-2xl font-bold text-white">{mockCourses.length}</h3>
              <p className="text-sm text-gray-400">Total Courses</p>
            </div>
          </div>
        </div>
        
        <div className="p-6 rounded-xl border border-gray-800 bg-gradient-to-br from-gray-900/50 to-gray-800/30">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 rounded-lg bg-blue-400 flex items-center justify-center">
              <Play size={20} style={{ color: '#0B0D14' }} />
            </div>
            <div>
              <h3 className="text-2xl font-bold text-white">{inProgressCourses.length}</h3>
              <p className="text-sm text-gray-400">In Progress</p>
            </div>
          </div>
        </div>
        
        <div className="p-6 rounded-xl border border-gray-800 bg-gradient-to-br from-gray-900/50 to-gray-800/30">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 rounded-lg bg-green-400 flex items-center justify-center">
              <CheckCircle size={20} style={{ color: '#0B0D14' }} />
            </div>
            <div>
              <h3 className="text-2xl font-bold text-white">{completedCourses.length}</h3>
              <p className="text-sm text-gray-400">Completed</p>
            </div>
          </div>
        </div>
        
        <div className="p-6 rounded-xl border border-gray-800 bg-gradient-to-br from-gray-900/50 to-gray-800/30">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 rounded-lg bg-purple-400 flex items-center justify-center">
              <Award size={20} style={{ color: '#0B0D14' }} />
            </div>
            <div>
              <h3 className="text-2xl font-bold text-white">45</h3>
              <p className="text-sm text-gray-400">Hours Learned</p>
            </div>
          </div>
        </div>
      </div>

      {/* Continue Learning Section */}
      {inProgressCourses.length > 0 && (
        <div>
          <h2 className="text-2xl font-bold text-white mb-6">Continue Learning</h2>
          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
            {inProgressCourses.map((course) => (
              <CourseCard
                key={course.id}
                course={course}
                onEnroll={handleEnrollCourse}
                onContinue={handleContinueCourse}
              />
            ))}
          </div>
        </div>
      )}

      {/* All Courses */}
      <div>
        <h2 className="text-2xl font-bold text-white mb-6">All Courses</h2>
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
          {mockCourses.map((course) => (
            <CourseCard
              key={course.id}
              course={course}
              onEnroll={handleEnrollCourse}
              onContinue={handleContinueCourse}
            />
          ))}
        </div>
      </div>

      {/* Course Modal */}
      <CourseModal
        course={selectedCourse}
        isOpen={modalOpen}
        onClose={() => {
          setModalOpen(false);
          setSelectedCourse(null);
        }}
      />
    </div>
  );
};

export default Learning;