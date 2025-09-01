import js from "@eslint/js";
import reactPlugin from "eslint-plugin-react";
import hooksPlugin from "eslint-plugin-react-hooks";
import reactRefresh from "eslint-plugin-react-refresh";

export default [
  {
    ignores: ["dist/**", "coverage-vitest/**", "node_modules/**"]
  },
  js.configs.recommended,
  {
    files: ["**/*.{js,jsx}"],
    languageOptions: {
      ecmaVersion: "latest",
      sourceType: "module",
      parserOptions: {
        ecmaFeatures: {
          jsx: true
        }
      },
      globals: {
        document: "readonly",
        window: "readonly",
        navigator: "readonly",
        console: "readonly",
        process: "readonly",
        global: "readonly",
        performance: "readonly",
        fetch: "readonly",
        URL: "readonly",
        URLSearchParams: "readonly",
        setTimeout: "readonly",
        clearTimeout: "readonly",
        setInterval: "readonly",
        clearInterval: "readonly",
        alert: "readonly",
        confirm: "readonly",
        module: "readonly",
        require: "readonly",
        Blob: "readonly",
        HTMLElement: "readonly",
        FormData: "readonly",
        IntersectionObserver: "readonly",
        // Test globals
        describe: "readonly",
        it: "readonly",
        test: "readonly",
        expect: "readonly",
        beforeAll: "readonly",
        afterAll: "readonly",
        beforeEach: "readonly",
        afterEach: "readonly",
        vi: "readonly",
        jest: "readonly"
      },
    },
    plugins: {
      react: reactPlugin,
      "react-hooks": hooksPlugin,
      "react-refresh": reactRefresh,
      // Ignore "React" because it's often imported for JSX but not directly referenced.
      // Ignore variables starting with "_" as a convention for unused variables.
      "no-unused-vars": ["error", { 
        varsIgnorePattern: "^React$",
        varsIgnorePattern: "^_",
      ...reactPlugin.configs.recommended.rules,
      ...hooksPlugin.configs.recommended.rules,
      "react/react-in-jsx-scope": "off",
      "react/jsx-uses-react": "off",
      "react/prop-types": "off", // Disable prop-types for now
      "no-unused-vars": ["error", { 
        varsIgnorePattern: "^React$|^_",
        argsIgnorePattern: "^_"
      }],
    },
    settings: {
      react: {
        version: "detect",
      },
    },
  },
];