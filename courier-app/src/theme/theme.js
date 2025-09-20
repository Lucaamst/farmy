import { MD3LightTheme } from 'react-native-paper';

export const theme = {
  ...MD3LightTheme,
  colors: {
    ...MD3LightTheme.colors,
    primary: '#ea580c',
    primaryContainer: '#fed7aa',
    secondary: '#dc2626',
    secondaryContainer: '#fecaca',
    tertiary: '#059669',
    tertiaryContainer: '#a7f3d0',
    surface: '#ffffff',
    surfaceVariant: '#fff7ed',
    background: '#fff7ed',
    error: '#dc2626',
    errorContainer: '#fecaca',
    onPrimary: '#ffffff',
    onSecondary: '#ffffff',
    onTertiary: '#ffffff',
    onSurface: '#1f2937',
    onSurfaceVariant: '#6b7280',
    onBackground: '#1f2937',
    outline: '#d1d5db',
    shadow: '#000000',
  },
  fonts: {
    ...MD3LightTheme.fonts,
    bodyLarge: {
      fontFamily: 'System',
      fontSize: 16,
      fontWeight: '400',
      lineHeight: 24,
    },
    bodyMedium: {
      fontFamily: 'System',
      fontSize: 14,
      fontWeight: '400',
      lineHeight: 20,
    },
    titleLarge: {
      fontFamily: 'System',
      fontSize: 22,
      fontWeight: '600',
      lineHeight: 28,
    },
    titleMedium: {
      fontFamily: 'System',
      fontSize: 18,
      fontWeight: '600',
      lineHeight: 24,
    },
  },
};