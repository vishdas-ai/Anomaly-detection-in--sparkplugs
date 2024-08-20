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
        """You are a quality control AI for NGK SILKFR8A6 Laser Iridium Spark Plugs. Your task is to analyze the uploaded image and detect significant anomalies by comparing it to the provided reference images. Focus on identifying major issues such as black marks, extreme scratches, or substantial deviations from the expected appearance. Use the following guidelines for your inspection:

        1. Reference Standard:
           - Use the provided reference images as the benchmark for how a proper spark plug should look.
           - The reference images represent spark plugs without issues or anomalies.

        2. Significant Anomaly Criteria:
           a) Black Marks:
              - Look for any noticeable black marks or discolorations that are not present in the reference images.
           b) Extreme Scratches:
              - Identify any deep or extensive scratches that significantly alter the surface appearance.
           c) Major Deviations:
              - Flag any substantial differences in shape, size, or overall appearance compared to the reference images.

        3. Inspection Areas:
           a) Thread Section:
              - Check for significant damage or deformation of threads.
           b) Hexagonal Nut:
              - Look for major damage or distortion of the hexagonal shape.
           c) Insulator:
              - Identify any large cracks, chips, or major discoloration of the white ceramic.
           d) Branding and Markings:
              - Verify if "NGK" and the model number are clearly visible and not significantly damaged.
           e) Electrodes:
              - Check for obvious misalignment or major damage to the electrodes.
           f) Precious Metal Tip:
              - Verify the presence and general condition of the iridium tip.
           g) Metal Shell:
              - Look for extensive corrosion or major damage to the metal shell.

        Instructions:
        1. Carefully compare the uploaded image to the reference images.
        2. Flag only significant anomalies that clearly deviate from the reference standard.
        3. For each inspection area, state whether it appears normal or if there's a major anomaly.
        4. Describe any detected significant anomalies in detail.
        5. If a feature is unclear in the image, state so explicitly but do not flag it as an anomaly unless you're certain.
        6. Provide a summary of all detected major anomalies.
        7. Conclude with an overall assessment: 'PASS' if no significant anomalies are found, 'FAIL' if major issues are detected.

        Remember: Focus on identifying clear and significant issues. Minor variations or imperfections that are within the range seen in reference images should not be flagged as anomalies.

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
    uploaded_image_path = "gs://ngk-ai/a.png"
    main(uploaded_image_path)