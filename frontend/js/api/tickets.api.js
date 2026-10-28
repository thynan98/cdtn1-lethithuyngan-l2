import { request } from "./client.js";

export const listTickets = (query) => request("GET", "/api/tickets", { query });
export const getTicket = (id) => request("GET", `/api/tickets/${id}`);
export const createTicket = (body) => request("POST", "/api/tickets", { body });
export const setCategory = (id, categoryId) => request("PATCH", `/api/tickets/${id}/category`, { body: { category_id: categoryId } });
export const assignTechnician = (id, technicianId) => request("PATCH", `/api/tickets/${id}/technician`, { body: { technician_id: technicianId } });
export const changeStatus = (id, status) => request("PATCH", `/api/tickets/${id}/status`, { body: { status } });
export const deleteTicket = (id) => request("DELETE", `/api/tickets/${id}`);
export const listCategories = () => request("GET", "/api/issue-categories");
export const findCustomer = (phone) => request("GET", "/api/customers", { query: { phone } });
export const getOverview = () => request("GET", "/api/overview");
