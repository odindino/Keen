/// <reference types="vite/client" />

declare module 'plotly.js-dist-min'

declare global {
  interface Window {
    pywebview: {
      api: any
    }
  }
}
