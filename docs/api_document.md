# Tài Liệu API (API Document) - Visual Agent

Tài liệu này cung cấp chi tiết về các điểm cuối (Endpoints) API được cung cấp bởi FastAPI backend của dự án **Visual Agent**. Các API này phục vụ cho việc giao tiếp giữa Frontend và Backend.

Địa chỉ chạy mặc định của Backend: `http://127.0.0.1:8300`

---

## 1. Thông Tin Chung (Global Configurations)
- **Base URL**: `/api`
- **Định dạng dữ liệu**: `application/json` (đối với hầu hết các request và response, ngoại trừ API Upload tệp tin dùng `multipart/form-data`).

---

## 2. Danh Sách API chi tiết

### 2.1. Kiểm Tra Trạng Thái Hệ Thống (Health Check)
Dùng để kiểm tra trạng thái hoạt động của server và các thông tin telemetry về cấu hình model hiện tại.

- **Endpoint**: `/api/health`
- **Method**: `GET`
- **Response Model**: `HealthResponse`
- **Response Example (`200 OK`)**:
```json
{
  "status": "ok",
  "llm_provider": "ollama",
  "vlm_provider": "ollama",
  "text_model": "llama3.2:3b",
  "vision_model": "llama3.2-vision",
  "yolo_model_path": "/Users/phamtunglam/Documents/Projects/visual-agent/yolo11x.pt",
  "yolo_model_exists": true
}
```

---

### 2.2. Lấy Cấu Hình Của Hệ Thống (Get Provider Settings)
Lấy cấu hình hiện tại của các mô hình và trạng thái của các API key (chỉ trả về việc đã thiết lập key hay chưa, không trả về giá trị thô để bảo mật).

- **Endpoint**: `/api/settings`
- **Method**: `GET`
- **Response Model**: `ProviderSettingsResponse`
- **Response Example (`200 OK`)**:
```json
{
  "llm_provider": "ollama",
  "vlm_provider": "ollama",
  "ollama_text_model": "llama3.2:3b",
  "ollama_vision_model": "llama3.2-vision",
  "openai_text_model": "gpt-4.1-nano",
  "openai_vision_model": "gpt-4o-mini",
  "gemini_text_model": "gemini-2.5-flash",
  "gemini_vision_model": "gemini-2.5-flash",
  "has_openai_api_key": true,
  "has_gemini_api_key": false
}
```

---

### 2.3. Cập Nhật Cấu Hình Hệ Thống (Save Provider Settings)
Cập nhật nhà cung cấp dịch vụ LLM/VLM, thay đổi tên mô hình hoặc lưu các API keys vào tệp cấu hình `.env` cục bộ.

- **Endpoint**: `/api/settings`
- **Method**: `POST`
- **Request Model**: `ProviderSettingsRequest`
- **Request Body Fields**:
  - `llm_provider` (string): `"ollama" | "openai" | "gemini"` (Bắt buộc)
  - `vlm_provider` (string): `"ollama" | "openai" | "gemini"` (Bắt buộc)
  - `ollama_text_model` (string, min_length=1) (Bắt buộc)
  - `ollama_vision_model` (string, min_length=1) (Bắt buộc)
  - `openai_text_model` (string, min_length=1) (Bắt buộc)
  - `openai_vision_model` (string, min_length=1) (Bắt buộc)
  - `gemini_text_model` (string, min_length=1) (Bắt buộc)
  - `gemini_vision_model` (string, min_length=1) (Bắt buộc)
  - `openai_api_key` (string | null): Key mới để lưu (Tùy chọn)
  - `gemini_api_key` (string | null): Key mới để lưu (Tùy chọn)
- **Response Model**: `ProviderSettingsResponse`
- **Request Example**:
```json
{
  "llm_provider": "openai",
  "vlm_provider": "openai",
  "ollama_text_model": "llama3.2:3b",
  "ollama_vision_model": "llama3.2-vision",
  "openai_text_model": "gpt-4o",
  "openai_vision_model": "gpt-4o-mini",
  "gemini_text_model": "gemini-2.5-flash",
  "gemini_vision_model": "gemini-2.5-flash",
  "openai_api_key": "sk-proj-...",
  "gemini_api_key": null
}
```
- **Response Example (`200 OK`)**:
```json
{
  "llm_provider": "openai",
  "vlm_provider": "openai",
  "ollama_text_model": "llama3.2:3b",
  "ollama_vision_model": "llama3.2-vision",
  "openai_text_model": "gpt-4o",
  "openai_vision_model": "gpt-4o-mini",
  "gemini_text_model": "gemini-2.5-flash",
  "gemini_vision_model": "gemini-2.5-flash",
  "has_openai_api_key": true,
  "has_gemini_api_key": false
}
```
- **Error Responses**:
  - `400 Bad Request`: Thiếu API key khi chọn provider tương ứng hoặc để trống tên model.

---

### 2.4. Tải Ảnh Lên Server (Upload Image)
Tải tệp tin ảnh lên để hệ thống có thể phân tích thông qua đường dẫn local. Chỉ chấp nhận các tệp định dạng ảnh phổ biến (`PNG`, `JPG/JPEG`, `WEBP`) và giới hạn kích thước tối đa 20MB.

- **Endpoint**: `/api/upload`
- **Method**: `POST`
- **Content-Type**: `multipart/form-data`
- **Payload**:
  - `file`: Đối tượng File ảnh (Bắt buộc)
- **Response Model**: `UploadResponse`
- **Response Example (`200 OK`)**:
```json
{
  "file_name": "76ba3f6e1f0e4b8686d638ba4a77d12f.jpg",
  "path": "/Users/phamtunglam/Documents/Projects/visual-agent/data/uploads/76ba3f6e1f0e4b8686d638ba4a77d12f.jpg",
  "url": "/uploads/76ba3f6e1f0e4b8686d638ba4a77d12f.jpg"
}
```
- **Error Responses**:
  - `400 Bad Request`: Tệp không phải là ảnh hoặc định dạng đuôi file không hợp lệ.
  - `413 Request Entity Too Large`: File ảnh vượt quá kích thước cho phép.

---

### 2.5. Trò Chuyện Tích Hợp (Chat Router)
Đây là API chính nhận prompt từ người dùng và định tuyến tự động giữa các module Research, Vision, hoặc chạy đồng thời cả hai.

- **Endpoint**: `/api/chat`
- **Method**: `POST`
- **Request Model**: `ChatRequest`
- **Request Body Fields**:
  - `message` (string, min_length=1): Nội dung văn bản trò chuyện (Bắt buộc)
  - `mode` (string): `"auto" | "research" | "vision"` (Mặc định là `"auto"`)
  - `image_path_or_url` (string | null): Đường dẫn local của ảnh đã được upload hoặc URL ảnh từ web (Tùy chọn)
- **Response Model**: `ChatResponse`
- **Request Example**:
```json
{
  "message": "Có bao nhiêu người trong ảnh này?",
  "mode": "auto",
  "image_path_or_url": "/Users/phamtunglam/Documents/Projects/visual-agent/data/uploads/76ba3f6e1f0e4b8686d638ba4a77d12f.jpg"
}
```
- **Response Example (`200 OK` - Phân tích & Đếm với YOLO)**:
```json
{
  "route": "vision.detect",
  "answer": "Phát hiện 3 đối tượng `person` trong ảnh.",
  "sources": {},
  "artifacts": {
    "image_path_or_url": "/Users/phamtunglam/Documents/Projects/visual-agent/data/uploads/76ba3f6e1f0e4b8686d638ba4a77d12f.jpg",
    "counts": {
      "person": 3
    },
    "detections": [
      {
        "label": "person",
        "confidence": 0.8845,
        "bbox": [120, 50, 320, 480]
      },
      {
        "label": "person",
        "confidence": 0.9123,
        "bbox": [310, 80, 500, 470]
      },
      {
        "label": "person",
        "confidence": 0.7654,
        "bbox": [480, 110, 620, 450]
      }
    ],
    "annotated_url": "/uploads/annotated-d4c5e6f7g8h9.jpg"
  }
}
```
- **Response Example (`200 OK` - Tổng hợp Nghiên cứu khoa học)**:
```json
{
  "route": "research",
  "answer": "Rotary Positional Embeddings (RoPE), introduced in the RoFormer paper by Su et al. (2021), encodes positional information by multiplying representation vectors with a rotation matrix...",
  "sources": {
    "wikipedia": "Wikipedia search results for Rotary Positional Encoding...",
    "arxiv": "Published: 2021-04-12\nTitle: RoFormer: Enhanced Transformer with Rotary Position Embedding..."
  },
  "artifacts": {}
}
```

---

### 2.6. Tìm Kiếm Nghiên Cứu Độc Lập (Direct Research)
Gọi trực tiếp dịch vụ tra cứu Wikipedia & arXiv mà không thông qua bộ lọc định tuyến.

- **Endpoint**: `/api/research`
- **Method**: `POST`
- **Request Model**: `ResearchRequest`
- **Request Body Fields**:
  - `query` (string, min_length=1): Nội dung cần tìm kiếm (Bắt buộc)
- **Response Model**: `ChatResponse`
- **Request Example**:
```json
{
  "query": "RoFormer rotary embeddings"
}
```

---

### 2.7. Mô Tả Ảnh Độc Lập (Direct Vision Describe)
Gọi trực tiếp dịch vụ mô tả ảnh (VLM) mà không kiểm tra xem có yêu cầu nhận diện/đếm đối tượng hay không.

- **Endpoint**: `/api/vision/describe`
- **Method**: `POST`
- **Request Model**: `VisionRequest`
- **Request Body Fields**:
  - `image_path_or_url` (string, min_length=1): Đường dẫn hoặc URL ảnh (Bắt buộc)
  - `prompt` (string): Câu lệnh mô tả ảnh (Mặc định: `"Describe this image."`)
- **Response Model**: `ChatResponse`
- **Request Example**:
```json
{
  "image_path_or_url": "./data/uploads/image.png",
  "prompt": "What color is the sky in this picture?"
}
```

---

### 2.8. Nhận Diện & Đếm Ảnh Độc Lập (Direct Vision Detection)
Gọi trực tiếp dịch vụ nhận diện và đếm đối tượng sử dụng YOLOv11.

- **Endpoint**: `/api/vision/detect`
- **Method**: `POST`
- **Request Model**: `DetectionRequest`
- **Request Body Fields**:
  - `image_path_or_url` (string, min_length=1): Đường dẫn hoặc URL ảnh (Bắt buộc)
  - `prompt` (string): Câu lệnh đếm (Mặc định: `"Detect and count objects."`)
- **Response Model**: `ChatResponse`
- **Request Example**:
```json
{
  "image_path_or_url": "./data/uploads/image.png",
  "prompt": "count dogs"
}
```
