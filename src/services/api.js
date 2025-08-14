// src/api.js
import axios from 'axios';
import { createBrowserHistory } from 'history';

const history = createBrowserHistory();

const API = axios.create({
  baseURL: process.env.REACT_APP_API_URL,
});


API.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error?.response?.status === 401) {
      sessionStorage.removeItem("token");
      history.push("/login");
    }
    return Promise.reject(error);
  }
);

export default API;
