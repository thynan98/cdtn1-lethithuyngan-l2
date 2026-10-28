import { request } from "./client.js";

export const login = (username, password) => request("POST", "/api/auth/login", { body: { username, password } });
