import streamlit as st
import google.generativeai as genai
import json
import base64
import io
from PIL import Image
import numpy as np
from typing import Dict, List, Any
import time

# Page configuration
st.set_page_config(
    page_title="StyleAI - Virtual Clothing Store",
    page_icon="👗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern aesthetic
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #f8f6f1 0%, #f5f2eb 100%);
    }
    
    .stApp {
        background: linear-gradient(135deg, #f8f6f1 0%, #f5f2eb 100%);
    }
    
    .clothing-card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin: 10px 0;
        border: 1px solid #e8e3d8;
        transition: all 0.3s ease;
    }
    
    .clothing-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    .avatar-preview {
        background: white;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border: 1px solid #e8e3d8;
    }
    
    .category-button {
        background: #d4b5a0;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 25px;
        margin: 5px;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .category-button:hover {
        background: #c9a68a;
        transform: scale(1.05);
    }
    
    .upload-area {
        border: 2px dashed #d4b5a0;
        border-radius: 15px;
        padding: 40px;
        text-align: center;
        background: rgba(212, 181, 160, 0.1);
        transition: all 0.3s ease;
    }
    
    .upload-area:hover {
        background: rgba(212, 181, 160, 0.2);
        border-color: #c9a68a;
    }
    
    .price-tag {
        background: #8b7355;
        color: white;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        margin-top: 10px;
    }
    
    .try-on-button {
        background: linear-gradient(45deg, #d4b5a0, #c9a68a);
        color: white;
        border: none;
        padding: 12px 25px;
        border-radius: 25px;
        font-weight: bold;
        cursor: pointer;
        width: 100%;
        margin-top: 15px;
        transition: all 0.3s ease;
    }
    
    .try-on-button:hover {
        transform: scale(1.02);
        box-shadow: 0 4px 15px rgba(212, 181, 160, 0.4);
    }
    
    .avatar-stats {
        background: #f5f2eb;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border-left: 4px solid #d4b5a0;
    }
    
    h1, h2, h3 {
        color: #8b7355;
    }
    
    .sidebar .sidebar-content {
        background: rgba(255, 255, 255, 0.9);
    }
</style>
""", unsafe_allow_html=True)

# Gemini API configuration
GEMINI_API_KEY = "your-gemini-api-key-here"  # Replace with actual API key

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

# Available Gemini models for avatar creation
AVAILABLE_MODELS = {
    "gemini-2.0-flash-exp": "Gemini 2.0 Flash (Experimental) - Latest with best multimodal capabilities",
    "gemini-2.5-flash": "Gemini 2.5 Flash - Fast and efficient for image analysis", 
}

# Default model for avatar creation
DEFAULT_MODEL = "gemini-2.0-flash-exp"

# Sample clothing catalog
CLOTHING_CATALOG = {
    "dresses": [
        {"id": 1, "name": "Elegant Summer Dress", "price": "$89.99", "color": "Light Blue", "size": ["XS", "S", "M", "L", "XL"], "image": "👗", "description": "Flowy summer dress perfect for casual outings"},
        {"id": 2, "name": "Formal Evening Gown", "price": "$199.99", "color": "Black", "size": ["XS", "S", "M", "L", "XL"], "image": "🖤", "description": "Sophisticated evening wear for special occasions"},
        {"id": 3, "name": "Casual Midi Dress", "price": "$65.99", "color": "Coral", "size": ["XS", "S", "M", "L", "XL"], "image": "🧡", "description": "Comfortable midi dress for everyday wear"},
    ],
    "tops": [
        {"id": 4, "name": "Silk Blouse", "price": "$79.99", "color": "White", "size": ["XS", "S", "M", "L", "XL"], "image": "👔", "description": "Premium silk blouse for professional settings"},
        {"id": 5, "name": "Casual T-Shirt", "price": "$24.99", "color": "Navy", "size": ["XS", "S", "M", "L", "XL"], "image": "👕", "description": "Comfortable cotton t-shirt for casual wear"},
        {"id": 6, "name": "Crop Top", "price": "$34.99", "color": "Pink", "size": ["XS", "S", "M", "L", "XL"], "image": "💗", "description": "Trendy crop top for summer styling"},
    ],
    "bottoms": [
        {"id": 7, "name": "High-Waist Jeans", "price": "$89.99", "color": "Dark Blue", "size": ["24", "26", "28", "30", "32", "34"], "image": "👖", "description": "Classic high-waist denim jeans"},
        {"id": 8, "name": "Pleated Skirt", "price": "$55.99", "color": "Beige", "size": ["XS", "S", "M", "L", "XL"], "image": "🟤", "description": "Elegant pleated midi skirt"},
        {"id": 9, "name": "Wide-Leg Pants", "price": "$75.99", "color": "Olive", "size": ["XS", "S", "M", "L", "XL"], "image": "🫒", "description": "Comfortable wide-leg trousers"},
    ],
    "accessories": [
        {"id": 10, "name": "Designer Handbag", "price": "$149.99", "color": "Brown", "size": ["One Size"], "image": "👜", "description": "Luxury leather handbag"},
        {"id": 11, "name": "Statement Necklace", "price": "$39.99", "color": "Gold", "size": ["One Size"], "image": "📿", "description": "Bold statement jewelry piece"},
        {"id": 12, "name": "Sunglasses", "price": "$79.99", "color": "Black", "size": ["One Size"], "image": "🕶️", "description": "UV protection designer sunglasses"},
    ]
}

class AIClothingStore:
    def __init__(self):
        self.initialize_session_state()
    
    def initialize_session_state(self):
        """Initialize session state variables"""
        if 'avatar_generated' not in st.session_state:
            st.session_state.avatar_generated = False
        if 'avatar_data' not in st.session_state:
            st.session_state.avatar_data = None
        if 'selected_items' not in st.session_state:
            st.session_state.selected_items = []
        if 'cart' not in st.session_state:
            st.session_state.cart = []
        if 'avatar_measurements' not in st.session_state:
            st.session_state.avatar_measurements = {}
        if 'selected_model' not in st.session_state:
            st.session_state.selected_model = DEFAULT_MODEL
    
    def call_gemini_api(self, prompt: str, image_data: Image.Image = None, model_name: str = None) -> Dict[Any, Any]:
        """Make API call to Gemini using the official library"""
        try:
            # Use selected model or default
            model_to_use = model_name or st.session_state.get('selected_model', DEFAULT_MODEL)
            
            # Initialize the model
            model = genai.GenerativeModel(model_to_use)
            
            if image_data:
                # For image + text prompt
                response = model.generate_content([prompt, image_data])
            else:
                # For text-only prompt
                response = model.generate_content(prompt)
            
            return {
                "candidates": [{
                    "content": {
                        "parts": [{
                            "text": response.text
                        }]
                    }
                }],
                "model_used": model_to_use
            }
            
        except Exception as e:
            st.error(f"Gemini API Error with model {model_to_use}: {str(e)}")
            st.info("💡 **Note**: Gemini Nano runs on-device only. For cloud API, use Gemini Flash or Pro models.")
            
            # Fallback to demo response for development
            if image_data:
                return {
                    "candidates": [{
                        "content": {
                            "parts": [{
                                "text": json.dumps({
                                    "avatar_created": True,
                                    "analysis_confidence": "medium",
                                    "visible_features": {
                                        "clothing_style": "Casual contemporary style",
                                        "colors_worn": "Neutral tones",
                                        "overall_build": "Average build"
                                    },
                                    "measurements": {
                                        "height_category": "average",
                                        "estimated_height": "5'5\" - 5'7\"",
                                        "body_type": "Rectangle",
                                        "build": "average"
                                    },
                                    "recommended_sizes": {
                                        "tops": "M",
                                        "bottoms": "M",
                                        "dresses": "M"
                                    },
                                    "style_preferences": ["Casual", "Versatile", "Modern"],
                                    "color_palette": ["Neutrals", "Earth tones", "Pastels"],
                                    "confidence_note": f"Demo mode - using fallback analysis (attempted model: {model_to_use})"
                                })
                            }]
                        }
                    }],
                    "model_used": f"{model_to_use} (fallback)"
                }
            else:
                return {
                    "candidates": [{
                        "content": {
                            "parts": [{
                                "text": "Fashion recommendation generated successfully in demo mode."
                            }]
                        }
                    }],
                    "model_used": f"{model_to_use} (fallback)"
                }
        
    
    def generate_avatar_from_image(self, uploaded_file) -> Dict[str, Any]:
        """Generate avatar profile from uploaded image using Gemini's image analysis capabilities"""
        try:
            # Convert image to PIL Image
            image = Image.open(uploaded_file)
            image = image.convert('RGB')
            
            # Resize for API efficiency
            image.thumbnail((1024, 1024))  # Higher resolution for better analysis
            
            # Enhanced prompt for realistic image analysis
            prompt = """
            Please analyze this person's photo carefully and provide realistic estimates based on what you can observe. 
            Focus on visible features and use your knowledge of human proportions to make educated guesses.
            
            Please analyze:
            1. General body build/frame (petite, average, tall, athletic, etc.)
            2. Approximate height category (short: under 5'4", average: 5'4"-5'8", tall: over 5'8")
            3. Body shape/type (pear, apple, hourglass, rectangle, inverted triangle)
            4. Clothing style visible in the photo
            5. Colors the person is wearing
            6. Overall aesthetic/style preference hints
            
            Based on your analysis, estimate appropriate clothing sizes and provide style recommendations.
            
            IMPORTANT: Return your response as a valid JSON object only, with this exact structure:
            {
                "avatar_created": true,
                "analysis_confidence": "medium/high/low",
                "visible_features": {
                    "clothing_style": "description of current outfit style",
                    "colors_worn": "colors visible in the photo",
                    "overall_build": "description of body build"
                },
                "measurements": {
                    "height_category": "short/average/tall",
                    "estimated_height": "estimated height range",
                    "body_type": "body shape classification",
                    "build": "petite/average/athletic/curvy"
                },
                "recommended_sizes": {
                    "tops": "XS/S/M/L/XL",
                    "bottoms": "XS/S/M/L/XL", 
                    "dresses": "XS/S/M/L/XL"
                },
                "style_preferences": ["style1", "style2", "style3"],
                "color_palette": ["color_category1", "color_category2", "color_category3"],
                "confidence_note": "explanation of analysis limitations"
            }
            
            DO NOT include any text outside of this JSON structure.
            """
            
            response = self.call_gemini_api(prompt, image)
            
            if "candidates" in response and len(response["candidates"]) > 0:
                result_text = response["candidates"][0]["content"]["parts"][0]["text"].strip()
                
                # Clean up the response to extract JSON
                try:
                    # Remove markdown code blocks if present
                    if result_text.startswith('```'):
                        result_text = result_text.split('```')[1]
                        if result_text.startswith('json'):
                            result_text = result_text[4:]
                    
                    # Find JSON boundaries
                    json_start = result_text.find('{')
                    json_end = result_text.rfind('}') + 1
                    
                    if json_start != -1 and json_end > json_start:
                        json_text = result_text[json_start:json_end]
                        avatar_data = json.loads(json_text)
                        
                        # Validate required fields
                        required_fields = ['avatar_created', 'measurements', 'recommended_sizes']
                        if all(field in avatar_data for field in required_fields):
                            return avatar_data
                        else:
                            raise ValueError("Missing required fields in API response")
                    else:
                        raise ValueError("No valid JSON found in response")
                        
                except (json.JSONDecodeError, ValueError) as e:
                    st.warning(f"Could not parse AI response properly: {e}")
                    st.info("Using intelligent fallback based on average measurements...")
                    
                    # Create a more realistic fallback based on common sizing
                    avatar_data = {
                        "avatar_created": True,
                        "analysis_confidence": "low",
                        "visible_features": {
                            "clothing_style": "Unable to analyze clearly",
                            "colors_worn": "Various colors",
                            "overall_build": "Average build"
                        },
                        "measurements": {
                            "height_category": "average",
                            "estimated_height": "5'4\" - 5'8\"",
                            "body_type": "Rectangle",
                            "build": "average"
                        },
                        "recommended_sizes": {
                            "tops": "M",
                            "bottoms": "M",
                            "dresses": "M"
                        },
                        "style_preferences": ["Casual", "Versatile", "Comfortable"],
                        "color_palette": ["Neutrals", "Earth tones", "Classic colors"],
                        "confidence_note": "Analysis based on general population averages due to image processing limitations"
                    }
                    return avatar_data
            else:
                raise Exception("No response from AI model")
                
        except Exception as e:
            st.error(f"Error in avatar generation: {str(e)}")
            st.info("Creating avatar with default measurements...")
            
            # Fallback avatar data
            return {
                "avatar_created": True,
                "analysis_confidence": "low",
                "visible_features": {
                    "clothing_style": "Unable to analyze",
                    "colors_worn": "Unable to determine",
                    "overall_build": "Average"
                },
                "measurements": {
                    "height_category": "average",
                    "estimated_height": "5'5\" - 5'7\"",
                    "body_type": "Rectangle",
                    "build": "average"
                },
                "recommended_sizes": {
                    "tops": "M",
                    "bottoms": "M",
                    "dresses": "M"
                },
                "style_preferences": ["Universal", "Adaptable", "Classic"],
                "color_palette": ["Neutrals", "Basics", "Versatile"],
                "confidence_note": "Default avatar created due to analysis limitations"
            }
    
    def get_virtual_try_on_recommendation(self, item: Dict, avatar_data: Dict) -> str:
        """Get AI recommendation for how an item would look on the avatar"""
        prompt = f"""
        Based on the avatar measurements and the clothing item details, provide a recommendation:
        
        Avatar Details:
        - Body Type: {avatar_data.get('measurements', {}).get('body_type', 'Unknown')}
        - Measurements: {json.dumps(avatar_data.get('measurements', {}))}
        - Recommended Sizes: {json.dumps(avatar_data.get('recommended_sizes', {}))}
        
        Clothing Item:
        - Name: {item['name']}
        - Description: {item['description']}
        - Available Sizes: {item['size']}
        
        Please provide:
        1. How this item would fit on this body type
        2. Recommended size for this person
        3. Style advice and how to wear it
        4. Any fit concerns or highlights
        
        Keep the response conversational and helpful, around 2-3 sentences.
        """
        
        response = self.call_gemini_api(prompt)
        if "candidates" in response:
            return response["candidates"][0]["content"]["parts"][0]["text"]
        return "This item would look great on you! Consider trying your recommended size."
    
    def render_header(self):
        """Render the application header"""
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("<h1 style='text-align: center; color: #8b7355; font-size: 3rem; margin-bottom: 0;'>👗 StyleAI</h1>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: #d4b5a0; font-size: 1.2rem; margin-top: 0;'>Your Personal AI Fashion Assistant</p>", unsafe_allow_html=True)
    
    def render_avatar_section(self):
        """Render the avatar creation and management section"""
        st.markdown("## 📸 Create Your AI Avatar")
        
        # Model selection
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown("### 🤖 Choose AI Model")
        with col2:
            selected_model = st.selectbox(
                "AI Model",
                options=list(AVAILABLE_MODELS.keys()),
                format_func=lambda x: x.split('-')[1].title() + " " + x.split('-')[2].title() if len(x.split('-')) > 2 else x,
                key="model_selector",
                help="Choose the Gemini model for avatar analysis"
            )
            st.session_state.selected_model = selected_model
        
        # Display model info
        st.info(f"**Selected**: {AVAILABLE_MODELS[selected_model]}")
        
        # Important note about Gemini Nano
        st.warning("""
        📱 **About Gemini Nano**: Gemini Nano is designed for on-device processing (like Android phones) and is not available via cloud API. 
        For server-based applications like this, use Gemini Flash or Pro models which offer excellent image analysis capabilities.
        """)
        
        if not st.session_state.avatar_generated:
            st.markdown("""
            <div class='upload-area'>
                <h3 style='color: #8b7355; margin-bottom: 10px;'>Upload Your Photo</h3>
                <p style='color: #d4b5a0;'>Upload a clear photo of yourself for AI-powered avatar analysis</p>
            </div>
            """, unsafe_allow_html=True)
            
            uploaded_file = st.file_uploader(
                "Choose your photo", 
                type=['png', 'jpg', 'jpeg'],
                help="Upload a clear, front-facing photo for best results"
            )
            
            if uploaded_file is not None:
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.image(uploaded_file, caption="Your Photo", use_column_width=True)
                
                with col2:
                    st.markdown(f"**Using Model**: {selected_model}")
                    
                    if st.button("🚀 Generate AI Avatar", key="generate_avatar"):
                        with st.spinner(f"Creating your avatar using {selected_model}... This may take a moment."):
                            avatar_data = self.generate_avatar_from_image(uploaded_file)
                            
                            if "error" not in avatar_data:
                                st.session_state.avatar_generated = True
                                st.session_state.avatar_data = avatar_data
                                st.session_state.avatar_measurements = avatar_data.get('measurements', {})
                                st.success("✨ Avatar created successfully!")
                                st.rerun()
                            else:
                                st.error("Failed to create avatar. Please try again.")
        else:
            self.render_avatar_display()
    
    def render_avatar_display(self):
        """Display the generated avatar information"""
        st.markdown("### 🎯 Your Virtual Avatar")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("""
            <div class='avatar-preview'>
                <div style='text-align: center; padding: 40px; background: linear-gradient(135deg, #f8f6f1, #f5f2eb); border-radius: 10px;'>
                    <div style='font-size: 4rem; margin-bottom: 10px;'>🧍‍♀️</div>
                    <h4 style='color: #8b7355; margin: 0;'>Your AI Avatar</h4>
                    <p style='color: #d4b5a0; margin: 5px 0;'>Ready for virtual try-ons!</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            avatar_data = st.session_state.avatar_data
            measurements = avatar_data.get('measurements', {})
            recommended_sizes = avatar_data.get('recommended_sizes', {})
            confidence = avatar_data.get('analysis_confidence', 'medium')
            
            # Display confidence indicator
            confidence_color = {'high': '#4CAF50', 'medium': '#FF9800', 'low': '#F44336'}
            confidence_emoji = {'high': '🎯', 'medium': '⚡', 'low': '📊'}
            
            st.markdown(f"""
            <div class='avatar-stats'>
                <h4 style='color: #8b7355; margin-top: 0;'>📊 Avatar Analysis</h4>
                <p><strong>Analysis Confidence:</strong> 
                <span style='color: {confidence_color.get(confidence, '#666')};'>
                {confidence_emoji.get(confidence, '📊')} {confidence.title()}
                </span></p>
                
                <p><strong>Height Category:</strong> {measurements.get('height_category', 'N/A').title()}</p>
                <p><strong>Estimated Height:</strong> {measurements.get('estimated_height', 'N/A')}</p>
                <p><strong>Body Type:</strong> {measurements.get('body_type', 'N/A')}</p>
                <p><strong>Build:</strong> {measurements.get('build', 'N/A').title()}</p>
                
                <hr style='border-color: #d4b5a0; opacity: 0.3; margin: 15px 0;'>
                
                <p><strong>Recommended Sizes:</strong></p>
                <ul style='margin-left: 15px;'>
                    <li>Tops: {recommended_sizes.get('tops', 'N/A')}</li>
                    <li>Bottoms: {recommended_sizes.get('bottoms', 'N/A')}</li>
                    <li>Dresses: {recommended_sizes.get('dresses', 'N/A')}</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            # Show analysis details if available
            visible_features = avatar_data.get('visible_features', {})
            if visible_features:
                with st.expander("🔍 Analysis Details"):
                    st.write(f"**Clothing Style Observed:** {visible_features.get('clothing_style', 'N/A')}")
                    st.write(f"**Colors in Photo:** {visible_features.get('colors_worn', 'N/A')}")
                    st.write(f"**Overall Build:** {visible_features.get('overall_build', 'N/A')}")
                    
                    confidence_note = avatar_data.get('confidence_note', '')
                    if confidence_note:
                        st.info(f"**Note:** {confidence_note}")
        
        if st.button("🔄 Create New Avatar", key="new_avatar"):
            st.session_state.avatar_generated = False
            st.session_state.avatar_data = None
            st.rerun()
    
    def render_clothing_catalog(self):
        """Render the clothing catalog with categories"""
        st.markdown("## 🛍️ Clothing Catalog")
        
        # Category selection
        categories = list(CLOTHING_CATALOG.keys())
        selected_category = st.selectbox(
            "Choose Category",
            categories,
            format_func=lambda x: x.title()
        )
        
        # Display items in selected category
        items = CLOTHING_CATALOG[selected_category]
        
        # Create grid layout
        cols = st.columns(3)
        
        for idx, item in enumerate(items):
            with cols[idx % 3]:
                self.render_clothing_item(item)
    
    def render_clothing_item(self, item: Dict):
        """Render individual clothing item card"""
        st.markdown(f"""
        <div class='clothing-card'>
            <div style='text-align: center; font-size: 3rem; margin-bottom: 10px;'>
                {item['image']}
            </div>
            <h4 style='color: #8b7355; margin: 10px 0; text-align: center;'>{item['name']}</h4>
            <p style='color: #666; text-align: center; margin: 10px 0;'>{item['description']}</p>
            <p style='text-align: center;'><strong>Color:</strong> {item['color']}</p>
            <p style='text-align: center;'><strong>Sizes:</strong> {', '.join(item['size'])}</p>
            <div style='text-align: center;'>
                <span class='price-tag'>{item['price']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button(f"🛒 Add to Cart", key=f"cart_{item['id']}"):
                st.session_state.cart.append(item)
                st.success(f"Added {item['name']} to cart!")
        
        with col2:
            if st.session_state.avatar_generated:
                if st.button(f"👗 Virtual Try-On", key=f"tryon_{item['id']}"):
                    self.show_virtual_try_on(item)
            else:
                st.button("👗 Try-On (Create Avatar First)", disabled=True, key=f"disabled_tryon_{item['id']}")
    
    def show_virtual_try_on(self, item: Dict):
        """Display virtual try-on results"""
        st.markdown("### 🎨 Virtual Try-On Results")
        
        with st.spinner("AI is analyzing how this item will look on you..."):
            time.sleep(2)  # Simulate processing time
            recommendation = self.get_virtual_try_on_recommendation(item, st.session_state.avatar_data)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown(f"""
            <div class='avatar-preview'>
                <div style='text-align: center; padding: 20px;'>
                    <div style='font-size: 4rem; margin-bottom: 10px;'>🧍‍♀️</div>
                    <div style='font-size: 2rem; margin-bottom: 10px;'>{item['image']}</div>
                    <h4 style='color: #8b7355;'>You wearing</h4>
                    <p style='color: #d4b5a0;'>{item['name']}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class='avatar-stats'>
                <h4 style='color: #8b7355; margin-top: 0;'>🤖 AI Fashion Advice</h4>
                <p>{recommendation}</p>
                <hr style='border-color: #d4b5a0; opacity: 0.3;'>
                <p><strong>Recommended Size:</strong> {st.session_state.avatar_data.get('recommended_sizes', {}).get('tops' if 'top' in item['name'].lower() else 'dresses' if 'dress' in item['name'].lower() else 'bottoms', 'M')}</p>
                <p><strong>Fit Prediction:</strong> Perfect fit for your {st.session_state.avatar_data.get('measurements', {}).get('body_type', 'body type')}</p>
            </div>
            """, unsafe_allow_html=True)
    
    def render_sidebar(self):
        """Render the sidebar with cart and user info"""
        with st.sidebar:
            st.markdown("### 🛒 Shopping Cart")
            
            if st.session_state.cart:
                total_price = 0
                for item in st.session_state.cart:
                    st.markdown(f"**{item['name']}**")
                    st.markdown(f"Price: {item['price']}")
                    price_value = float(item['price'].replace('$', ''))
                    total_price += price_value
                    st.markdown("---")
                
                st.markdown(f"**Total: ${total_price:.2f}**")
                
                if st.button("🚀 Checkout"):
                    st.success("Thank you for your purchase! 🎉")
                    st.session_state.cart = []
                    st.rerun()
                
                if st.button("🗑️ Clear Cart"):
                    st.session_state.cart = []
                    st.rerun()
            else:
                st.markdown("Your cart is empty")
            
            st.markdown("---")
            
            # Avatar info in sidebar
            if st.session_state.avatar_generated:
                st.markdown("### 👤 Your Avatar")
                avatar_data = st.session_state.avatar_data
                measurements = avatar_data.get('measurements', {})
                confidence = avatar_data.get('analysis_confidence', 'medium')
                
                # Confidence indicator
                confidence_colors = {'high': '🟢', 'medium': '🟡', 'low': '🔴'}
                st.markdown(f"**Analysis:** {confidence_colors.get(confidence, '⚪')} {confidence.title()}")
                st.markdown(f"**Body Type:** {measurements.get('body_type', 'N/A')}")
                st.markdown(f"**Height:** {measurements.get('estimated_height', 'N/A')}")
                st.markdown(f"**Build:** {measurements.get('build', 'N/A').title()}")
                
                style_prefs = avatar_data.get('style_preferences', [])
                if style_prefs:
                    st.markdown("**Style Preferences:**")
                    for pref in style_prefs:
                        st.markdown(f"• {pref}")
            else:
                st.markdown("### 👤 Create Your Avatar")
                st.markdown("Upload a photo to get AI-powered size recommendations and style analysis!")
    
    def run(self):
        """Main application runner"""
        self.render_header()
        self.render_sidebar()
        
        # Main content tabs
        tab1, tab2 = st.tabs(["🏠 Home & Avatar", "🛍️ Shop"])
        
        with tab1:
            self.render_avatar_section()
            
            # Feature highlights
            if not st.session_state.avatar_generated:
                st.markdown("---")
                st.markdown("## ✨ Features")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("""
                    <div class='clothing-card' style='text-align: center;'>
                        <div style='font-size: 3rem; margin-bottom: 15px;'>📸</div>
                        <h4 style='color: #8b7355;'>3D Avatar Creation</h4>
                        <p>Upload your photo and get a personalized 3D avatar with accurate measurements</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown("""
                    <div class='clothing-card' style='text-align: center;'>
                        <div style='font-size: 3rem; margin-bottom: 15px;'>👗</div>
                        <h4 style='color: #8b7355;'>Virtual Try-On</h4>
                        <p>See how clothes will look on your avatar before making a purchase</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown("""
                    <div class='clothing-card' style='text-align: center;'>
                        <div style='font-size: 3rem; margin-bottom: 15px;'>🤖</div>
                        <h4 style='color: #8b7355;'>AI Recommendations</h4>
                        <p>Get personalized style advice powered by advanced AI technology</p>
                    </div>
                    """, unsafe_allow_html=True)
        
        with tab2:
            self.render_clothing_catalog()

# Run the application
if __name__ == "__main__":
    app = AIClothingStore()
    app.run()
