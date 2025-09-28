console.log('Starting React app...');

import React from 'react';
import { createRoot } from 'react-dom/client';

console.log('React imported successfully');

const App = () => {
    console.log('App component rendering');
    return React.createElement('div', {
        style: { padding: '40px', textAlign: 'center' }
    }, [
        React.createElement('h1', { key: '1' }, '🚀 Minimal Test'),
        React.createElement('p', { key: '2' }, 'If you see this, React is working!')
    ]);
};

console.log('App component defined');

const container = document.getElementById('root');
console.log('Container:', container);

if (!container) {
    console.error('Root element not found!');
} else {
    console.log('Creating root...');
    const root = createRoot(container);
    console.log('Root created, rendering...');
    root.render(React.createElement(App));
    console.log('Render called');
}
