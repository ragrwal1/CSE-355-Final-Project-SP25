'use client';

import { applyTheme } from './theme';

/**
 * Simple hook to apply theme in components
 */
export function useTheme() {
  if (typeof document !== 'undefined') {
    applyTheme();
  }
}