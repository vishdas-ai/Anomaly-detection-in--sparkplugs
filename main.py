import vertexai
from vertexai.generative_models import GenerativeModel, Part
from typing import List, Dict, Any
import os

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

def create_refined_anomaly_detection_prompt(uploaded_image: Part, reference_materials: Dict[str, Part]) -> List[Any]:
    prompt = [
        """You are a quality control AI for NGK SILKFR8A6 Laser Iridium Spark Plugs. Your task is to analyze the uploaded image and detect significant anomalies by comparing it to the provided reference images. Focus only on the following major issues:

        1. Black Marks:
           - Look for any noticeable black marks or discolorations that are not present in the reference images.
           - Pay special attention to marker marks, which may appear as intentional black lines or writing on the spark plug.
        2. Missing Branding:
           - Check if the "NGK" branding and model number are completely absent or unreadable.
        3. Missing Parts:
           - Verify that all essential parts of the spark plug are present (hexagonal nut, insulator, metal shell, precious metal tip).
        4. Nut Bending:
           - Look for any significant bending or distortion of the hexagonal nut.
        5. Tip Condition:
           - Examine the precious metal tip carefully.
           - Check if the tip appears blurred, damaged, or significantly different from the reference images.
           - Look for any signs of wear, melting, or deformation at the tip.

        Instructions:
        1. Carefully compare the uploaded image to the reference images.
        2. Flag only the specific issues mentioned above.
        3. For each of the five criteria, state whether it appears normal or if there's an issue.
        4. Describe any detected anomalies in detail.
        5. For black marks, distinguish between unintentional marks and intentional marker marks if possible.
        6. When examining the tip, comment on its clarity, shape, and any signs of wear or damage.
        7. If a feature is unclear in the image, state so explicitly but do not flag it as an anomaly unless you're certain.
        8. Provide a summary of all detected major anomalies.
        9. Conclude with an overall assessment: 'PASS' if none of the specified issues are found, 'FAIL' if any of the five major issues are detected.

        Remember: Only flag issues that clearly fall into one of the five categories mentioned. Do not report on any other types of anomalies or minor imperfections.

        Now, analyze the uploaded spark plug image and report your findings:
        """
    ]
    
    prompt.append(uploaded_image)
    prompt.extend(reference_materials.values())
    
    return prompt

def detect_anomalies(model: GenerativeModel, uploaded_image: Part, reference_materials: Dict[str, Part]) -> str:
    prompt = create_refined_anomaly_detection_prompt(uploaded_image, reference_materials)
    
    generation_config = {
        "max_output_tokens": 2048,
        "temperature": 0.2,
        "top_p": 0.8,
    }
    
    # safety_settings = [
    #     SafetySetting(category=category, threshold=SafetySetting.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE)
    #     for category in [
    #         SafetySetting.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
    #         SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
    #         SafetySetting.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
    #         SafeteSetting.HarmCategory.HARM_CATEGORY_HARASSMENT,
    #     ]
    # ]

    response = model.generate_content(
        prompt,
        generation_config=generation_config,
       
    )

    return response.text

def save_result(result: str, output_dir: str, filename: str):
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, filename), "w") as f:
        f.write(result)

def main(uploaded_image_path: str):
    model = initialize_model()
    reference_materials = load_reference_materials()
    
    uploaded_image = Part.from_uri(mime_type="image/jpeg", uri=uploaded_image_path)
    
    result = detect_anomalies(model, uploaded_image, reference_materials)
    
    output_dir = "spark_plug_analysis_results"
    save_result(result, output_dir, "refined_analysis_result.txt")
    
    print(f"Refined anomaly detection complete. Result saved in {output_dir}/refined_analysis_result.txt")

if __name__ == "__main__":
    # Replace this with the actual path of the uploaded image
    uploaded_image_path = "gs://ngk-ai/NGK-Image2.jpg"
    main(uploaded_image_path)