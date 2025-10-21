import os
import uvicorn
import numpy as np
import plotly.graph_objects as go
import google.generativeai as genai
import re
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# --- Cấu hình ---
# Vui lòng tạo file .env trong thư mục backend và thêm GOOGLE_API_KEY="KEY_CUA_BAN"
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

if API_KEY:
    genai.configure(api_key=API_KEY)
else:
    print("CẢNH BÁO: Biến môi trường GOOGLE_API_KEY không được tìm thấy.")

app = FastAPI()

# --- Cấu hình CORS ---
origins = [
    "http://localhost",
    "http://localhost:3000",
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
# Sử dụng model gemini-2.5-flash theo yêu cầu
gemini_model = genai.GenerativeModel('gemini-2.5-flash') if API_KEY else None

# Hàm để trích xuất code Python từ text của AI
def extract_python_code(text):
    match = re.search(r"```python\n(.*?)\n```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None

# --- Trang trí Figure để đẹp và chi tiết hơn ---
def beautify_figure(fig: go.Figure) -> go.Figure:
    """Áp dụng style tối nhẹ, chữ rõ, legend sáng và cân bằng."""
    fig.update_layout(
        template="plotly_dark",
        autosize=True,
        margin=dict(l=10, r=10, b=10, t=40),
        showlegend=True,
        legend=dict(
            bgcolor="rgba(240,240,240,0.8)",  # nền sáng nhẹ, hơi mờ
            bordercolor="rgba(0,0,0,0.2)",
            borderwidth=1,
            x=0.02,
            y=0.98,
            font=dict(
                family="Segoe UI, Inter, Roboto, Arial, sans-serif",
                size=13,
                color="#111",  # chữ đen
            ),
        ),
        font=dict(
            family="Segoe UI, Inter, Roboto, Arial, sans-serif",
            size=14,
            color="#000000",  # màu chữ chung (sáng)
        ),
        colorway=[
            "#4E79A7", "#F28E2B", "#E15759", "#76B7B2", "#59A14F",
            "#EDC948", "#B07AA1", "#FF9DA7", "#9C755F", "#BAB0AC",
        ],
        paper_bgcolor="#1E1E1E",  # nền tổng thể tối nhẹ
        plot_bgcolor="#262626",
        hovermode="closest",
    )

    return fig


def finalize_figure(fig: go.Figure) -> go.Figure:
    """Thêm legend và áp dụng style cho figure."""
    if fig and isinstance(fig, go.Figure):
        # 🔹 Bổ sung legend nếu thiếu
        for i, tr in enumerate(fig.data):
            if not getattr(tr, "name", None):
                tr.name = f"Trace {i+1}"
            tr.showlegend = True  # ép hiển thị

        # 🔹 Áp dụng style tối nhẹ, legend sáng chữ đen
        fig = beautify_figure(fig)

        # 🔹 Đảm bảo legend luôn nổi bật trên nền tối
        fig.update_layout(
            legend=dict(
                bgcolor="rgba(240,240,240,0.85)",  # nền sáng hơn để chữ đen rõ
                bordercolor="rgba(0,0,0,0.2)",
                borderwidth=1,
                font=dict(color="#111", size=13, family="Inter, sans-serif"),
            ),
        )

        return fig
    else:
        return None

# --- Logic chính của API ---
@app.post("/generate-plot")
async def generate_plot(request: PromptRequest):
    if not gemini_model:
        raise HTTPException(status_code=500, detail="API Key của Google chưa được cấu hình trên server.")

    print(f"Nhận được prompt: {request.prompt}")
    system_prompt = f"""
    Bạn là một trợ lý tạo mã Python để vẽ hình khối, vật thể 3D bằng Plotly.

    QUY TẮC:
    1. CHỈ trả về mã Python trong khối ```python ... ```.
    2. KHÔNG giải thích, chỉ cần code.
    3. Import cần thiết: plotly.graph_objects as go, numpy as np.
    4. Tạo đối tượng `fig = go.Figure(...)`.
    5. Không gọi `fig.show()`.
    6. Yêu cầu cần phải tạo cả legend đầy đủ, chữ của legend cần là màu trắng và in đậm.
    7. Yêu cầu với các khối cần đặt trên một nền đen, ngoài ra cũng cần có các lưới màu trắng theo trục X và Y để có thể tương phản.
    8. Yêu cầu phần trục nên có các số là chiều cao và dài để giống đồ thị.
    9. Với các loại hình học: Hình tròn, hình tam giác, hình hộp, ... Thì sẽ phải vẽ ra khối 3D của nó.
    10. Các loại hình khối nên là khối đặc, lớp ngoài không có trong suốt, vẽ các khối nên đổ bóng để nhìn cho dễ.
    Yêu cầu: "{request.prompt}"
    """
    try:
        print("Đang gọi Gemini API để tạo code...")
        response = gemini_model.generate_content(
            system_prompt,
            safety_settings={
                'HARM_CATEGORY_HARASSMENT': 'BLOCK_NONE',
                'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_NONE',
                'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_NONE',
                'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_NONE',
            }
        )
        
        try:
            generated_code_raw = response.text
        except ValueError:
            finish_reason = "UNKNOWN"
            if response.candidates and response.candidates[0].finish_reason:
                finish_reason = response.candidates[0].finish_reason.name
            error_message = f"Phản hồi của AI bị chặn. Lý do: {finish_reason}. Vui lòng thử một prompt khác."
            raise HTTPException(status_code=400, detail=error_message)

        generated_code = extract_python_code(generated_code_raw)
        
        if not generated_code:
             raise HTTPException(status_code=400, detail="AI không tạo ra được mã Python hợp lệ hoặc không có trong phản hồi.")

        print("--- Mã được tạo bởi AI ---")
        print(generated_code)
        print("--------------------------")
        
        local_scope = {}
        exec(generated_code, {"go": go, "np": np}, local_scope)
        fig = local_scope.get("fig")

        if fig and isinstance(fig, go.Figure):
            # Trang trí lại để đảm bảo nhất quán và đẹp
            fig = finalize_figure(fig)
            print("Thực thi mã thành công, đang chuyển đổi Figure sang HTML...")
            config = dict(
                responsive=True,
                displaylogo=False,
                scrollZoom=True,
                toImageButtonOptions=dict(scale=2, filename="3d-plot"),
                modeBarButtonsToRemove=["lasso2d", "select2d", "toggleSpikelines"],
            )
            plot_html = fig.to_html(full_html=False, include_plotlyjs='cdn', config=config)
            # Trả về cả code Python cho frontend
            return {
                "html": plot_html,
                "code": generated_code,
                "code_type": "python"
            }
        else:
            raise HTTPException(status_code=400, detail="Mã do AI tạo ra không hợp lệ hoặc không tạo ra đối tượng 'fig'.")

    except Exception as e:
        print(f"Đã xảy ra lỗi: {e}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Lỗi máy chủ nội bộ: {str(e)}")

if __name__ == "__main__":
    print("Khởi động server tại http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)



