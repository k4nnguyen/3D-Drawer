import os
import uvicorn
import numpy as np
import plotly.graph_objects as go
import google.generativeai as genai
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# --- Cấu hình ---
# Lấy API Key từ biến môi trường
# Hãy tạo một file .env và đặt GOOGLE_API_KEY="YOUR_API_KEY" vào đó
# Hoặc thay thế os.getenv("GOOGLE_API_KEY") bằng key của bạn trực tiếp
# Ví dụ: genai.configure(api_key="AIza...")
try:
    from dotenv import load_dotenv
    load_dotenv()
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
except ImportError:
    print("Thư viện python-dotenv chưa được cài. Hãy chạy: pip install python-dotenv")
    # Cấu hình thủ công nếu không có dotenv
    # genai.configure(api_key="YOUR_API_KEY_HERE")


app = FastAPI()

# --- Cấu hình CORS ---
# Cho phép frontend React (chạy trên port khác) gọi đến API này
origins = [
    "http://localhost",
    "http://localhost:3000", # Port mặc định của React
    "http://localhost:5173", # Port mặc định của Vite
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Model để nhận dữ liệu từ frontend ---
class PromptRequest(BaseModel):
    prompt: str

# --- Cấu hình mô hình AI ---
generation_config = {
  "temperature": 0.4,
  "top_p": 1,
  "top_k": 32,
  "max_output_tokens": 4096,
}
gemini_model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)

# --- Logic chính của API ---
@app.post("/generate-plot")
async def generate_plot(request: PromptRequest):
    """
    Nhận prompt, dùng AI để tạo code Plotly, thực thi và trả về HTML.
    """
    print(f"Nhận được prompt: {request.prompt}")

    # Prompt chỉ dẫn cho AI
    system_prompt = f"""
    Bạn là một chuyên gia Python chuyên về thư viện Plotly. Nhiệm vụ của bạn là tạo mã Python để tạo ra một hình ảnh 3D dựa trên prompt của người dùng.
    YÊU CẦU BẮT BUỘC:
    1. Chỉ được phép sử dụng thư viện `plotly.graph_objects as go` và `numpy as np`.
    2. Mã phải tạo ra một đối tượng `go.Figure` duy nhất có tên là `fig`.
    3. KHÔNG được gọi `fig.show()` hay `fig.write_html()`.
    4. Chỉ trả về phần mã Python, không giải thích gì thêm.
    5. Dòng cuối cùng của mã PHẢI là biến `fig`.

    Ví dụ prompt của người dùng: 'vẽ một quả cầu màu xanh'
    Kết quả bạn trả về:
    import plotly.graph_objects as go
    import numpy as np
    center = np.array([0, 0, 0])
    radius = 1.0
    num_segments = 20
    u = np.linspace(0, 2 * np.pi, num_segments)
    v = np.linspace(0, np.pi, num_segments)
    U, V = np.meshgrid(u, v)
    sphere_x = center[0] + radius * np.cos(U) * np.sin(V)
    sphere_y = center[1] + radius * np.sin(U) * np.sin(V)
    sphere_z = center[2] + radius * np.cos(V)
    fig = go.Figure(data=[go.Surface(x=sphere_x, y=sphere_y, z=sphere_z, colorscale='Blues', showscale=False, opacity=0.9)])
    fig.update_layout(title='Quả cầu 3D', scene_aspectmode='data')
    fig
    """

    try:
        # Gọi Gemini API
        print("Đang gọi Gemini API để tạo code...")
        response = gemini_model.generate_content([system_prompt, request.prompt])
        generated_code = response.text

        # Dọn dẹp mã trả về từ AI (loại bỏ ```python và ```)
        if generated_code.strip().startswith("```python"):
            generated_code = generated_code.strip()[9:]
        if generated_code.strip().endswith("```"):
            generated_code = generated_code.strip()[:-3]

        print("--- Mã được tạo bởi AI ---")
        print(generated_code)
        print("--------------------------")
        
        # Thực thi mã một cách an toàn
        local_scope = {}
        exec(generated_code, {"go": go, "np": np}, local_scope)

        fig = local_scope.get("fig")

        if fig and isinstance(fig, go.Figure):
            print("Thực thi mã thành công, đang chuyển đổi Figure sang HTML...")
            # Chuyển đổi Figure sang HTML, không bao gồm thẻ <html>, <body>
            # và dùng CDN để giảm kích thước payload
            plot_html = fig.to_html(
                full_html=False,
                include_plotlyjs='cdn'
            )
            return {"html": plot_html}
        else:
            return {"error": "Mã được tạo không tạo ra đối tượng 'fig' hợp lệ."}, 500

    except Exception as e:
        print(f"Đã xảy ra lỗi: {e}")
        return {"error": f"Đã xảy ra lỗi trong quá trình xử lý: {str(e)}"}, 500

if __name__ == "__main__":
    print("Khởi động server tại http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)
