from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import vertexai
from vertexai.generative_models import GenerativeModel, Part
from typing import Dict, Any
import io

app = FastAPI()

# Add CORS middleware with more permissive settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

class AnalysisResult(BaseModel):
    analysis: str
    overall_assessment: str

def initialize_model() -> GenerativeModel:
    vertexai.init(project="fresh-span-400217", location="us-central1")
    return GenerativeModel("gemini-1.5-flash-001")

def load_reference_materials() -> Dict[str, Part]:
    reference_materials = {
        "video": Part.from_uri(
            mime_type="video/mp4",
            uri="gs://ngk-ai/NGK SILKFR8A6 Laser Iridium Spark Plug-Video quick Manual.mp4"
        ),
        "document": Part.from_uri(
            mime_type="application/pdf",
            uri="gs://ngk-ai/NGK SILKFR8A6 Laser Iridium Spark Plug.pdf"
        )
    }
    
    for i in range(1, 23):
        uri = f"gs://ngk-ai/NGK SILKFR8A6 Laser Iridium Spark Plug_Image{i}.jpeg"
        reference_materials[f"reference_image_{i}"] = Part.from_uri(mime_type="image/jpeg", uri=uri)
    
    return reference_materials

def create_anomaly_detection_prompt(uploaded_image: Part, reference_materials: Dict[str, Part]) -> list[Any]:
    prompt = [
        """Analyze the uploaded spark plug image for these major issues:
        1. Black Marks: Look for noticeable black marks or discolorations.
        2. Missing Branding: Check if the "NGK" branding and model number are absent or unreadable.
        3. Missing Parts: Verify all essential parts are present (hexagonal nut, insulator, metal shell, precious metal tip).
        4. Nut Bending: Look for significant bending or distortion of the hexagonal nut.
        5. Tip Condition: Examine the precious metal tip for blur, damage, wear, melting, or deformation.

        For each criterion, state if it's normal or if there's an issue. Describe detected anomalies in detail.
        Provide a summary of all detected major anomalies.
        Conclude with an overall assessment: 'PASS' if no major issues, 'FAIL' if any major issues detected.
        """
    ]
    
    prompt.append(uploaded_image)
    prompt.extend(reference_materials.values())
    with open("prompt.txt", "w") as f:
        f.write(str(prompt))
    
    return prompt

def detect_anomalies(model: GenerativeModel, uploaded_image: Part, reference_materials: Dict[str, Part]) -> AnalysisResult:
    prompt = create_anomaly_detection_prompt(uploaded_image, reference_materials)
    
    generation_config = {
        "max_output_tokens": 2048,
        "temperature": 0.2,
        "top_p": 0.8,
    }
    
    try:
        response = model.generate_content(
            prompt,
            generation_config=generation_config,
        )

        analysis = response.text
        overall_assessment = "PASS" if "PASS" in analysis else "FAIL"

        return AnalysisResult(analysis=analysis, overall_assessment=overall_assessment)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in anomaly detection: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.options("/analyze")
async def options_analyze():
    return {}  # This is needed for CORS preflight requests

@app.post("/analyze/", response_model=AnalysisResult)
async def analyze_spark_plug(file: UploadFile = File(...)):
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded")
    
    try:
        content = await file.read()
        image = io.BytesIO(content)
        
        uploaded_image = Part.from_data(data=image.getvalue(), mime_type=file.content_type)
        
        model = initialize_model()
        reference_materials = load_reference_materials()
        
        analysis_result = detect_anomalies(model, uploaded_image, reference_materials)
        
        return analysis_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)