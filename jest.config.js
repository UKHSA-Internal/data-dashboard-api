/** @type {import('jest').Config} */
export default {
  testEnvironment: 'jsdom',
  transform: {},

  // 1. Where Jest looks for tests
  roots: [
    '<rootDir>/auth_content/static/js',
    '<rootDir>/cms/dashboard/static/js'
  ],

  // 2. How Jest finds test files
  testMatch: [
    '**/*.spec.js',
  ],

  // 3. Ignore junk when discovering tests
  testPathIgnorePatterns: [
    '/node_modules/',
    '/static/admin/',
    '/static/vendor/',
    '/static/rest_framework/',
    '/static/debug_toolbar/',
    '/static/wagtail',
    '/staticfiles/',
    '/collected_static/',
    String.raw`/static/.*\.[0-9a-f]{6,}\.js$`
  ],

  // 4. Coverage ON
  collectCoverage: true,

  // 5. What files to include in coverage
  collectCoverageFrom: [
    '<rootDir>/auth_content/static/js/**/*.js',
    '<rootDir>/cms/dashboard/static/js/**/*.js',

    // EXCLUDE everything we don’t own
    '!**/node_modules/**',
    '!**/static/**/vendor/**',
    '!**/static/admin/**',
    '!**/static/rest_framework/**',
    '!**/static/debug_toolbar/**',
    '!**/static/wagtail*/**',
  ],

  // 6. Coverage output
  coverageDirectory: '<rootDir>/coverage',

  // 7. Coverage formats
  coverageReporters: ['json-summary', 'text', 'html'],

  // 8. Optional but useful
  modulePathIgnorePatterns: [
    '<rootDir>/node_modules/',
  ],

  // 9. Coverage threshold
  coverageThreshold: {
    global: {
      statements: 100,
      branches: 100,
      functions: 100,
      lines: 100,
    },
  },

  // 10. Reporters
  reporters: ['default', 'jest-junit'],
};
