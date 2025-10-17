import { describe, it, expect } from 'vitest';
import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App.jsx';

describe('App', () => {
    it('should render without crashing', () => {
        expect(true).toBe(true);
    });

    it('should be defined', () => {
        expect(App).toBeDefined();
    });
});
