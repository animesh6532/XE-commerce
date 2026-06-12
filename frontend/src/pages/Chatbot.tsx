import React from 'react';
import { ChatbotWindow } from '../components/chatbot';

const Chatbot: React.FC = () => {
  return (
    <div style={{
      minHeight: '100vh',
      backgroundColor: '#080b11',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      padding: '2rem'
    }}>
      <div style={{
        maxWidth: '1200px',
        width: '100%',
        margin: '0 auto'
      }}>
        <ChatbotWindow />
      </div>
    </div>
  );
};

export default Chatbot;
