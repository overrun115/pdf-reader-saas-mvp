import React from 'react';
import { IconButton, Tooltip } from '@mui/material';
import { LightMode, DarkMode } from '@mui/icons-material';
import { useTheme } from '../../hooks/useTheme';

interface ThemeToggleProps {
  size?: 'small' | 'medium' | 'large';
  color?: 'inherit' | 'primary' | 'secondary' | 'default';
}

export const ThemeToggle: React.FC<ThemeToggleProps> = ({ 
  size = 'small', 
  color = 'inherit' 
}) => {
  const { mode, toggleTheme } = useTheme();

  return (
    <IconButton
      onClick={toggleTheme}
      color={color}
      size={size}
      sx={{
        color: 'text.secondary',
        transition: 'all 0.15s ease-in-out',
        '&:hover': {
          color: 'text.primary',
          bgcolor: 'action.hover',
        },
        '& svg': {
          fontSize: 18,
        },
      }}
    >
      {mode === 'light' ? <DarkMode /> : <LightMode />}
    </IconButton>
  );
};

export default ThemeToggle;