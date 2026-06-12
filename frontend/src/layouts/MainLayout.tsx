import React from 'react';

const MainLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <div className='main-layout'>
    {children}
  </div>
);

export default MainLayout;
