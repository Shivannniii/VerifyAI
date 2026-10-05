const BASE_URL = (import.meta.env?.VITE_API_URL ?? "").replace(/\/+$/, "");

const TOKEN_KEY = "verifyai_token";

export const getToken = () => localStorage.getItem(TOKEN_KEY);

export const setToken = (token) => localStorage.setItem(TOKEN_KEY, token);

export const clearToken = () => localStorage.removeItem(TOKEN_KEY);

export class ApiError extends Error {
    constructor(message, status) {
        super(message);
        this.name = "ApiError";
        this.status = status;
    }
}

let unauthorizedHandler = null;

export const setUnauthorizedHandler = (handler) => {
    unauthorizedHandler = handler;
};

function errorMessage(data, status) {
    const detail = data?.detail;

    if (typeof detail === "string") {
        return detail;
    }

    if (Array.isArray(detail)) {
        return detail.map((item) => item.msg || "").join(". ");
    }

    return `Request failed (HTTP ${status})`;
}

async function request(
    path,
    {
        method = "GET",
        json,
        formData,
        auth = true,
    } = {}
) {
    const headers = {};
    const token = getToken();

    if (auth && token) {
        headers.Authorization = `Bearer ${token}`;
    }

    let body;

    if (formData) {
        body = formData;
    } else if (json !== undefined) {
        headers["Content-Type"] = "application/json";
        body = JSON.stringify(json);
    }

    let res;

    try {
        // IMPORTANT:
        // BASE_URL already ends with /api
        // so we must NOT add another /api here.
            res = await fetch(`${BASE_URL}${path}`, {
            method,
            headers,
            body,
        });
    } catch {
        throw new ApiError(
            "Cannot reach the server. Please check your internet connection.",
            0
        );
    }

    if (res.status === 204) {
        return null;
    }

    let data = null;

    try {
        data = await res.json();
    } catch {
        // Empty/non-JSON response
    }

    if (!res.ok) {
        if (
            res.status === 401 &&
            auth &&
            token &&
            unauthorizedHandler
        ) {
            unauthorizedHandler();
        }

        throw new ApiError(
            errorMessage(data, res.status),
            res.status
        );
    }

    return data;
}

export const api = {
    // Authentication
    register: (email, password) =>
        request("/auth/register", {
            method: "POST",
            json: {
                email,
                password,
            },
            auth: false,
        }),

    login: (email, password) =>
        request("/auth/login", {
            method: "POST",
            json: {
                email,
                password,
            },
            auth: false,
        }),

    me: () => request("/auth/me"),

    // Research
    listPapers: () => request("/research"),

    uploadPdf: (file) => {
        const formData = new FormData();
        formData.append("file", file);

        return request("/research/upload", {
            method: "POST",
            formData,
        });
    },

    submitText: (text, title) =>
        request("/research/text", {
            method: "POST",
            json: {
                text,
                title: title || null,
            },
        }),

    getPaper: (id) =>
        request(`/research/${id}`),

    getClaims: (id) =>
        request(`/research/${id}/claims`),

    analyze: (id) =>
        request(`/research/${id}/analyze`, {
            method: "POST",
        }),

    deletePaper: (id) =>
        request(`/research/${id}`, {
            method: "DELETE",
        }),

    // Verification
    verifyClaim: (id) =>
        request(`/verification/${id}/verify`, {
            method: "POST",
        }),

    // Detector
    detector: (text) =>
        request("/detector/analyze", {
            method: "POST",
            json: {
                text,
            },
        }),

    detectorFile: (file) => {
        const formData = new FormData();
        formData.append("file", file);

        return request("/detector/analyze-file", {
            method: "POST",
            formData,
        });
    },

    detectorHistory: () =>
        request("/detector/history"),

    // Dashboard
    dashboard: () =>
        request("/dashboard/stats"),

    // Reports
    report: (id) =>
        request(`/research/${id}/report`),

    reportMarkdown: (id) =>
        request(`/research/${id}/report/markdown`),
};