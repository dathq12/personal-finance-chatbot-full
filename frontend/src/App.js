import React from 'react';
import { BrowserRouter as Router } from 'react-router-dom';
import AppRoutes from './AppRoutes'; // import file vừa tạo


function App() {
  return (
    <Router>
      <AppRoutes />
    </Router>
  );
}

export default App;
