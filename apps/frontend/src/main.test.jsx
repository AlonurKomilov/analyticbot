import { describe, it, expect, beforeAll } from 'vitest';
import { createRoot } from 'react-dom/client';

describe('Main Entry Point', () => {
    let container;

    beforeAll(() => {
        container = document.createElement('div');
        container.id = 'root';
        document.body.appendChild(container);
    });

    it('should have createRoot function available', () => {
        expect(createRoot).toBeDefined();
        expect(typeof createRoot).toBe('function');
    });

    it('should be able to create a root', () => {
        const root = createRoot(container);
        expect(root).toBeDefined();
    });
});
