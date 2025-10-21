# 3D Chat App

Trình tạo mô hình 3D qua chat AI. Ứng dụng cho phép bạn nhập mô tả bằng tiếng Việt hoặc tiếng Anh, AI sẽ sinh ra biểu đồ 3D Plotly tương ứng.

## 🚀 Tính Năng

- Chat với AI để tạo mô hình 3D trực quan
- Hỗ trợ tiếng Việt và tiếng Anh
- Giao diện hiện đại, hỗ trợ dark/light mode
- Avatar chatbot, hiệu ứng động UI
- Tùy chỉnh màu sắc, legend, phóng to biểu đồ
- Lưu lịch sử chat (tùy chọn)

## 🛠️ Công Nghệ Sử Dụng

- Frontend: ReactJS, CSS
- Backend: Python, FastAPI, Plotly, Google Gemini API

## 📦 Cài Đặt

### 1. Backend

```bash
cd backend
python main.py
```

### 2. Frontend

```bash
cd frontend
npm install
npm start
```

## ⚙️ Cấu Hình

- Yêu cầu Python >= 3.8, Node.js >= 14
- Tạo file `backend/.env` với nội dung:

```
GOOGLE_API_KEY=your_api_key_here
```

## 💡 Sử Dụng

1. Chạy backend và frontend như hướng dẫn trên.
2. Truy cập `http://localhost:3000` trên trình duyệt.
3. Nhập mô tả (ví dụ: "vẽ một quả cầu", "tạo hình bánh donut", ...).
4. Xem kết quả biểu đồ 3D và tương tác với AI.

## 🤝 Đóng Góp

- Fork repo, tạo pull request với mô tả rõ ràng.
- Mọi ý tưởng, bug report hoặc góp ý UI/UX đều được hoan nghênh!

## 📄 License

MIT License

## 📬 Liên hệ

- Tác giả: An Nguyen
- Email: k4nnguyen@gmail.com
- Github: https://github.com/k4nnguyen/3D-Drawer

---

Nếu có vấn đề khi cài đặt hoặc sử dụng, vui lòng mở issue trên Github hoặc liên hệ trực tiếp.
