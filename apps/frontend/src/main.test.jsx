import React from 'react';
import { createRoot } from 'react-dom/client';

const App = () => (
    <div style={{padding: '40px', textAlign: 'center'}}>
        <h1>🚀 Minimal Test</h1>
        <p>If you see this, React is working!</p>
    </div>
);

const container = document.getElementById('root');
const root = createRoot(container);
root.render(<App />);
