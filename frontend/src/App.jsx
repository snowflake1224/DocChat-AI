import React, { useState } from 'react';

function App() {
  const [docData, setDocData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [error, setError] = useState('');

  const handleFileUpload = async (e) => {
    if (!e.target.files.length) return;
    
    setIsLoading(true);
    setError('');
    const file = e.target.files[0];
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      const response = await fetch('http://localhost:8000/upload', {
        method: 'POST',
        body: formData
      });
      
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Upload failed');
      }
      
      const data = await response.json();
      setDocData({
        id: data.doc_id,
        filename: file.name,
        summary: data.summary
      });
      setChatHistory([]);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendMessage = async () => {
    if (!message.trim() || !docData) return;
    
    setIsLoading(true);
    setError('');
    const userMessage = message;
    setMessage('');
    
    // Add user message to chat
    setChatHistory(prev => [...prev, { sender: 'user', text: userMessage }]);
    
    try {
      const formData = new FormData();
      formData.append('doc_id', docData.id);
      formData.append('message', userMessage);
      
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        body: formData
      });
      
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Chat failed');
      }
      
      const data = await response.json();
      setChatHistory(prev => [...prev, { sender: 'ai', text: data.response }]);
    } catch (err) {
      setError(err.message);
      setChatHistory(prev => prev.slice(0, -1)); // Remove last message
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-3xl font-bold text-center my-6">DocChat AI</h1>
        
        {error && (
          <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 mb-4">
            {error}
          </div>
        )}
        
        {!docData ? (
          <div className="bg-white rounded-lg shadow p-6">
            <label className="block text-lg font-medium mb-4">
              Upload a document (PDF, TXT, DOCX)
            </label>
            <input 
              type="file" 
              accept=".pdf,.txt,.docx"
              onChange={handleFileUpload}
              disabled={isLoading}
              className="block w-full text-sm text-gray-500
                file:mr-4 file:py-2 file:px-4
                file:rounded file:border-0
                file:text-sm file:font-semibold
                file:bg-blue-50 file:text-blue-700
                hover:file:bg-blue-100"
            />
            {isLoading && (
              <div className="mt-4 text-center text-gray-500">Processing document...</div>
            )}
          </div>
        ) : (
          <div>
            <div className="bg-white rounded-lg shadow p-6 mb-6">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-semibold">{docData.filename}</h2>
                <button 
                  onClick={() => setDocData(null)}
                  className="text-sm text-blue-600 hover:text-blue-800"
                >
                  Upload new
                </button>
              </div>
              <div className="prose max-w-none">
                <h3 className="font-medium text-gray-700">Summary:</h3>
                <p className="text-gray-600">{docData.summary}</p>
              </div>
            </div>
            
            <div className="bg-white rounded-lg shadow p-6">
              <div className="h-80 overflow-y-auto mb-4 p-3 bg-gray-50 rounded">
                {chatHistory.map((msg, i) => (
                  <div 
                    key={i} 
                    className={`mb-3 ${msg.sender === 'user' ? 'text-right' : ''}`}
                  >
                    <span 
                      className={`inline-block px-4 py-2 rounded-lg ${
                        msg.sender === 'user' 
                          ? 'bg-blue-100 text-blue-800' 
                          : 'bg-gray-100 text-gray-800'
                      }`}
                    >
                      {msg.text}
                    </span>
                  </div>
                ))}
              </div>
              
              <div className="flex">
                <input
                  type="text"
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  placeholder="Ask about the document..."
                  className="flex-grow px-4 py-2 border rounded-l-lg focus:outline-none"
                  onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
                  disabled={isLoading}
                />
                <button
                  onClick={handleSendMessage}
                  disabled={isLoading || !message.trim()}
                  className="bg-blue-600 text-white px-6 py-2 rounded-r-lg disabled:opacity-50"
                >
                  {isLoading ? 'Sending...' : 'Send'}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;