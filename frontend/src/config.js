const config = {
  // Use relative path for production (when served from the same domain as the backend)
  // For development, we set this to the full backend URL (http://localhost:8000)
  backendBaseUrl:
    import.meta.env.MODE === "development" ? "http://localhost:8000" : "",
};

export default config;
