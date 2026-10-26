const configuredBackendUrl = process.env.REACT_APP_API_BASE_URL || "http://127.0.0.1:8000";

export const BACKEND_BASE_URL = configuredBackendUrl.replace(/\/+$/, "");

export const backendUrl = (path = "") => {
  if (/^https?:\/\//i.test(path)) return path;
  return `${BACKEND_BASE_URL}/${path.replace(/^\/+/, "")}`;
};
