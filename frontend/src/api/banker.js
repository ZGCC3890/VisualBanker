import axios from "axios";

// 设置 API 基础 URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://zgcc.online/zgcc/api/banker";

export const fetchBankerData = async (n, m) => {
    const response = await axios.post(`${API_BASE_URL}/banker/`, { n, m });
    return response.data;
};
