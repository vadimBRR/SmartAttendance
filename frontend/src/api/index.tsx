const API_BASE_URL = "http://127.0.0.1:8000";

export const useGetSubjects = async () => {
  const response = await fetch(`${API_BASE_URL}/subjects/`);
  const data = await response.json();
  return data;
};

export const useGetGroups = async () => {
  const response = await fetch(`${API_BASE_URL}/groups/`);
  const data = await response.json();
  return data;
};




