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

def create_strict_anomaly_detection_prompt(uploaded_image: Part, reference_materials: Dict[str, Part]) -> List[Any]:
    prompt = [
        """You are an extremely meticulous quality control AI for NGK SILKFR8A6 Laser Iridium Spark Plugs. Your task is to analyze the uploaded image with utmost scrutiny and detect ANY deviation from perfect condition, no matter how minor. Even the slightest imperfection should be flagged as an anomaly. Use the following guidelines for your inspection:

        1. Perfection Standard:
           - The spark plug must be in absolutely perfect condition.
           - ANY scratch, mark, discoloration, or deviation from ideal specifications is an anomaly.

        2. Comprehensive Inspection Areas:
           a) Thread Section:
              - Exactly 18-19 threads, perfectly clean and uniformly spaced.
              - No signs of wear, damage, or cross-threading.
           b) Hexagonal Nut:
              - Perfect hexagonal shape with sharp, undamaged edges.
              - No signs of tool marks or wear.
           c) Insulator:
              - Pristine white ceramic with no discoloration, chips, or cracks.
              - Perfectly attached to the metal shell with no gaps or misalignment.
           d) Branding and Markings:
              - "NGK" must be clearly written in perfect light blue.
              - Model number (SILKFR8A6) must be crisp and fully legible.
              - All markings must be perfectly aligned and undamaged.
           e) Electrodes:
              - Center and ground electrodes must be in perfect alignment.
              - No signs of wear, erosion, or discoloration.
              - Gap must appear precise and uniform.
           f) Precious Metal Tip:
              - Iridium tip must be perfectly formed, fine, and pointed.
              - No signs of wear or deformation.
           g) Seal Ring:
              - Must be present, perfectly seated, and undamaged.
              - No signs of compression or deformation.
           h) Metal Shell:
              - Absolutely no corrosion, scratches, or marks.
              - Plating or coating must be perfectly uniform.
           i) Overall Dimensions and Proportions:
              - Must appear exactly consistent with specifications.
           j) Manufacturing Quality:
              - No signs of poor assembly, misalignments, or residues.
           k) Packaging (if visible):
              - Must be pristine, undamaged, and properly sealed.

        Instructions:
        1. Analyze the uploaded image with extreme attention to detail.
        2. Compare against the provided reference materials meticulously.
        3. Flag ANY deviation from perfect condition as an anomaly, no matter how minor.
        4. For each inspection area, clearly state whether it's perfect or if there's an anomaly.
        5. Describe ALL detected anomalies in detail, no matter how small.
        6. If you can't clearly see any feature, state so explicitly and consider it a potential anomaly.
        7. Provide a summary of ALL detected anomalies, even if they seem insignificant.
        8. Conclude with an overall assessment: 'PASS' only if absolutely perfect, otherwise 'FAIL'.

        Remember: Your role is to ensure only absolutely perfect spark plugs pass inspection. Be extremely strict and flag even the slightest imperfections.

        Now, analyze the uploaded spark plug image and report your findings:
        """
    ]
    
    prompt.append(uploaded_image)
    prompt.extend(reference_materials.values())
    
    return prompt

def detect_anomalies(model: GenerativeModel, uploaded_image: Part, reference_materials: Dict[str, Part]) -> str:
    prompt = create_strict_anomaly_detection_prompt(uploaded_image, reference_materials)
    
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
        generation_config=generation_config
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
    save_result(result, output_dir, "strict_analysis_result.txt")
    
    print(f"Strict anomaly detection complete. Result saved in {output_dir}/strict_analysis_result.txt")

if __name__ == "__main__":
    # Replace this with the actual path of the uploaded image
    uploaded_image_path = "gs://ngk-ai/NGK-Image2.jpg"
    main(uploaded_image_path)

# if __name__ == "__main__":
#     # Replace this with the actual path of the uploaded image
#     uploaded_image_path = "gs://ngk-ai/NGK-Image2.jpg"
#     main(uploaded_image_path)