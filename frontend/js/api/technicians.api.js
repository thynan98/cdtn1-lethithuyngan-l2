import { request } from "./client.js";

export const listTechnicians = () => request("GET", "/api/technicians");
