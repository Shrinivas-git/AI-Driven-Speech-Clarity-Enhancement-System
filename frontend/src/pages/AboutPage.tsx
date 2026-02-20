import React from 'react';
import { 
  SparklesIcon, 
  UserGroupIcon, 
  AcademicCapIcon,
  HeartIcon 
} from '@heroicons/react/24/outline';

export const AboutPage: React.FC = () => {
  return (
    <div className="space-y-6">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 dark:from-blue-800 dark:to-indigo-800 rounded-lg shadow-lg overflow-hidden">
        <div className="px-6 py-12 sm:px-12">
          <h1 className="text-4xl font-bold text-white mb-4">About Speech Clarity</h1>
          <p className="text-xl text-blue-100 max-w-3xl">
            Empowering clear communication through AI-powered speech enhancement technology
          </p>
        </div>
      </div>

      {/* Mission Section */}
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
        <div className="px-6 py-8">
          <div className="flex items-center mb-4">
            <SparklesIcon className="h-8 w-8 text-blue-600 dark:text-blue-400 mr-3" />
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Our Mission</h2>
          </div>
          <p className="text-gray-600 dark:text-gray-300 text-lg leading-relaxed">
            Speech Clarity is dedicated to helping individuals with speech disfluencies communicate more 
            confidently. Our AI-powered platform removes stuttering, repetitions, and filler words from 
            speech, transforming unclear audio into fluent, professional communication.
          </p>
        </div>
      </div>

      {/* Features Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Technology */}
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
          <div className="flex items-center mb-4">
            <AcademicCapIcon className="h-8 w-8 text-indigo-600 dark:text-indigo-400 mr-3" />
            <h3 className="text-xl font-bold text-gray-900 dark:text-white">Advanced Technology</h3>
          </div>
          <p className="text-gray-600 dark:text-gray-300">
            Built with state-of-the-art AI models including Whisper ASR for speech recognition, 
            intelligent text cleaning algorithms, and neural TTS for natural-sounding output.
          </p>
        </div>

        {/* Accessibility */}
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
          <div className="flex items-center mb-4">
            <UserGroupIcon className="h-8 w-8 text-green-600 dark:text-green-400 mr-3" />
            <h3 className="text-xl font-bold text-gray-900 dark:text-white">For Everyone</h3>
          </div>
          <p className="text-gray-600 dark:text-gray-300">
            Whether you're a student, professional, or content creator, our platform helps you 
            communicate clearly and confidently in any situation.
          </p>
        </div>
      </div>

      {/* What We Do */}
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
        <div className="px-6 py-8">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">What We Do</h2>
          <div className="space-y-4">
            <div className="flex items-start">
              <div className="flex-shrink-0">
                <div className="flex items-center justify-center h-8 w-8 rounded-md bg-blue-500 text-white">
                  1
                </div>
              </div>
              <div className="ml-4">
                <h4 className="text-lg font-medium text-gray-900 dark:text-white">Speech Recognition</h4>
                <p className="text-gray-600 dark:text-gray-300">
                  Convert your audio to text using advanced ASR technology
                </p>
              </div>
            </div>

            <div className="flex items-start">
              <div className="flex-shrink-0">
                <div className="flex items-center justify-center h-8 w-8 rounded-md bg-blue-500 text-white">
                  2
                </div>
              </div>
              <div className="ml-4">
                <h4 className="text-lg font-medium text-gray-900 dark:text-white">Intelligent Cleaning</h4>
                <p className="text-gray-600 dark:text-gray-300">
                  Remove stuttering, repetitions, fillers, and grammar errors
                </p>
              </div>
            </div>

            <div className="flex items-start">
              <div className="flex-shrink-0">
                <div className="flex items-center justify-center h-8 w-8 rounded-md bg-blue-500 text-white">
                  3
                </div>
              </div>
              <div className="ml-4">
                <h4 className="text-lg font-medium text-gray-900 dark:text-white">Natural Speech Synthesis</h4>
                <p className="text-gray-600 dark:text-gray-300">
                  Generate clear, fluent audio from the cleaned text
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Academic Project */}
      <div className="bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 rounded-lg shadow">
        <div className="px-6 py-8">
          <div className="flex items-center mb-4">
            <HeartIcon className="h-8 w-8 text-purple-600 dark:text-purple-400 mr-3" />
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Academic Project</h2>
          </div>
          <p className="text-gray-700 dark:text-gray-300 text-lg leading-relaxed">
            This project was developed as part of an academic research initiative to explore 
            AI applications in speech enhancement. It demonstrates the practical implementation 
            of machine learning models for real-world communication challenges.
          </p>
        </div>
      </div>

      {/* Stats */}
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
        <div className="px-6 py-8">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6 text-center">
            Platform Statistics
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-4xl font-bold text-blue-600 dark:text-blue-400 mb-2">
                95%+
              </div>
              <div className="text-gray-600 dark:text-gray-300">
                Fluency Improvement
              </div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-green-600 dark:text-green-400 mb-2">
                Fast
              </div>
              <div className="text-gray-600 dark:text-gray-300">
                Real-time Processing
              </div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-purple-600 dark:text-purple-400 mb-2">
                100%
              </div>
              <div className="text-gray-600 dark:text-gray-300">
                Privacy Protected
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Contact */}
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
        <div className="px-6 py-8 text-center">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
            Get in Touch
          </h2>
          <p className="text-gray-600 dark:text-gray-300 mb-6">
            Have questions or feedback? We'd love to hear from you!
          </p>
          <a
            href="mailto:support@speechclarity.com"
            className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600"
          >
            Contact Us
          </a>
        </div>
      </div>
    </div>
  );
};
