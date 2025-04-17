'use client';

import { useEffect } from 'react';
import { applyTheme } from '@/lib/theme';

/**
 * Simple client component that applies the theme
 */
export default function ThemeLoader() {
  useEffect(() => {
    applyTheme();
  }, []);
  
  return null;
} 