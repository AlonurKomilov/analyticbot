/**
 * Touch Ripple Effect for Mobile
 */
import React, { useState } from 'react';
import { Box } from '@mui/material';
import { rippleAnimation } from './keyframes';
import type { TouchRippleProps, Ripple } from './types';

export const TouchRipple: React.FC<TouchRippleProps> = ({ children, ...props }) => {
  const [ripples, setRipples] = useState<Ripple[]>([]);

  const addRipple = (
    event: React.MouseEvent<HTMLDivElement> | React.TouchEvent<HTMLDivElement>
  ): void => {
    const rect = event.currentTarget.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);

    let clientX: number, clientY: number;

    if ('touches' in event) {
      clientX = event.touches[0].clientX;
      clientY = event.touches[0].clientY;
    } else {
      clientX = event.clientX;
      clientY = event.clientY;
    }

    const x = clientX - rect.left - size / 2;
    const y = clientY - rect.top - size / 2;

    const newRipple: Ripple = {
      x,
      y,
      size,
      id: Date.now(),
    };

    setRipples((prev) => [...prev, newRipple]);

    setTimeout(() => {
      setRipples((prev) => prev.filter((ripple) => ripple.id !== newRipple.id));
    }, 600);
  };

  return (
    <Box
      {...props}
      onTouchStart={addRipple}
      onClick={addRipple as any}
      sx={{
        position: 'relative',
        overflow: 'hidden',
        ...props.sx,
      }}
    >
      {children}
      {ripples.map((ripple) => (
        <Box
          key={ripple.id}
          sx={{
            position: 'absolute',
            left: ripple.x,
            top: ripple.y,
            width: ripple.size,
            height: ripple.size,
            borderRadius: '50%',
            backgroundColor: 'rgba(0, 0, 0, 0.2)',
            animation: `${rippleAnimation} 0.6s ease-out`,
            pointerEvents: 'none',
          }}
        />
      ))}
    </Box>
  );
};
