import React, { useState, useRef } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import { motion } from 'framer-motion';
import { Zap, BarChart2, Clock, Award } from 'lucide-react';

const API_URL = 'http://localhost:8000';

const Header = () => (
  <motion.header 
    initial={{ y: -50, opacity: 0 }}
    animate={{ y: 0, opacity: 1 }}
    transition={{ duration: 0.5 }}
    className="bg-purple-600 text-white p-4"
  >
    <div className="container mx-auto text-center">
      <h1 className="text-3xl font-bold">Spark Plug Analyzer</h1>
    </div>
  </motion.header>
);

const Footer = () => (
  <footer className="bg-gray-800 text-white p-4">
    <div className="container mx-auto text-center">
      <p>Spark Plug Analyzer - Optimizing Engine Performance</p>
    </div>
  </footer>
);

const FeatureItem = ({ Icon, title, description }) => (
  <div className="flex items-center space-x-2">
    <div className="flex-shrink-0">
      <Icon className="h-5 w-5 text-purple-500" />
    </div>
    <div>
      <h3 className="text-sm font-medium text-gray-900">{title}</h3>
      <p className="text-xs text-gray-500">{description}</p>
    </div>
  </div>
);

const LLMModel = () => {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    setFile(selectedFile);
    setPreview(URL.createObjectURL(selectedFile));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setError('Please select a file to upload.');
      return;
    }

    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(`${API_URL}/analyze/`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setAnalysis(response.data);
    } catch (error) {
      setError(error.response?.data?.detail || error.message || 'An unknown error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col min-h-screen bg-gray-100">
      <Header />
      <main className="flex-grow container mx-auto px-4 py-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {/* First Column - Upload */}
          <motion.div 
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5 }}
            className="bg-white rounded-xl shadow-lg p-4 flex flex-col h-full"
          >
            <h2 className="text-xl font-bold mb-3">Upload Image</h2>
            <form onSubmit={handleSubmit} className="space-y-3 mb-4">
              <div className="flex items-center justify-center w-full h-48">
                <label htmlFor="file-upload" className="flex flex-col items-center justify-center w-full h-full border-2 border-purple-300 border-dashed rounded-lg cursor-pointer bg-purple-50 hover:bg-purple-100 transition-all duration-300">
                  <div className="flex flex-col items-center justify-center p-4 text-center">
                    <svg className="w-10 h-10 mb-3 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                    </svg>
                    <p className="mb-2 text-sm text-purple-500"><span className="font-semibold">Click to upload</span> or drag and drop</p>
                    <p className="text-xs text-purple-500">PNG or JPG (MAX. 800x400px)</p>
                  </div>
                  <input id="file-upload" type="file" className="hidden" onChange={handleFileChange} accept="image/*" />
                </label>
              </div>
              <motion.button 
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                type="submit" 
                disabled={loading || !file}
                className={`w-full py-2 px-4 rounded-lg text-white font-medium ${
                  loading || !file ? 'bg-purple-300 cursor-not-allowed' : 'bg-purple-600 hover:bg-purple-700'
                }`}
              >
                {loading ? 'Analyzing...' : 'Analyze'}
              </motion.button>
            </form>
            <div className="space-y-2 mt-auto">
              <h3 className="text-lg font-semibold">Feature Highlights</h3>
              <FeatureItem 
                Icon={Zap} 
                title="Instant Analysis" 
                description="Quick insights on spark plug condition"
              />
              <FeatureItem 
                Icon={BarChart2} 
                title="Detailed Reports" 
                description="Comprehensive health breakdown"
              />
              <FeatureItem 
                Icon={Clock} 
                title="Time-Saving" 
                description="Efficient maintenance process"
              />
              <FeatureItem 
                Icon={Award} 
                title="Expert Insights" 
                description="AI-powered expert analysis"
              />
            </div>
          </motion.div>

          {/* Second Column - Preview */}
          <motion.div 
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="bg-white rounded-xl shadow-lg p-4 flex flex-col h-full"
          >
            <h2 className="text-xl font-bold mb-3">Image Preview</h2>
            <div className="flex-grow flex items-center justify-center bg-gray-100 rounded-lg overflow-hidden" style={{ height: '300px' }}>
              {preview ? (
                <motion.img 
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ duration: 0.5 }}
                  src={preview} 
                  alt="Preview" 
                  className="max-w-full max-h-full object-contain" 
                />
              ) : (
                <p className="text-gray-500">No image uploaded yet</p>
              )}
            </div>
          </motion.div>

          {/* Third Column - Results */}
          <motion.div 
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="bg-white rounded-xl shadow-lg p-4 flex flex-col h-full"
          >
            <h2 className="text-xl font-bold mb-3">Analysis Results</h2>
            <div className="flex-grow overflow-auto" style={{ height: '300px' }}>
              {loading && (
                <div className="flex justify-center items-center h-full">
                  <motion.div 
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                    className="w-10 h-10 border-t-2 border-b-2 border-purple-500 rounded-full"
                  />
                </div>
              )}
              {error && (
                <motion.div 
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ duration: 0.3 }}
                  className="bg-red-100 border-l-4 border-red-500 text-red-700 p-3 rounded" 
                  role="alert"
                >
                  <p className="font-bold">Error</p>
                  <p>{error}</p>
                </motion.div>
              )}
              {analysis && (
                <motion.div 
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ duration: 0.5 }}
                  className="space-y-3"
                >
                  <div className="flex justify-between items-center">
                    <span className="text-gray-700">Overall Assessment:</span>
                    <span className={`px-2 py-1 rounded-full text-sm font-medium ${
                      analysis.overall_assessment === 'PASS' ? 'bg-green-200 text-green-800' : 'bg-red-200 text-red-800'
                    }`}>
                      {analysis.overall_assessment}
                    </span>
                  </div>
                  <div className="bg-gray-50 p-3 rounded-lg overflow-auto">
                    <ReactMarkdown 
                      className="prose prose-sm max-w-none"
                      components={{
                        h1: ({node, ...props}) => <h1 className="text-lg font-bold mt-3 mb-2" {...props} />,
                        h2: ({node, ...props}) => <h2 className="text-md font-semibold mt-2 mb-1" {...props} />,
                        h3: ({node, ...props}) => <h3 className="text-sm font-medium mt-1 mb-1" {...props} />,
                        p: ({node, ...props}) => <p className="mb-2 text-sm" {...props} />,
                        ul: ({node, ...props}) => <ul className="list-disc pl-4 mb-2" {...props} />,
                        ol: ({node, ...props}) => <ol className="list-decimal pl-4 mb-2" {...props} />,
                        li: ({node, ...props}) => <li className="mb-1 text-sm" {...props} />,
                        code: ({node, inline, ...props}) => 
                          inline ? (
                            <code className="bg-gray-200 rounded px-1 py-0.5 text-xs" {...props} />
                          ) : (
                            <code className="block bg-gray-200 rounded p-2 overflow-x-auto text-xs" {...props} />
                          ),
                      }}
                    >
                      {analysis.analysis}
                    </ReactMarkdown>
                  </div>
                </motion.div>
              )}
              {!analysis && !loading && (
                <div className="flex items-center justify-center h-full">
                  <p className="text-gray-500">No analysis results yet</p>
                </div>
              )}
            </div>
          </motion.div>
        </div>
      </main>
      <Footer />
    </div>
  );
};

export default LLMModel;