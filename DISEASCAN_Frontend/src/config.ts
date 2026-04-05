// Environment variables
export const config = {
  // API Configuration
  apiUrl: import.meta.env.VITE_API_URL || 'http://localhost:8000',

  // Feature flags
  features: {
    enableMockMode: import.meta.env.VITE_MOCK_MODE === 'true',
    enableTypeAnimation: true,
    enableAutoScroll: true,
  },

  // UI Configuration
  ui: {
    messageAnimationDuration: 300,
    typingSpeed: 5, // ms per character
  },
}
